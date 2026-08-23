"""Unit tests for the data_fetcher module (mocked yfinance calls)."""

from __future__ import annotations

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from randy_invests.data_fetcher import (
    _cache_is_fresh,
    _cache_path,
    fetch_historical_data,
    fetch_realtime_quote,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ohlcv(n: int = 20) -> pd.DataFrame:
    rng = np.random.default_rng(0)
    prices = 100 + np.cumsum(rng.normal(0, 1, n))
    idx = pd.date_range("2023-01-01", periods=n, freq="B", tz="UTC")
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


# ---------------------------------------------------------------------------
# fetch_historical_data
# ---------------------------------------------------------------------------


class TestFetchHistoricalData:
    def test_returns_dataframe(self):
        mock_df = _make_ohlcv()
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = mock_df
            result = fetch_historical_data("AAPL", period_days=30, use_cache=False)
        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]

    def test_raises_on_empty_response(self):
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = pd.DataFrame()
            with pytest.raises(ValueError, match="No historical data"):
                fetch_historical_data("INVALID", use_cache=False)

    def test_cache_write_and_read(self):
        mock_df = _make_ohlcv()
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
                mock_ticker.return_value.history.return_value = mock_df
                # First call: writes to cache
                r1 = fetch_historical_data(
                    "AAPL", period_days=30, use_cache=True,
                    cache_dir=cache_dir, cache_ttl_seconds=3600,
                )
                # Second call: reads from cache (no yf call)
                r2 = fetch_historical_data(
                    "AAPL", period_days=30, use_cache=True,
                    cache_dir=cache_dir, cache_ttl_seconds=3600,
                )
            assert len(r1) == len(r2)
            # Only one real download should have occurred
            assert mock_ticker.return_value.history.call_count == 1

    def test_stale_cache_triggers_download(self):
        mock_df = _make_ohlcv()
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
                mock_ticker.return_value.history.return_value = mock_df
                # Write with ttl=0 so it is immediately stale
                fetch_historical_data(
                    "AAPL", period_days=30, use_cache=True,
                    cache_dir=cache_dir, cache_ttl_seconds=0,
                )
                fetch_historical_data(
                    "AAPL", period_days=30, use_cache=True,
                    cache_dir=cache_dir, cache_ttl_seconds=0,
                )
            # Two downloads because cache is always stale
            assert mock_ticker.return_value.history.call_count == 2

    def test_no_cache_always_downloads(self):
        mock_df = _make_ohlcv()
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.history.return_value = mock_df
            fetch_historical_data("AAPL", period_days=30, use_cache=False)
            fetch_historical_data("AAPL", period_days=30, use_cache=False)
        assert mock_ticker.return_value.history.call_count == 2


# ---------------------------------------------------------------------------
# fetch_realtime_quote
# ---------------------------------------------------------------------------


class TestFetchRealtimeQuote:
    def _make_fast_info(self, price=150.0, prev_close=148.0, volume=1_000_000, market_cap=2e12):
        info = MagicMock()
        info.last_price = price
        info.previous_close = prev_close
        info.three_month_average_volume = volume
        info.market_cap = market_cap
        return info

    def test_returns_expected_keys(self):
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = self._make_fast_info()
            result = fetch_realtime_quote("AAPL")
        for key in ["ticker", "price", "previous_close", "change_pct", "volume", "market_cap", "timestamp"]:
            assert key in result

    def test_change_pct_calculation(self):
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = self._make_fast_info(price=110.0, prev_close=100.0)
            result = fetch_realtime_quote("AAPL")
        assert abs(result["change_pct"] - 10.0) < 0.01

    def test_ticker_uppercased(self):
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = self._make_fast_info()
            result = fetch_realtime_quote("aapl")
        assert result["ticker"] == "AAPL"

    def test_raises_on_missing_fast_info_fields(self):
        info = MagicMock()
        info.last_price = None  # will fail float(None)
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = info
            # float(None) raises TypeError, which should be wrapped in ValueError
            with pytest.raises(ValueError, match="Could not retrieve"):
                fetch_realtime_quote("INVALID")

    def test_zero_previous_close_does_not_divide_by_zero(self):
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = self._make_fast_info(prev_close=0.0)
            result = fetch_realtime_quote("AAPL")
        assert result["change_pct"] == 0.0

    def test_timestamp_is_utc_iso_string(self):
        with patch("randy_invests.data_fetcher.yf.Ticker") as mock_ticker:
            mock_ticker.return_value.fast_info = self._make_fast_info()
            result = fetch_realtime_quote("AAPL")
        # Should be parseable as an ISO datetime
        dt = datetime.fromisoformat(result["timestamp"])
        assert dt.tzinfo is not None


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------


class TestCacheHelpers:
    def test_cache_path_format(self):
        path = _cache_path("AAPL", 365, "1d", Path("/tmp"))
        assert path.name == "AAPL_365d_1d.parquet"

    def test_cache_is_fresh_missing_file(self):
        assert _cache_is_fresh(Path("/tmp/does_not_exist_randy.parquet"), 3600) is False

    def test_cache_is_fresh_new_file(self):
        with tempfile.NamedTemporaryFile(suffix=".parquet") as f:
            assert _cache_is_fresh(Path(f.name), 3600) is True

    def test_cache_is_stale_ttl_zero(self):
        with tempfile.NamedTemporaryFile(suffix=".parquet") as f:
            assert _cache_is_fresh(Path(f.name), 0) is False
