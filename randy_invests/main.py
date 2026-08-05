"""Main entry point for the Randy-Invests stock market predictor."""

from __future__ import annotations

import argparse
import sys

from randy_invests.data_fetcher import fetch_historical_data, fetch_realtime_quote
from randy_invests.predictor import StockPredictor
from randy_invests.recommender import generate_recommendation
from randy_invests.technical_analysis import add_indicators, identify_patterns


def analyse(ticker: str, period_days: int = 365, forward_days: int = 5) -> None:
    """Run the full analysis pipeline for a stock ticker and print results.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL').
        period_days: Days of historical data to use for training.
        forward_days: Prediction horizon in trading days.
    """
    print(f"\n{'='*60}")
    print(f"  Randy-Invests Stock Market Predictor: {ticker.upper()}")
    print(f"{'='*60}")

    # 1. Fetch data
    print(f"\n[1/4] Fetching historical data ({period_days} days)...")
    df = fetch_historical_data(ticker, period_days=period_days)
    print(f"      Loaded {len(df)} trading days.")

    print("\n[2/4] Fetching real-time quote...")
    quote = fetch_realtime_quote(ticker)
    print(f"      {ticker.upper()} @ ${quote['price']:.2f}  ({quote['change_pct']:+.2f}% today)")

    # 2. Technical analysis
    print("\n[3/4] Computing technical indicators and patterns...")
    df_ind = add_indicators(df)
    patterns = identify_patterns(df_ind)
    _print_patterns(patterns)

    # 3. Train predictor
    print("\n[4/4] Training ML models and generating prediction...")
    predictor = StockPredictor(forward_days=forward_days)
    metrics = predictor.train(df_ind)
    print(f"      Model accuracy — RF: {metrics['rf_accuracy']:.1%}  "
          f"GB: {metrics['gb_accuracy']:.1%}  "
          f"Ensemble: {metrics['ensemble_accuracy']:.1%}")

    prediction = predictor.predict(df_ind)

    # 4. Recommendation
    rec = generate_recommendation(
        ticker=ticker,
        quote=quote,
        prediction=prediction,
        patterns=patterns,
        training_metrics=metrics,
        forward_days=forward_days,
    )

    print(f"\n{rec}\n")


def _print_patterns(patterns: dict) -> None:
    """Print a compact summary of detected patterns."""
    labels = {
        "golden_cross":            "Golden Cross (SMA-20 > SMA-50)",
        "death_cross":             "Death Cross (SMA-20 < SMA-50)",
        "macd_bullish_crossover":  "MACD Bullish Crossover",
        "macd_bearish_crossover":  "MACD Bearish Crossover",
        "price_above_sma20":       "Above SMA-20",
        "price_above_sma50":       "Above SMA-50",
        "price_above_sma200":      "Above SMA-200",
        "rsi_overbought":          "RSI Overbought (>70)",
        "rsi_oversold":            "RSI Oversold (<30)",
        "stoch_overbought":        "Stochastic Overbought (>80)",
        "stoch_oversold":          "Stochastic Oversold (<20)",
        "williams_r_overbought":   "Williams %R Overbought (>-20)",
        "williams_r_oversold":     "Williams %R Oversold (<-80)",
        "cci_overbought":          "CCI Overbought (>100)",
        "cci_oversold":            "CCI Oversold (<-100)",
        "bollinger_squeeze":       "Bollinger Band Squeeze",
        "bb_above_upper":          "Price Above BB Upper Band",
        "bb_below_lower":          "Price Below BB Lower Band",
        "kc_above_upper":          "Price Above Keltner Upper Band",
        "kc_below_lower":          "Price Below Keltner Lower Band",
        "dc_breakout_up":          "Donchian Breakout Up (new 20-day high)",
        "dc_breakout_down":        "Donchian Breakout Down (new 20-day low)",
        "strong_trend":            "Strong Trend (ADX > 25)",
        "weak_trend":              "Weak Trend (ADX < 20)",
        "adx_bullish":             "ADX Bullish (+DI > -DI)",
        "vortex_bullish":          "Vortex Bullish (VI+ > VI-)",
        "psar_bullish":            "Parabolic SAR Bullish",
        "psar_bearish":            "Parabolic SAR Bearish",
        "aroon_bullish":           "Aroon Bullish",
        "aroon_bearish":           "Aroon Bearish",
        "mfi_overbought":          "MFI Overbought (>80)",
        "mfi_oversold":            "MFI Oversold (<20)",
    }
    active = [label for key, label in labels.items() if patterns.get(key)]
    trend = patterns.get("recent_trend", "neutral")
    print(f"      Recent trend: {trend.upper()}")
    if active:
        for label in active:
            print(f"      ✓ {label}")
    else:
        print("      No strong pattern signals detected.")


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="randy-invests",
        description="Randy-Invests: ML-powered stock market predictor with buy/sell recommendations.",
    )
    parser.add_argument(
        "tickers",
        nargs="+",
        metavar="TICKER",
        help="One or more stock ticker symbols to analyse (e.g. AAPL MSFT TSLA).",
    )
    parser.add_argument(
        "--period",
        type=int,
        default=365,
        metavar="DAYS",
        help="Days of historical data to use for training (default: 365).",
    )
    parser.add_argument(
        "--forward",
        type=int,
        default=5,
        metavar="DAYS",
        help="Prediction horizon in trading days (default: 5).",
    )

    args = parser.parse_args()

    errors = []
    for ticker in args.tickers:
        try:
            analyse(ticker, period_days=args.period, forward_days=args.forward)
        except Exception as exc:  # noqa: BLE001
            print(f"\n[ERROR] {ticker.upper()}: {exc}", file=sys.stderr)
            errors.append(ticker)

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
