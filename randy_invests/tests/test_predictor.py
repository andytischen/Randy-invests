"""Unit tests for the Randy-Invests stock market predictor."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from randy_invests.predictor import StockPredictor
from randy_invests.recommender import generate_recommendation
from randy_invests.technical_analysis import add_indicators, identify_patterns


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_ohlcv(n: int = 300, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic OHLCV data for testing."""
    rng = np.random.default_rng(seed)
    prices = 100 + np.cumsum(rng.normal(0, 1, n))
    prices = np.maximum(prices, 10)  # keep positive
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
# Technical analysis tests
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
            # Trend
            "sma_20", "sma_50", "sma_200", "ema_12", "ema_26", "ema_50", "wma_20",
            "macd", "macd_signal", "macd_diff",
            "adx", "adx_pos", "adx_neg",
            "aroon_up", "aroon_down",
            "cci", "trix", "kst", "vortex_pos", "vortex_neg",
            "psar_up_indicator", "psar_down_indicator",
            "ichimoku_conv", "ichimoku_base",
            # Momentum
            "rsi", "roc", "williams_r", "ultimate_oscillator", "awesome_oscillator",
            "stoch_k", "stoch_d", "stochrsi_k", "stochrsi_d",
            "ppo", "pvo",
            # Volatility
            "atr", "bb_upper", "bb_middle", "bb_lower", "bb_width", "bb_pband",
            "dc_upper", "dc_lower", "dc_width",
            "kc_upper", "kc_lower", "kc_width",
            # Volume
            "obv", "chaikin_mf", "mfi", "vpt", "force_index",
            # Others
            "daily_return", "daily_log_return", "cumulative_return",
        ]
        for col in expected_cols:
            assert col in result.columns, f"Missing column: {col}"

    def test_does_not_modify_original(self):
        df = _make_ohlcv()
        original_cols = list(df.columns)
        add_indicators(df)
        assert list(df.columns) == original_cols


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
            assert key in result

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


# ---------------------------------------------------------------------------
# ML Predictor tests
# ---------------------------------------------------------------------------

class TestStockPredictor:
    def test_train_returns_metrics(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor(forward_days=5)
        metrics = predictor.train(df_ind)
        for key in ["rf_accuracy", "gb_accuracy", "ensemble_accuracy", "train_samples", "test_samples"]:
            assert key in metrics

    def test_accuracy_in_valid_range(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor(forward_days=5)
        metrics = predictor.train(df_ind)
        for key in ["rf_accuracy", "gb_accuracy", "ensemble_accuracy"]:
            assert 0.0 <= metrics[key] <= 1.0

    def test_predict_after_train(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor(forward_days=5)
        predictor.train(df_ind)
        result = predictor.predict(df_ind)
        assert result["predicted_direction"] in ("UP", "DOWN")
        assert 0.0 <= result["direction_probability"] <= 1.0
        assert result["confidence"] in ("HIGH", "MEDIUM", "LOW")

    def test_predict_before_train_raises(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor()
        with pytest.raises(RuntimeError):
            predictor.predict(df_ind)

    def test_train_insufficient_data_raises(self):
        # Build a minimal indicator dataframe (bypassing add_indicators which needs n>=14)
        n = 5
        rng = np.random.default_rng(99)
        prices = 100 + np.cumsum(rng.normal(0, 1, n))
        idx = pd.date_range("2023-01-01", periods=n, freq="B")
        small_df = pd.DataFrame(
            {"Open": prices, "High": prices * 1.01, "Low": prices * 0.99,
             "Close": prices, "Volume": [1_000_000] * n},
            index=idx,
        )
        small_df.index.name = "Date"
        predictor = StockPredictor()
        with pytest.raises((ValueError, Exception)):
            predictor.train(small_df)


# ---------------------------------------------------------------------------
# Recommender tests
# ---------------------------------------------------------------------------

class TestRecommender:
    def _sample_inputs(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor(forward_days=5)
        metrics = predictor.train(df_ind)
        prediction = predictor.predict(df_ind)
        patterns = identify_patterns(df_ind)
        quote = {
            "ticker": "TEST",
            "price": 150.0,
            "previous_close": 148.0,
            "change_pct": 1.35,
            "volume": 1_000_000,
            "market_cap": 2e12,
            "timestamp": "2024-01-01T00:00:00Z",
        }
        return quote, prediction, patterns, metrics

    def test_returns_recommendation(self):
        from randy_invests.recommender import Recommendation
        quote, prediction, patterns, metrics = self._sample_inputs()
        rec = generate_recommendation("TEST", quote, prediction, patterns, metrics)
        assert isinstance(rec, Recommendation)

    def test_signal_is_valid(self):
        quote, prediction, patterns, metrics = self._sample_inputs()
        rec = generate_recommendation("TEST", quote, prediction, patterns, metrics)
        assert rec.signal in ("BUY", "SELL", "HOLD")

    def test_strength_is_valid(self):
        quote, prediction, patterns, metrics = self._sample_inputs()
        rec = generate_recommendation("TEST", quote, prediction, patterns, metrics)
        assert rec.strength in ("STRONG", "MODERATE", "WEAK")

    def test_score_in_range(self):
        quote, prediction, patterns, metrics = self._sample_inputs()
        rec = generate_recommendation("TEST", quote, prediction, patterns, metrics)
        assert -1.0 <= rec.score <= 1.0

    def test_reasons_not_empty(self):
        quote, prediction, patterns, metrics = self._sample_inputs()
        rec = generate_recommendation("TEST", quote, prediction, patterns, metrics)
        assert len(rec.reasons) > 0

    def test_str_representation(self):
        quote, prediction, patterns, metrics = self._sample_inputs()
        rec = generate_recommendation("TEST", quote, prediction, patterns, metrics)
        text = str(rec)
        assert "TEST" in text
        assert rec.signal in text
