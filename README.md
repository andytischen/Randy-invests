# Randy-Invests

[![CI](https://github.com/andytischen/Randy-invests/actions/workflows/ci.yml/badge.svg)](https://github.com/andytischen/Randy-invests/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> ⚠ **Disclaimer**: Randy-Invests is for informational and educational purposes only.
> Nothing in this output constitutes financial advice, a recommendation to buy or sell any security,
> or an offer or solicitation to trade. Always do your own research and consult a qualified financial
> professional before investing.

A comprehensive **ML-powered stock market predictor** with buy/sell recommendations, real-time market data, historical pattern analysis, and a **retail investor portal** that presents investment access tiers.

## Retail investor portal

A public web desk where retail investors can compare **Bronze / Silver / Gold / Platinum** programs — minimums, benefits, fees, hold periods, and eligibility — then express interest (payments are mocked). It also lists **share recommendations structured for retail investors** (`/recommendations`): the ML model's buy/hold/sell read on each stock, restated as a plain-language stance, an illustrative estimated move, and a few de-jargoned talking points.

```bash
# After install (see below)
python -m randy_invests.web
# or: randy-invests-portal
```

Then open:

| Route | What it is |
| --- | --- |
| [http://127.0.0.1:5000/tiers](http://127.0.0.1:5000/tiers) | **Comparison portal** (cards + side-by-side table) |
| [http://127.0.0.1:5000/recommendations](http://127.0.0.1:5000/recommendations) | **Share ideas** — ML buy/hold/sell reads structured for retail investors |
| [http://127.0.0.1:5000/](http://127.0.0.1:5000/) | Overview / landing |
| [http://127.0.0.1:5000/channel](http://127.0.0.1:5000/channel) | **YouTube channel** (Randy icon, playlists, episode slate) |
| [http://127.0.0.1:5000/advertise](http://127.0.0.1:5000/advertise) | Marketing playbook, ad snippets, partner form |
| [http://127.0.0.1:5000/about](http://127.0.0.1:5000/about) | Meet Randy |
| [http://127.0.0.1:5000/learn](http://127.0.0.1:5000/learn) | How the desk works |
| [http://127.0.0.1:5000/interest](http://127.0.0.1:5000/interest) | Express-interest form |
| `/tiers/gold` (etc.) | Single-tier notes |
| `/recommendations?tickers=AAPL+MSFT` | Look up your own symbols (up to 6) |
| `/youtube` | Alias for `/channel` |
| `/portal` and `/invest` | Redirects to `/tiers` |
| `/api/tiers`, `/api/recommendations` | JSON catalogue / share ideas |

Optional: bind another interface with `HOST=0.0.0.0 PORT=5000 python -m randy_invests.web`.

The **Randy Invests** YouTube face is a generated channel icon of Randy — a middle-class member of the investment community — plus kitchen-table channel art. Both live in `randy_invests/web/static/img/`. This repo cannot open a live YouTube account; it ships the branded channel page. Point Subscribe at a real property with `YOUTUBE_CHANNEL_URL`.

There is **no account system** in this release. The `/tiers` page is public. Enter an amount on that page to highlight an illustrative fit. When auth is added later, a signed-in retail user should see the tier they already hold against the same catalogue (`randy_invests/web/tiers.py`).

Tier figures are **seeded demo data**, not a live offering. Footer copy is conservative: illustrative information, not financial advice.

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
- **Retail investor portal** — Flask app at `/tiers` comparing Bronze, Silver, Gold, and Platinum access programs, plus `/recommendations` presenting share recommendations structured for retail investors.

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
├── web/                   # Retail investor portal (Flask)
│   ├── app.py             # Routes: /, /tiers, /recommendations, /interest, /api/*
│   ├── tiers.py           # Seeded Bronze–Platinum catalogue
│   ├── recommendations.py # Retail-structured share recommendations (wraps run_pipeline)
│   ├── templates/         # Jinja pages
│   └── static/            # Portal CSS / JS
└── tests/
    ├── test_data_fetcher.py      # Data fetcher tests (mocked yfinance)
    ├── test_technical_analysis.py
    ├── test_predictor.py
    ├── test_recommender.py
    ├── test_main.py              # run_pipeline + output formatter tests
    ├── test_tiers.py             # Catalogue + interest-form validation
    ├── test_recommendations.py   # Retail share-recommendation structuring
    └── test_web.py               # Portal HTTP tests
```

## Running Tests

```bash
pytest randy_invests/tests/ -v
```
