"""Data fetching module for real-time and historical market data."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache configuration
# ---------------------------------------------------------------------------

_DEFAULT_CACHE_DIR = Path.home() / ".randy_invests" / "cache"
_DEFAULT_CACHE_TTL_SECONDS = 3600  # 1 hour


def _cache_path(ticker: str, period_days: int, interval: str, cache_dir: Path) -> Path:
    """Return the parquet file path for a given cache key."""
    return cache_dir / f"{ticker.upper()}_{period_days}d_{interval}.parquet"


def _cache_is_fresh(path: Path, ttl_seconds: int) -> bool:
    """Return True if the cache file exists and is newer than *ttl_seconds*."""
    if not path.exists():
        return False
    age = datetime.now(timezone.utc).timestamp() - path.stat().st_mtime
    return age < ttl_seconds


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def fetch_historical_data(
    ticker: str,
    period_days: int = 365,
    interval: str = "1d",
    use_cache: bool = True,
    cache_dir: Path | None = None,
    cache_ttl_seconds: int = _DEFAULT_CACHE_TTL_SECONDS,
) -> pd.DataFrame:
    """Fetch historical OHLCV data for a ticker, with optional file caching.

    Results are stored as parquet files under *cache_dir* (default:
    ``~/.randy_invests/cache/``).  A cached file is considered fresh when it
    is younger than *cache_ttl_seconds* seconds.  Set ``use_cache=False`` to
    always download fresh data.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL').
        period_days: Number of calendar days of history to fetch.
        interval: Data interval ('1d', '1h', '15m', etc.).
        use_cache: Whether to read from / write to the local parquet cache.
        cache_dir: Directory used for caching.  Defaults to
            ``~/.randy_invests/cache/``.
        cache_ttl_seconds: Maximum age (seconds) for a cached file to be
            considered fresh.

    Returns:
        DataFrame with columns Open, High, Low, Close, Volume indexed by Date.

    Raises:
        ValueError: If the ticker is invalid or no data is returned.
    """
    resolved_cache_dir = cache_dir or _DEFAULT_CACHE_DIR

    if use_cache:
        path = _cache_path(ticker, period_days, interval, resolved_cache_dir)
        if _cache_is_fresh(path, cache_ttl_seconds):
            logger.debug("Cache hit for %s (%dd %s)", ticker, period_days, interval)
            return pd.read_parquet(path)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=period_days)
    stock = yf.Ticker(ticker)
    df = stock.history(
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        interval=interval,
    )
    if df.empty:
        raise ValueError(f"No historical data returned for ticker '{ticker}'.")
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    df = df[["Open", "High", "Low", "Close", "Volume"]]

    if use_cache:
        resolved_cache_dir.mkdir(parents=True, exist_ok=True)
        path = _cache_path(ticker, period_days, interval, resolved_cache_dir)
        df.to_parquet(path)
        logger.debug("Cached %s to %s", ticker, path)

    return df


def fetch_realtime_quote(ticker: str) -> dict:
    """Fetch the most recent real-time quote for a ticker.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Dictionary with keys: ticker, price, previous_close, change_pct,
        volume, market_cap, timestamp.

    Raises:
        ValueError: If the quote cannot be retrieved (invalid ticker, network
            error, or missing fields in the API response).
    """
    stock = yf.Ticker(ticker)
    info = stock.fast_info
    try:
        price = float(info.last_price)
        previous_close = float(info.previous_close)
        volume = int(info.three_month_average_volume or 0)
        market_cap = float(getattr(info, "market_cap", 0) or 0)
    except Exception as exc:
        raise ValueError(f"Could not retrieve real-time quote for '{ticker}': {exc}") from exc

    change_pct = ((price - previous_close) / previous_close * 100) if previous_close else 0.0

    return {
        "ticker": ticker.upper(),
        "price": round(price, 4),
        "previous_close": round(previous_close, 4),
        "change_pct": round(change_pct, 4),
        "volume": volume,
        "market_cap": market_cap,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
