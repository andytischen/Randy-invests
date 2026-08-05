"""Technical analysis module: compute indicators and identify patterns."""

from __future__ import annotations

import pandas as pd
import ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add a comprehensive set of technical indicators to the OHLCV DataFrame.

    Adds:
        - RSI (14-period)
        - MACD line, signal, histogram
        - Bollinger Bands (upper, middle, lower)
        - SMA 20 and SMA 50
        - EMA 12 and EMA 26
        - ATR (14-period, volatility)
        - OBV (on-balance volume)
        - Stochastic %K and %D

    Args:
        df: DataFrame with at least Open, High, Low, Close, Volume columns.

    Returns:
        New DataFrame with all original columns plus indicator columns.
    """
    df = df.copy()
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    # Trend
    df["sma_20"] = ta.trend.sma_indicator(close, window=20)
    df["sma_50"] = ta.trend.sma_indicator(close, window=50)
    df["ema_12"] = ta.trend.ema_indicator(close, window=12)
    df["ema_26"] = ta.trend.ema_indicator(close, window=26)

    # MACD
    macd = ta.trend.MACD(close)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_diff"] = macd.macd_diff()

    # RSI
    df["rsi"] = ta.momentum.rsi(close, window=14)

    # Stochastic
    stoch = ta.momentum.StochasticOscillator(high, low, close)
    df["stoch_k"] = stoch.stoch()
    df["stoch_d"] = stoch.stoch_signal()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    df["bb_upper"] = bb.bollinger_hband()
    df["bb_middle"] = bb.bollinger_mavg()
    df["bb_lower"] = bb.bollinger_lband()
    df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

    # Volatility
    df["atr"] = ta.volatility.average_true_range(high, low, close, window=14)

    # Volume
    df["obv"] = ta.volume.on_balance_volume(close, volume)

    return df


def identify_patterns(df: pd.DataFrame) -> dict:
    """Identify simple candlestick/trend patterns from recent price history.

    Args:
        df: DataFrame with Close, sma_20, sma_50 columns (after add_indicators).

    Returns:
        Dictionary with boolean flags for detected patterns:
            golden_cross, death_cross, price_above_sma20, price_above_sma50,
            rsi_overbought, rsi_oversold, macd_bullish_crossover,
            bollinger_squeeze, recent_trend (str: 'bullish'/'bearish'/'neutral').
    """
    last = df.dropna().iloc[-1] if not df.dropna().empty else None
    if last is None:
        return {}

    patterns: dict = {}

    # Golden / Death cross (SMA 20 vs SMA 50)
    if len(df) >= 2:
        prev = df.dropna().iloc[-2]
        patterns["golden_cross"] = bool(prev["sma_20"] < prev["sma_50"] and last["sma_20"] >= last["sma_50"])
        patterns["death_cross"] = bool(prev["sma_20"] > prev["sma_50"] and last["sma_20"] <= last["sma_50"])
        patterns["macd_bullish_crossover"] = bool(
            prev["macd"] < prev["macd_signal"] and last["macd"] >= last["macd_signal"]
        )
    else:
        patterns["golden_cross"] = False
        patterns["death_cross"] = False
        patterns["macd_bullish_crossover"] = False

    patterns["price_above_sma20"] = bool(last["Close"] > last["sma_20"])
    patterns["price_above_sma50"] = bool(last["Close"] > last["sma_50"])
    patterns["rsi_overbought"] = bool(last["rsi"] > 70)
    patterns["rsi_oversold"] = bool(last["rsi"] < 30)
    patterns["bollinger_squeeze"] = bool(last["bb_width"] < df["bb_width"].quantile(0.2))

    # Determine recent trend from last 20 closes
    recent = df["Close"].dropna().tail(20)
    if len(recent) >= 2:
        slope = (recent.iloc[-1] - recent.iloc[0]) / len(recent)
        if slope > 0:
            patterns["recent_trend"] = "bullish"
        elif slope < 0:
            patterns["recent_trend"] = "bearish"
        else:
            patterns["recent_trend"] = "neutral"
    else:
        patterns["recent_trend"] = "neutral"

    return patterns
