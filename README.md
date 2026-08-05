# Randy-Invests

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
pip install -r requirements.txt
```

## Usage

```bash
# Analyse one or more tickers
python -m randy_invests.main AAPL MSFT TSLA

# Customise the historical window and prediction horizon
python -m randy_invests.main NVDA --period 730 --forward 10
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
├── data_fetcher.py        # Real-time & historical data via yfinance
├── technical_analysis.py  # Technical indicators & pattern detection
├── predictor.py           # ML ensemble (Random Forest + Gradient Boosting)
├── recommender.py         # Buy/sell/hold recommendation engine
├── main.py                # CLI entry point
└── tests/
    └── test_predictor.py  # Unit tests
```

## Running Tests

```bash
pytest randy_invests/tests/ -v
```
