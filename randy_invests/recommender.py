"""Recommendation engine: generate buy/sell/hold signals from predictions and patterns."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Recommendation:
    """A structured buy/sell/hold recommendation."""

    ticker: str
    signal: str  # 'BUY', 'SELL', 'HOLD'
    strength: str  # 'STRONG', 'MODERATE', 'WEAK'
    score: float  # composite score in [-1, 1]; positive → buy, negative → sell
    reasons: list[str] = field(default_factory=list)
    price: float = 0.0
    price_change_estimate_pct: float = 0.0
    forward_days: int = 5

    def __str__(self) -> str:
        lines = [
            f"=== {self.ticker} Recommendation ===",
            f"Signal   : {self.strength} {self.signal}",
            f"Score    : {self.score:+.3f} (range −1 sell → +1 buy)",
            f"Price    : ${self.price:.2f}",
            f"Est. change in {self.forward_days}d: {self.price_change_estimate_pct:+.2f}%",
            "Reasons  :",
        ]
        for reason in self.reasons:
            lines.append(f"  • {reason}")
        return "\n".join(lines)


def generate_recommendation(
    ticker: str,
    quote: dict,
    prediction: dict,
    patterns: dict,
    training_metrics: dict,
    forward_days: int = 5,
) -> Recommendation:
    """Synthesise a buy/sell/hold recommendation from all available signals.

    Scoring scheme (each component adds to a score in [-1, 1]):
        +0.35  ML ensemble prediction (UP) or −0.35 (DOWN), weighted by confidence
        +0.15  RSI oversold (buy) / −0.15 RSI overbought (sell)
        +0.15  MACD bullish crossover / −0.10 MACD bearish
        +0.10  Golden cross / −0.10 Death cross
        +0.10  Price above SMA20 & SMA50 / −0.10 below both
        +0.05  Recent bullish trend / −0.05 bearish trend
        +0.10  Positive real-time day change / −0.10 negative

    Args:
        ticker: Ticker symbol.
        quote: Output from data_fetcher.fetch_realtime_quote().
        prediction: Output from predictor.StockPredictor.predict().
        patterns: Output from technical_analysis.identify_patterns().
        training_metrics: Output from predictor.StockPredictor.train().
        forward_days: Prediction horizon.

    Returns:
        Recommendation dataclass.
    """
    score = 0.0
    reasons: list[str] = []

    # --- ML prediction signal ---
    conf_weight = {"HIGH": 1.0, "MEDIUM": 0.65, "LOW": 0.35}.get(prediction.get("confidence", "LOW"), 0.35)
    ml_contribution = 0.35 * conf_weight
    if prediction.get("predicted_direction") == "UP":
        score += ml_contribution
        reasons.append(
            f"ML ensemble predicts UP with {prediction['confidence']} confidence "
            f"(prob={prediction['direction_probability']:.2f})"
        )
    else:
        score -= ml_contribution
        reasons.append(
            f"ML ensemble predicts DOWN with {prediction['confidence']} confidence "
            f"(prob={1 - prediction['direction_probability']:.2f})"
        )

    # --- RSI ---
    if patterns.get("rsi_oversold"):
        score += 0.15
        reasons.append("RSI < 30: oversold — potential reversal upward")
    elif patterns.get("rsi_overbought"):
        score -= 0.15
        reasons.append("RSI > 70: overbought — potential reversal downward")

    # --- MACD ---
    if patterns.get("macd_bullish_crossover"):
        score += 0.15
        reasons.append("MACD bullish crossover detected")
    elif patterns.get("macd_bearish_crossover"):
        score -= 0.10
        reasons.append("MACD bearish crossover detected")

    # --- Moving average crosses ---
    if patterns.get("golden_cross"):
        score += 0.10
        reasons.append("Golden cross: SMA-20 crossed above SMA-50")
    elif patterns.get("death_cross"):
        score -= 0.10
        reasons.append("Death cross: SMA-20 crossed below SMA-50")

    # --- Price vs SMAs ---
    above_20 = patterns.get("price_above_sma20", False)
    above_50 = patterns.get("price_above_sma50", False)
    if above_20 and above_50:
        score += 0.10
        reasons.append("Price trading above both SMA-20 and SMA-50 (bullish)")
    elif not above_20 and not above_50:
        score -= 0.10
        reasons.append("Price trading below both SMA-20 and SMA-50 (bearish)")

    # --- Recent trend ---
    trend = patterns.get("recent_trend", "neutral")
    if trend == "bullish":
        score += 0.05
        reasons.append("Recent 20-day price trend is bullish")
    elif trend == "bearish":
        score -= 0.05
        reasons.append("Recent 20-day price trend is bearish")

    # --- Real-time day performance ---
    change_pct = quote.get("change_pct", 0.0)
    if change_pct > 0:
        score += min(0.10, change_pct / 100)
        reasons.append(f"Positive day change: {change_pct:+.2f}%")
    elif change_pct < 0:
        score -= min(0.10, abs(change_pct) / 100)
        reasons.append(f"Negative day change: {change_pct:+.2f}%")

    # --- Bollinger squeeze (neutral note) ---
    if patterns.get("bollinger_squeeze"):
        reasons.append("Bollinger Band squeeze detected — potential breakout imminent")
    if patterns.get("bb_above_upper"):
        score -= 0.05
        reasons.append("Price above Bollinger upper band — overbought territory")
    elif patterns.get("bb_below_lower"):
        score += 0.05
        reasons.append("Price below Bollinger lower band — oversold territory")

    # --- ADX (trend strength) ---
    if patterns.get("strong_trend"):
        if patterns.get("adx_bullish"):
            score += 0.05
            reasons.append("ADX > 25: strong bullish trend (+DI > -DI)")
        else:
            score -= 0.05
            reasons.append("ADX > 25: strong bearish trend (-DI > +DI)")

    # --- Vortex ---
    if patterns.get("vortex_bullish"):
        score += 0.04
        reasons.append("Vortex indicator bullish (VI+ > VI-)")
    elif not patterns.get("vortex_bullish"):
        score -= 0.02
        reasons.append("Vortex indicator bearish (VI- > VI+)")

    # --- PSAR ---
    if patterns.get("psar_bullish"):
        score += 0.04
        reasons.append("Parabolic SAR in uptrend")
    elif patterns.get("psar_bearish"):
        score -= 0.04
        reasons.append("Parabolic SAR in downtrend")

    # --- Stochastic ---
    if patterns.get("stoch_oversold"):
        score += 0.04
        reasons.append("Stochastic < 20: oversold")
    elif patterns.get("stoch_overbought"):
        score -= 0.04
        reasons.append("Stochastic > 80: overbought")

    # --- Williams %R ---
    if patterns.get("williams_r_oversold"):
        score += 0.04
        reasons.append("Williams %R < -80: oversold")
    elif patterns.get("williams_r_overbought"):
        score -= 0.04
        reasons.append("Williams %R > -20: overbought")

    # --- CCI ---
    if patterns.get("cci_oversold"):
        score += 0.03
        reasons.append("CCI < -100: oversold")
    elif patterns.get("cci_overbought"):
        score -= 0.03
        reasons.append("CCI > 100: overbought")

    # --- MFI ---
    if patterns.get("mfi_oversold"):
        score += 0.03
        reasons.append("MFI < 20: oversold (money flowing out, potential reversal)")
    elif patterns.get("mfi_overbought"):
        score -= 0.03
        reasons.append("MFI > 80: overbought (money flowing in strongly)")

    # --- Aroon ---
    if patterns.get("aroon_bullish"):
        score += 0.03
        reasons.append("Aroon Up > Aroon Down: bullish trend")
    elif patterns.get("aroon_bearish"):
        score -= 0.03
        reasons.append("Aroon Down > Aroon Up: bearish trend")

    # --- Donchian breakouts ---
    if patterns.get("dc_breakout_up"):
        score += 0.03
        reasons.append("Donchian channel upper breakout: new 20-day high")
    elif patterns.get("dc_breakout_down"):
        score -= 0.03
        reasons.append("Donchian channel lower breakout: new 20-day low")

    # Clamp score
    score = max(-1.0, min(1.0, score))

    # Determine signal
    if score >= 0.20:
        signal = "BUY"
        strength = "STRONG" if score >= 0.50 else "MODERATE"
    elif score <= -0.20:
        signal = "SELL"
        strength = "STRONG" if score <= -0.50 else "MODERATE"
    else:
        signal = "HOLD"
        strength = "WEAK"

    return Recommendation(
        ticker=ticker.upper(),
        signal=signal,
        strength=strength,
        score=round(score, 4),
        reasons=reasons,
        price=quote.get("price", 0.0),
        price_change_estimate_pct=prediction.get("price_change_estimate_pct", 0.0),
        forward_days=forward_days,
    )
