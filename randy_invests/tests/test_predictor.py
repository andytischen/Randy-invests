"""Unit tests for the predictor and PipelineConfig modules."""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from randy_invests.predictor import PipelineConfig, StockPredictor
from randy_invests.technical_analysis import add_indicators


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
# PipelineConfig
# ---------------------------------------------------------------------------


class TestPipelineConfig:
    def test_defaults(self):
        cfg = PipelineConfig()
        assert cfg.period_days == 365
        assert cfg.forward_days == 5
        assert cfg.cv_n_splits == 5
        assert cfg.use_cache is True

    def test_custom_values(self):
        cfg = PipelineConfig(forward_days=10, rf_n_estimators=50, gb_max_depth=3)
        assert cfg.forward_days == 10
        assert cfg.rf_n_estimators == 50
        assert cfg.gb_max_depth == 3


# ---------------------------------------------------------------------------
# StockPredictor
# ---------------------------------------------------------------------------


class TestStockPredictor:
    def test_train_returns_metrics(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor(forward_days=5)
        metrics = predictor.train(df_ind)
        for key in ["rf_accuracy", "gb_accuracy", "ensemble_accuracy",
                    "cv_rf_accuracy", "cv_gb_accuracy",
                    "train_samples", "test_samples"]:
            assert key in metrics

    def test_accuracy_in_valid_range(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor(forward_days=5)
        metrics = predictor.train(df_ind)
        for key in ["rf_accuracy", "gb_accuracy", "ensemble_accuracy",
                    "cv_rf_accuracy", "cv_gb_accuracy"]:
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

    def test_config_hyperparameters_used(self):
        cfg = PipelineConfig(rf_n_estimators=10, gb_n_estimators=10, cv_n_splits=2)
        predictor = StockPredictor(config=cfg)
        assert predictor.rf.n_estimators == 10
        assert predictor.gb.n_estimators == 10

    def test_save_and_load(self):
        df = _make_ohlcv(300)
        df_ind = add_indicators(df)
        predictor = StockPredictor(forward_days=5)
        predictor.train(df_ind)
        orig_pred = predictor.predict(df_ind)

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "model.pkl"
            predictor.save(path)
            assert path.exists()

            loaded = StockPredictor.load(path)
            loaded_pred = loaded.predict(df_ind)

        assert loaded_pred["predicted_direction"] == orig_pred["predicted_direction"]
        assert loaded_pred["direction_probability"] == orig_pred["direction_probability"]

    def test_save_before_train_raises(self):
        predictor = StockPredictor()
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(RuntimeError):
                predictor.save(Path(tmpdir) / "model.pkl")

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            StockPredictor.load("/tmp/does_not_exist_randy.pkl")
