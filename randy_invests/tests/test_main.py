"""Unit tests for main.py — run_pipeline and output formatters."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from randy_invests.main import (
    _results_to_csv,
    _results_to_json,
    _print_summary_table,
    run_pipeline,
)
from randy_invests.predictor import PipelineConfig
from randy_invests.recommender import Recommendation


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_result(ticker: str = "AAPL", signal: str = "BUY", score: float = 0.4) -> dict:
    rec = Recommendation(
        ticker=ticker,
        signal=signal,
        strength="MODERATE",
        score=score,
        reasons=["test reason"],
        price=150.0,
        price_change_estimate_pct=1.0,
        forward_days=5,
    )
    return {
        "ticker": ticker,
        "quote": {
            "ticker": ticker,
            "price": 150.0,
            "previous_close": 148.0,
            "change_pct": 1.35,
            "volume": 1_000_000,
            "market_cap": 2e12,
            "timestamp": "2024-01-01T00:00:00+00:00",
        },
        "patterns": {"recent_trend": "bullish"},
        "metrics": {
            "rf_accuracy": 0.55,
            "gb_accuracy": 0.57,
            "ensemble_accuracy": 0.56,
            "cv_rf_accuracy": 0.54,
            "cv_gb_accuracy": 0.55,
            "train_samples": 200,
            "test_samples": 50,
        },
        "prediction": {
            "direction_probability": 0.62,
            "predicted_direction": "UP",
            "price_change_estimate_pct": 1.0,
            "confidence": "MEDIUM",
        },
        "recommendation": rec,
    }


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------


class TestResultsToJson:
    def test_valid_json(self):
        results = [_make_result("AAPL"), _make_result("MSFT", signal="SELL", score=-0.3)]
        output = _results_to_json(results)
        data = json.loads(output)
        assert len(data) == 2
        assert data[0]["ticker"] == "AAPL"
        assert data[1]["ticker"] == "MSFT"

    def test_recommendation_keys_present(self):
        results = [_make_result()]
        data = json.loads(_results_to_json(results))
        rec = data[0]["recommendation"]
        for key in ["signal", "strength", "score", "price", "reasons"]:
            assert key in rec


class TestResultsToCsv:
    def test_has_header(self):
        results = [_make_result()]
        output = _results_to_csv(results)
        assert "ticker" in output.splitlines()[0]

    def test_has_data_row(self):
        results = [_make_result("AAPL")]
        output = _results_to_csv(results)
        lines = output.strip().splitlines()
        assert len(lines) == 2  # header + 1 data row
        assert "AAPL" in lines[1]

    def test_multiple_tickers(self):
        results = [_make_result("AAPL"), _make_result("MSFT")]
        output = _results_to_csv(results)
        lines = output.strip().splitlines()
        assert len(lines) == 3  # header + 2 data rows


class TestPrintSummaryTable:
    def test_prints_without_error(self, capsys):
        results = [_make_result("AAPL"), _make_result("MSFT", signal="SELL", score=-0.4)]
        _print_summary_table(results)
        captured = capsys.readouterr()
        assert "AAPL" in captured.out
        assert "MSFT" in captured.out
        assert "SUMMARY" in captured.out


# ---------------------------------------------------------------------------
# run_pipeline integration (mocked I/O)
# ---------------------------------------------------------------------------


def _make_ohlcv(n: int = 300) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    prices = 100 + np.cumsum(rng.normal(0, 1, n))
    prices = np.maximum(prices, 10)
    idx = pd.date_range("2023-01-01", periods=n, freq="B")
    df = pd.DataFrame(
        {
            "Open": prices,
            "High": prices * 1.01,
            "Low": prices * 0.99,
            "Close": prices,
            "Volume": rng.integers(1_000_000, 5_000_000, n),
        },
        index=idx,
    )
    df.index.name = "Date"
    return df


class TestRunPipeline:
    def test_returns_expected_keys(self):
        ohlcv = _make_ohlcv()
        mock_quote = {
            "ticker": "AAPL",
            "price": 150.0,
            "previous_close": 148.0,
            "change_pct": 1.35,
            "volume": 1_000_000,
            "market_cap": 2e12,
            "timestamp": "2024-01-01T00:00:00+00:00",
        }
        config = PipelineConfig(period_days=365, forward_days=5)
        with (
            patch("randy_invests.main.fetch_historical_data", return_value=ohlcv),
            patch("randy_invests.main.fetch_realtime_quote", return_value=mock_quote),
        ):
            result = run_pipeline("AAPL", config)

        for key in ["ticker", "quote", "patterns", "metrics", "prediction", "recommendation"]:
            assert key in result

    def test_recommendation_is_valid(self):
        ohlcv = _make_ohlcv()
        mock_quote = {
            "ticker": "AAPL",
            "price": 150.0,
            "previous_close": 148.0,
            "change_pct": 1.35,
            "volume": 1_000_000,
            "market_cap": 2e12,
            "timestamp": "2024-01-01T00:00:00+00:00",
        }
        config = PipelineConfig(period_days=365, forward_days=5)
        with (
            patch("randy_invests.main.fetch_historical_data", return_value=ohlcv),
            patch("randy_invests.main.fetch_realtime_quote", return_value=mock_quote),
        ):
            result = run_pipeline("AAPL", config)

        rec: Recommendation = result["recommendation"]
        assert rec.signal in ("BUY", "SELL", "HOLD")
        assert -1.0 <= rec.score <= 1.0
