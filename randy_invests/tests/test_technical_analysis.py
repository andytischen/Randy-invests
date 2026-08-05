"""Unit tests for technical_analysis module."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from randy_invests.technical_analysis import add_indicators, identify_patterns


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ohlcv(n: int = 300, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    prices = 100 + np.cumsum(rng.normal(0, 1, n))
    prices = np.maximum(prices, 10)
    idx = pd.date_range("2023-01-01", periods=n, freq="B")
    df = pd.DataFrame(
        {
            "Open": prices * (1 + rng.uniform(-0.005, 0.005, n)),
            "High": prices * (1 + rng.uniform(0, 0.01, n)),
            "Low": prices * (1 - rng.uniform(0, 0.01, n)),
            "Close": prices,
            "Volume": rng.integers(1_000_000, 10_000_000, n),
        },
        index=idx,
    )
    df.index.name = "Date"
    return df


# ---------------------------------------------------------------------------
# add_indicators
# ---------------------------------------------------------------------------


class TestAddIndicators:
    def test_returns_dataframe(self):
        df = _make_ohlcv()
        result = add_indicators(df)
        assert isinstance(result, pd.DataFrame)

    def test_indicator_columns_present(self):
        df = _make_ohlcv()
        result = add_indicators(df)
        expected_cols = [
            "sma_20", "sma_50", "sma_200", "ema_12", "ema_26", "ema_50", "wma_20",
            "macd", "macd_signal", "macd_diff",
            "adx", "adx_pos", "adx_neg",
            "aroon_up", "aroon_down",
            "cci", "trix", "kst", "vortex_pos", "vortex_neg",
            "psar_up_indicator", "psar_down_indicator",
            "ichimoku_conv", "ichimoku_base",
            "rsi", "roc", "williams_r", "ultimate_oscillator", "awesome_oscillator",
            "stoch_k", "stoch_d", "stochrsi_k", "stochrsi_d",
            "ppo", "pvo",
            "atr", "bb_upper", "bb_middle", "bb_lower", "bb_width", "bb_pband",
            "dc_upper", "dc_lower", "dc_width",
            "kc_upper", "kc_lower", "kc_width",
            "obv", "chaikin_mf", "mfi", "vpt", "force_index",
            "daily_return", "daily_log_return", "cumulative_return",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_does_not_modify_original(self):
        df = _make_ohlcv()
        original_cols = list(df.columns)
        add_indicators(df)
        assert list(df.columns) == original_cols

    def test_short_dataframe_does_not_raise(self):
        """add_indicators should silently skip indicators that need more data."""
        df = _make_ohlcv(n=10)
        result = add_indicators(df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10


# ---------------------------------------------------------------------------
# identify_patterns
# ---------------------------------------------------------------------------


class TestIdentifyPatterns:
    def test_returns_dict(self):
        df = _make_ohlcv()
        df_ind = add_indicators(df)
        result = identify_patterns(df_ind)
        assert isinstance(result, dict)

    def test_contains_expected_keys(self):
        df = _make_ohlcv()
        df_ind = add_indicators(df)
        result = identify_patterns(df_ind)
        for key in [
            "golden_cross", "death_cross", "rsi_overbought", "rsi_oversold",
            "price_above_sma20", "price_above_sma50", "price_above_sma200",
            "recent_trend", "strong_trend", "adx_bullish", "vortex_bullish",
            "macd_bullish_crossover", "macd_bearish_crossover",
            "stoch_overbought", "stoch_oversold",
            "williams_r_overbought", "williams_r_oversold",
            "cci_overbought", "cci_oversold",
            "bollinger_squeeze", "bb_above_upper", "bb_below_lower",
            "kc_above_upper", "kc_below_lower",
            "dc_breakout_up", "dc_breakout_down",
            "mfi_overbought", "mfi_oversold",
            "psar_bullish", "psar_bearish",
            "aroon_bullish", "aroon_bearish",
        ]:
            assert key in result, f"Missing pattern key: {key}"

    def test_recent_trend_valid_values(self):
        df = _make_ohlcv()
        df_ind = add_indicators(df)
        result = identify_patterns(df_ind)
        assert result["recent_trend"] in ("bullish", "bearish", "neutral")

    def test_boolean_flags(self):
        df = _make_ohlcv()
        df_ind = add_indicators(df)
        result = identify_patterns(df_ind)
        for key in [
            "golden_cross", "death_cross", "rsi_overbought", "rsi_oversold",
            "price_above_sma20", "price_above_sma50", "price_above_sma200",
            "macd_bullish_crossover", "macd_bearish_crossover",
            "bollinger_squeeze", "strong_trend", "adx_bullish",
            "vortex_bullish", "psar_bullish", "psar_bearish",
            "aroon_bullish", "aroon_bearish",
            "stoch_overbought", "stoch_oversold",
            "williams_r_overbought", "williams_r_oversold",
            "cci_overbought", "cci_oversold",
            "mfi_overbought", "mfi_oversold",
        ]:
            assert isinstance(result[key], bool), f"{key} should be bool"

    # --- Edge cases ---

    def test_very_short_dataframe(self):
        """identify_patterns should return an empty dict or graceful result for < 5 rows."""
        df = _make_ohlcv(n=3)
        df_ind = add_indicators(df)
        result = identify_patterns(df_ind)
        # Should not raise; recent_trend may be present or absent
        assert isinstance(result, dict)

    def test_all_nan_columns(self):
        """identify_patterns should handle DataFrames with all-NaN indicator columns."""
        df = _make_ohlcv(n=30)
        df_ind = add_indicators(df)
        # Force indicator columns to NaN
        for col in df_ind.columns:
            if col not in ("Open", "High", "Low", "Close", "Volume"):
                df_ind[col] = float("nan")
        result = identify_patterns(df_ind)
        assert isinstance(result, dict)
        # Boolean flags should default to False, not raise
        for key in ["rsi_overbought", "golden_cross", "macd_bullish_crossover"]:
            if key in result:
                assert isinstance(result[key], bool)
