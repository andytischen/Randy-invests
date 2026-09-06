# Changelog

All notable changes to this project will be documented in this file.

## [0.3.1] - 2026-09-06

### Added
- Separate public pages: `/about`, `/learn`, `/channel` (`/youtube`), and `/advertise`.
- Randy Invests YouTube channel page with a middle-class investor icon, banner art, playlists, and an educational episode slate.
- Advertising desk: retail marketing channels, ready-to-run snippets, UTM share links, media-kit downloads, and a mocked partner form.

## [0.3.0] - 2026-09-06

### Added
- Retail investor web portal (`python -m randy_invests.web`) with public routes `/`, `/tiers`, `/tiers/<slug>`, and `/interest`.
- Seeded Bronze / Silver / Gold / Platinum catalogue: minimums, benefits, access, fees, hold periods, and eligibility notes.
- Side-by-side comparison table plus stacked cards; amount highlighter for an illustrative fit.
- Mocked express-interest form (in-memory inbox, no payments).
- JSON catalogue at `/api/tiers`. `/portal` and `/invest` redirect to `/tiers`.

### Fixed
- `pyproject.toml` build backend (`setuptools.build_meta`) so `pip install -e ".[dev]"` succeeds.

## [0.2.0] - 2026-08-05

### Added
- `PipelineConfig` dataclass to centralise all pipeline parameters (period, horizon, hyperparameters, cache settings).
- `run_pipeline()` pure function extracted from `analyse()` — fully testable with no I/O side effects.
- `StockPredictor.save()` / `StockPredictor.load()` for joblib-based model persistence.
- Time-series cross-validation (`TimeSeriesSplit`) — CV accuracy now reported alongside hold-out accuracy.
- `class_weight='balanced'` on `RandomForestClassifier` to handle UP/DOWN class imbalance.
- Dedicated `lr_scaler` for Ridge regressor to eliminate scaler data leakage.
- Local parquet cache for historical data (`~/.randy_invests/cache/`) with configurable TTL.
- `--json` / `--csv` CLI flags for machine-readable output.
- `--watchlist FILE` CLI flag to read tickers from a plain-text file.
- Multi-ticker summary table printed after all individual analyses.
- Financial disclaimer printed on every human-readable run.
- GitHub Actions CI workflow (lint + test on Python 3.9, 3.11, 3.12).
- `pyproject.toml` with entry-point so `randy-invests` works as an installed CLI.
- `CONTRIBUTING.md` with setup and PR guidelines.
- Test suite split into four focused files; new tests for `data_fetcher`, `main`, edge cases, and SELL/HOLD paths.

### Fixed
- `datetime.utcnow()` deprecated in Python 3.12 — replaced with `datetime.now(timezone.utc)`.
- Target leakage in Ridge regressor: forward return now computed via `pct_change().shift(-forward_days)` and restricted to the training split.
- Scoring bias in `recommender.py`: absent MACD crossover and absent Vortex signal no longer silently subtract from the score.
- Error message mismatch in `_prepare_features` (removed duplicate length check with wrong threshold).
- Silent indicator failures in `technical_analysis.py` now emit `DEBUG`-level log messages.

### Changed
- `add_indicators()` no longer reads the unused `open_` variable.
- Removed unused `from typing import Optional` (data_fetcher) and `from typing import Tuple` (predictor).
- `analyse()` now delegates all computation to `run_pipeline()`.

## [0.1.0] - Initial release
