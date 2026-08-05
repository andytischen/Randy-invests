"""Data fetching module for real-time and historical market data."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import yfinance as yf


def fetch_historical_data(
    ticker: str,
    period_days: int = 365,
    interval: str = "1d",
) -> pd.DataFrame:
    """Fetch historical OHLCV data for a ticker.

    Args:
        ticker: Stock ticker symbol (e.g. 'AAPL').
        period_days: Number of calendar days of history to fetch.
        interval: Data interval ('1d', '1h', '15m', etc.).

    Returns:
        DataFrame with columns Open, High, Low, Close, Volume indexed by Date.

    Raises:
        ValueError: If the ticker is invalid or no data is returned.
    """
    end = datetime.utcnow()
    start = end - timedelta(days=period_days)
    stock = yf.Ticker(ticker)
    df = stock.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), interval=interval)
    if df.empty:
        raise ValueError(f"No historical data returned for ticker '{ticker}'.")
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    return df[["Open", "High", "Low", "Close", "Volume"]]


def fetch_realtime_quote(ticker: str) -> dict:
    """Fetch the most recent real-time quote for a ticker.

    Args:
        ticker: Stock ticker symbol.

    Returns:
        Dictionary with keys: ticker, price, previous_close, change_pct,
        volume, market_cap, timestamp.
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
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
