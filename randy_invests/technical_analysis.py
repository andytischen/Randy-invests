"""Technical analysis module: compute indicators and identify patterns."""

from __future__ import annotations

import pandas as pd
import ta


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add ALL technical indicators from the ta library to the OHLCV DataFrame.

    Categories covered:
        Trend:
            SMA 20/50/200, EMA 12/26/50, WMA 20, MACD, ADX (+DI/-DI),
            Aroon Up/Down, CCI, DPO, Ichimoku (conversion/base/a/b),
            KST + signal, Mass Index, PSAR (up/down), STC, TRIX,
            Vortex (+/-).
        Momentum:
            RSI, Stochastic %K/%D, StochRSI %K/%D, Williams %R,
            Ultimate Oscillator, ROC, TSI, KAMA,
            Awesome Oscillator, PPO + signal + hist,
            PVO + signal + hist.
        Volatility:
            ATR, Bollinger Bands (upper/middle/lower/width/pband),
            Donchian Channel (high/mid/low/width/pband),
            Keltner Channel (upper/mid/lower/width/pband),
            Ulcer Index.
        Volume:
            OBV, Acc/Dist Index, Chaikin Money Flow,
            Ease of Movement (raw + SMA), Force Index,
            MFI (Money Flow Index), NVI,
            Volume Price Trend, VWAP.
        Others:
            Daily Return, Daily Log Return, Cumulative Return.

    Args:
        df: DataFrame with at least Open, High, Low, Close, Volume columns.

    Returns:
        New DataFrame with all original columns plus indicator columns.
        Indicators that cannot be computed (e.g. insufficient data) are
        silently skipped rather than raising an exception.
    """
    df = df.copy()
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]
    open_ = df["Open"]

    def _safe(fn, *args, **kwargs):
        """Call fn(*args, **kwargs); return None Series on any error."""
        try:
            return fn(*args, **kwargs)
        except Exception:
            return None

    def _add(col: str, series) -> None:
        if series is not None:
            df[col] = series

    # ── Trend ─────────────────────────────────────────────────────────────────
    _add("sma_20",  _safe(ta.trend.sma_indicator, close, window=20))
    _add("sma_50",  _safe(ta.trend.sma_indicator, close, window=50))
    _add("sma_200", _safe(ta.trend.sma_indicator, close, window=200))
    _add("ema_12",  _safe(ta.trend.ema_indicator, close, window=12))
    _add("ema_26",  _safe(ta.trend.ema_indicator, close, window=26))
    _add("ema_50",  _safe(ta.trend.ema_indicator, close, window=50))
    _add("wma_20",  _safe(ta.trend.wma_indicator, close, window=20))

    macd = ta.trend.MACD(close)
    _add("macd",        _safe(macd.macd))
    _add("macd_signal", _safe(macd.macd_signal))
    _add("macd_diff",   _safe(macd.macd_diff))

    adx_ind = ta.trend.ADXIndicator(high, low, close)
    _add("adx",     _safe(adx_ind.adx))
    _add("adx_pos", _safe(adx_ind.adx_pos))
    _add("adx_neg", _safe(adx_ind.adx_neg))

    aroon = ta.trend.AroonIndicator(high, low)
    _add("aroon_up",   _safe(aroon.aroon_up))
    _add("aroon_down", _safe(aroon.aroon_down))

    _add("cci",          _safe(ta.trend.cci, high, low, close))
    _add("dpo",          _safe(ta.trend.dpo, close))
    _add("mass_index",   _safe(ta.trend.mass_index, high, low))
    _add("trix",         _safe(ta.trend.trix, close))
    _add("kst",          _safe(ta.trend.kst, close))
    _add("kst_signal",   _safe(ta.trend.kst_sig, close))
    _add("stc",          _safe(ta.trend.stc, close))

    ichimoku = ta.trend.IchimokuIndicator(high, low)
    _add("ichimoku_conv",  _safe(ichimoku.ichimoku_conversion_line))
    _add("ichimoku_base",  _safe(ichimoku.ichimoku_base_line))
    _add("ichimoku_a",     _safe(ichimoku.ichimoku_a))
    _add("ichimoku_b",     _safe(ichimoku.ichimoku_b))

    psar = ta.trend.PSARIndicator(high, low, close)
    _add("psar_up",   _safe(psar.psar_up))
    _add("psar_down", _safe(psar.psar_down))
    _add("psar_up_indicator",   _safe(psar.psar_up_indicator))
    _add("psar_down_indicator", _safe(psar.psar_down_indicator))

    vortex = ta.trend.VortexIndicator(high, low, close)
    _add("vortex_pos", _safe(vortex.vortex_indicator_pos))
    _add("vortex_neg", _safe(vortex.vortex_indicator_neg))

    # ── Momentum ──────────────────────────────────────────────────────────────
    _add("rsi",  _safe(ta.momentum.rsi, close, window=14))
    _add("roc",  _safe(ta.momentum.roc, close))
    _add("tsi",  _safe(ta.momentum.tsi, close))
    _add("kama", _safe(ta.momentum.kama, close))
    _add("williams_r",        _safe(ta.momentum.williams_r, high, low, close))
    _add("ultimate_oscillator", _safe(ta.momentum.ultimate_oscillator, high, low, close))
    _add("awesome_oscillator",  _safe(ta.momentum.awesome_oscillator, high, low))

    stoch = ta.momentum.StochasticOscillator(high, low, close)
    _add("stoch_k", _safe(stoch.stoch))
    _add("stoch_d", _safe(stoch.stoch_signal))

    stochrsi = ta.momentum.StochRSIIndicator(close)
    _add("stochrsi",   _safe(stochrsi.stochrsi))
    _add("stochrsi_k", _safe(stochrsi.stochrsi_k))
    _add("stochrsi_d", _safe(stochrsi.stochrsi_d))

    ppo = ta.momentum.PercentagePriceOscillator(close)
    _add("ppo",        _safe(ppo.ppo))
    _add("ppo_signal", _safe(ppo.ppo_signal))
    _add("ppo_hist",   _safe(ppo.ppo_hist))

    pvo = ta.momentum.PercentageVolumeOscillator(volume)
    _add("pvo",        _safe(pvo.pvo))
    _add("pvo_signal", _safe(pvo.pvo_signal))
    _add("pvo_hist",   _safe(pvo.pvo_hist))

    # ── Volatility ────────────────────────────────────────────────────────────
    _add("atr",         _safe(ta.volatility.average_true_range, high, low, close, window=14))
    _add("ulcer_index", _safe(ta.volatility.ulcer_index, close))

    bb = ta.volatility.BollingerBands(close, window=20, window_dev=2)
    _add("bb_upper",  _safe(bb.bollinger_hband))
    _add("bb_middle", _safe(bb.bollinger_mavg))
    _add("bb_lower",  _safe(bb.bollinger_lband))
    _add("bb_pband",  _safe(bb.bollinger_pband))
    _add("bb_width",  _safe(bb.bollinger_wband))

    dc = ta.volatility.DonchianChannel(high, low, close)
    _add("dc_upper", _safe(dc.donchian_channel_hband))
    _add("dc_mid",   _safe(dc.donchian_channel_mband))
    _add("dc_lower", _safe(dc.donchian_channel_lband))
    _add("dc_pband", _safe(dc.donchian_channel_pband))
    _add("dc_width", _safe(dc.donchian_channel_wband))

    kc = ta.volatility.KeltnerChannel(high, low, close)
    _add("kc_upper", _safe(kc.keltner_channel_hband))
    _add("kc_mid",   _safe(kc.keltner_channel_mband))
    _add("kc_lower", _safe(kc.keltner_channel_lband))
    _add("kc_pband", _safe(kc.keltner_channel_pband))
    _add("kc_width", _safe(kc.keltner_channel_wband))

    # ── Volume ────────────────────────────────────────────────────────────────
    _add("obv",             _safe(ta.volume.on_balance_volume, close, volume))
    _add("acc_dist_index",  _safe(ta.volume.acc_dist_index, high, low, close, volume))
    _add("chaikin_mf",      _safe(ta.volume.chaikin_money_flow, high, low, close, volume))
    _add("ease_of_movement",_safe(ta.volume.ease_of_movement, high, low, volume))
    _add("sma_ease_of_movement", _safe(ta.volume.sma_ease_of_movement, high, low, volume))
    _add("force_index",     _safe(ta.volume.force_index, close, volume))
    _add("mfi",             _safe(ta.volume.money_flow_index, high, low, close, volume))
    _add("nvi",             _safe(ta.volume.negative_volume_index, close, volume))
    _add("vpt",             _safe(ta.volume.volume_price_trend, close, volume))
    _add("vwap",            _safe(ta.volume.volume_weighted_average_price, high, low, close, volume))

    # ── Others (returns) ──────────────────────────────────────────────────────
    _add("daily_return",     _safe(ta.others.daily_return, close))
    _add("daily_log_return", _safe(ta.others.daily_log_return, close))
    _add("cumulative_return",_safe(ta.others.cumulative_return, close))

    # Derived convenience columns (always safe)
    if "bb_upper" in df.columns and "bb_lower" in df.columns and "bb_middle" in df.columns:
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"].replace(0, float("nan"))

    return df


def identify_patterns(df: pd.DataFrame) -> dict:
    """Identify candlestick/trend patterns from recent price history.

    Uses all available indicators (added by add_indicators) to detect a
    comprehensive set of patterns and signals.

    Args:
        df: DataFrame with Close and indicator columns (after add_indicators).

    Returns:
        Dictionary with boolean flags and string values for detected patterns.
    """
    clean = df.dropna(how="all")
    if clean.empty:
        return {}

    last = clean.iloc[-1]
    patterns: dict = {}

    def _col(name: str):
        """Return last value of column or None if absent/NaN."""
        if name in df.columns:
            val = df[name].dropna()
            return float(val.iloc[-1]) if not val.empty else None
        return None

    def _prev_col(name: str):
        """Return second-to-last value of column or None."""
        if name in df.columns:
            val = df[name].dropna()
            return float(val.iloc[-2]) if len(val) >= 2 else None
        return None

    # ── Moving average crosses ────────────────────────────────────────────────
    sma20, sma50 = _col("sma_20"), _col("sma_50")
    prev_sma20, prev_sma50 = _prev_col("sma_20"), _prev_col("sma_50")
    if None not in (sma20, sma50, prev_sma20, prev_sma50):
        patterns["golden_cross"] = bool(prev_sma20 < prev_sma50 and sma20 >= sma50)
        patterns["death_cross"]  = bool(prev_sma20 > prev_sma50 and sma20 <= sma50)
    else:
        patterns["golden_cross"] = False
        patterns["death_cross"]  = False

    close = _col("Close")
    patterns["price_above_sma20"]  = bool(close is not None and sma20  is not None and close > sma20)
    patterns["price_above_sma50"]  = bool(close is not None and sma50  is not None and close > sma50)
    sma200 = _col("sma_200")
    patterns["price_above_sma200"] = bool(close is not None and sma200 is not None and close > sma200)

    # ── MACD ─────────────────────────────────────────────────────────────────
    macd, macd_sig = _col("macd"), _col("macd_signal")
    prev_macd, prev_macd_sig = _prev_col("macd"), _prev_col("macd_signal")
    if None not in (macd, macd_sig, prev_macd, prev_macd_sig):
        patterns["macd_bullish_crossover"] = bool(prev_macd < prev_macd_sig and macd >= macd_sig)
        patterns["macd_bearish_crossover"] = bool(prev_macd > prev_macd_sig and macd <= macd_sig)
    else:
        patterns["macd_bullish_crossover"] = False
        patterns["macd_bearish_crossover"] = False

    # ── RSI ──────────────────────────────────────────────────────────────────
    rsi = _col("rsi")
    patterns["rsi_overbought"] = bool(rsi is not None and rsi > 70)
    patterns["rsi_oversold"]   = bool(rsi is not None and rsi < 30)

    # ── Stochastic ───────────────────────────────────────────────────────────
    stoch_k = _col("stoch_k")
    patterns["stoch_overbought"] = bool(stoch_k is not None and stoch_k > 80)
    patterns["stoch_oversold"]   = bool(stoch_k is not None and stoch_k < 20)

    # ── Williams %R ──────────────────────────────────────────────────────────
    wr = _col("williams_r")
    patterns["williams_r_overbought"] = bool(wr is not None and wr > -20)
    patterns["williams_r_oversold"]   = bool(wr is not None and wr < -80)

    # ── CCI ──────────────────────────────────────────────────────────────────
    cci = _col("cci")
    patterns["cci_overbought"] = bool(cci is not None and cci > 100)
    patterns["cci_oversold"]   = bool(cci is not None and cci < -100)

    # ── ADX (trend strength) ─────────────────────────────────────────────────
    adx = _col("adx")
    patterns["strong_trend"] = bool(adx is not None and adx > 25)
    patterns["weak_trend"]   = bool(adx is not None and adx < 20)
    adx_pos, adx_neg = _col("adx_pos"), _col("adx_neg")
    patterns["adx_bullish"] = bool(None not in (adx_pos, adx_neg) and adx_pos > adx_neg)

    # ── Vortex ───────────────────────────────────────────────────────────────
    vp, vn = _col("vortex_pos"), _col("vortex_neg")
    patterns["vortex_bullish"] = bool(None not in (vp, vn) and vp > vn)

    # ── Bollinger Bands ──────────────────────────────────────────────────────
    bb_width = _col("bb_width")
    if bb_width is not None and "bb_width" in df.columns:
        patterns["bollinger_squeeze"] = bool(bb_width < df["bb_width"].quantile(0.2))
    else:
        patterns["bollinger_squeeze"] = False
    bb_pband = _col("bb_pband")
    patterns["bb_above_upper"] = bool(bb_pband is not None and bb_pband > 1)
    patterns["bb_below_lower"] = bool(bb_pband is not None and bb_pband < 0)

    # ── Keltner Channel ───────────────────────────────────────────────────────
    kc_upper, kc_lower = _col("kc_upper"), _col("kc_lower")
    patterns["kc_above_upper"] = bool(None not in (close, kc_upper) and close > kc_upper)
    patterns["kc_below_lower"] = bool(None not in (close, kc_lower) and close < kc_lower)

    # ── Donchian Channel ─────────────────────────────────────────────────────
    dc_upper, dc_lower = _col("dc_upper"), _col("dc_lower")
    patterns["dc_breakout_up"]   = bool(None not in (close, dc_upper) and close >= dc_upper)
    patterns["dc_breakout_down"] = bool(None not in (close, dc_lower) and close <= dc_lower)

    # ── MFI (Money Flow Index) ───────────────────────────────────────────────
    mfi = _col("mfi")
    patterns["mfi_overbought"] = bool(mfi is not None and mfi > 80)
    patterns["mfi_oversold"]   = bool(mfi is not None and mfi < 20)

    # ── PSAR ─────────────────────────────────────────────────────────────────
    psar_up_ind   = _col("psar_up_indicator")
    psar_down_ind = _col("psar_down_indicator")
    patterns["psar_bullish"] = bool(psar_up_ind is not None and psar_up_ind == 1)
    patterns["psar_bearish"] = bool(psar_down_ind is not None and psar_down_ind == 1)

    # ── Aroon ────────────────────────────────────────────────────────────────
    aroon_up, aroon_down = _col("aroon_up"), _col("aroon_down")
    patterns["aroon_bullish"] = bool(None not in (aroon_up, aroon_down) and aroon_up > aroon_down)
    patterns["aroon_bearish"] = bool(None not in (aroon_up, aroon_down) and aroon_down > aroon_up)

    # ── Recent trend (20-day slope) ───────────────────────────────────────────
    recent = df["Close"].dropna().tail(20)
    if len(recent) >= 2:
        slope = (recent.iloc[-1] - recent.iloc[0]) / len(recent)
        patterns["recent_trend"] = "bullish" if slope > 0 else ("bearish" if slope < 0 else "neutral")
    else:
        patterns["recent_trend"] = "neutral"

    return patterns

