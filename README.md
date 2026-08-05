# Randy-Invests

[![CI](https://github.com/andytischen/Randy-invests/actions/workflows/ci.yml/badge.svg)](https://github.com/andytischen/Randy-invests/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> ⚠ **Disclaimer**: Randy-Invests is for informational and educational purposes only.
> Nothing in this output constitutes financial advice, a recommendation to buy or sell any security,
> or an offer or solicitation to trade. Always do your own research and consult a qualified financial
> professional before investing.

A comprehensive **ML-powered stock market predictor** with buy/sell recommendations, real-time market data, and historical pattern analysis.

## Features

- **Real-Time Market Data** — Fetches live quotes (price, change %, volume, market cap) via `yfinance`.
- **Historical Analysis** — Downloads up to N days of OHLCV data and computes a rich set of technical indicators:
  - RSI, MACD, Stochastic Oscillator
  - Bollinger Bands, ATR
  - SMA-20/50, EMA-12/26
  - On-Balance Volume (OBV)
- **Pattern Detection** — Automatically identifies Golden Cross, Death Cross, MACD crossovers, Bollinger squeezes, and more.
- **Machine Learning Predictions** — Ensemble of Random Forest + Gradient Boosting classifiers trained on technical indicators to predict the price direction over a configurable time horizon.
- **Buy/Sell Recommendations** — Composite scoring engine combines ML predictions, technical signals, and real-time performance to produce `BUY / SELL / HOLD` recommendations with strength ratings.

## Installation

```bash
pip install -e ".[dev]" pyarrow
```

Or just install runtime dependencies:

```bash
pip install -r requirements.txt pyarrow
```

## Usage

```bash
# Analyse one or more tickers
python -m randy_invests.main AAPL MSFT TSLA

# Customise the historical window and prediction horizon
python -m randy_invests.main NVDA --period 730 --forward 10

# Read tickers from a watchlist file (one per line)
python -m randy_invests.main --watchlist my_stocks.txt

# Output as JSON or CSV (useful for scripting)
python -m randy_invests.main AAPL MSFT --json
python -m randy_invests.main AAPL MSFT --csv

# Disable local data cache (always fetch fresh data)
python -m randy_invests.main AAPL --no-cache
```

### Example Output

```
============================================================
  Randy-Invests Stock Market Predictor: AAPL
============================================================

[1/4] Fetching historical data (365 days)...
      Loaded 252 trading days.

[2/4] Fetching real-time quote...
      AAPL @ $189.30  (+0.74% today)

[3/4] Computing technical indicators and patterns...
      Recent trend: BULLISH
      Active signals: Above SMA-20, Above SMA-50

[4/4] Training ML models and generating prediction...
      Model accuracy — RF: 53.1%  GB: 55.9%  Ensemble: 55.9%

=== AAPL Recommendation ===
Signal   : MODERATE BUY
Score    : +0.408 (range −1 sell → +1 buy)
Price    : $189.30
Est. change in 5d: +1.23%
Reasons  :
  • ML ensemble predicts UP with MEDIUM confidence (prob=0.62)
  • Recent 20-day price trend is bullish
  • Price trading above both SMA-20 and SMA-50 (bullish)
  • Positive day change: +0.74%
```

## Project Structure

```
randy_invests/
├── data_fetcher.py        # Real-time & historical data via yfinance (with caching)
├── technical_analysis.py  # Technical indicators & pattern detection
├── predictor.py           # ML ensemble + PipelineConfig dataclass
├── recommender.py         # Buy/sell/hold recommendation engine
├── main.py                # CLI entry point (run_pipeline + analyse)
└── tests/
    ├── test_data_fetcher.py      # Data fetcher tests (mocked yfinance)
    ├── test_technical_analysis.py
    ├── test_predictor.py
    ├── test_recommender.py
    └── test_main.py              # run_pipeline + output formatter tests
```

## Running Tests

```bash
pytest randy_invests/tests/ -v
```
