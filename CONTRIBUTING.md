# Contributing to Randy-Invests

Thank you for your interest in contributing! Please follow these guidelines.

## Development Setup

```bash
# Clone the repo
git clone https://github.com/andytischen/Randy-invests.git
cd Randy-invests

# Install in editable mode with dev dependencies
pip install -e ".[dev]" pyarrow
```

## Running Tests

```bash
pytest randy_invests/tests/ -v
```

## Linting

```bash
ruff check randy_invests/
```

To auto-fix safe issues:

```bash
ruff check --fix randy_invests/
```

## Submitting a Pull Request

1. Fork the repository and create a feature branch from `main`.
2. Write or update tests for your changes.
3. Ensure all tests pass and linting is clean.
4. Open a PR against `main` with a clear description of what changed and why.

## Project Structure

```
randy_invests/
├── data_fetcher.py        # Real-time & historical data via yfinance (with caching)
├── technical_analysis.py  # Technical indicators & pattern detection
├── predictor.py           # ML ensemble + PipelineConfig
├── recommender.py         # Buy/sell/hold recommendation engine
├── main.py                # CLI entry point (run_pipeline + analyse)
└── tests/
    ├── test_data_fetcher.py
    ├── test_technical_analysis.py
    ├── test_predictor.py
    ├── test_recommender.py
    └── test_main.py
```
