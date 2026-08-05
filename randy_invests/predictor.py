"""Machine learning prediction module for stock price movements."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import accuracy_score
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class PipelineConfig:
    """Configuration object for the Randy-Invests analysis pipeline.

    Attributes:
        period_days: Days of historical data to download for training.
        forward_days: Prediction horizon in trading days.
        rf_n_estimators: Number of trees in the Random Forest.
        rf_max_depth: Maximum tree depth for the Random Forest.
        gb_n_estimators: Number of boosting stages for Gradient Boosting.
        gb_max_depth: Maximum tree depth for Gradient Boosting.
        cv_n_splits: Number of folds for time-series cross-validation.
        use_cache: Whether to use the local parquet data cache.
        cache_ttl_seconds: Cache freshness threshold in seconds.
    """

    period_days: int = 365
    forward_days: int = 5
    rf_n_estimators: int = 200
    rf_max_depth: int = 6
    gb_n_estimators: int = 100
    gb_max_depth: int = 4
    cv_n_splits: int = 5
    use_cache: bool = True
    cache_ttl_seconds: int = 3600


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------

FEATURE_COLS = [
    # Trend
    "sma_20", "sma_50", "sma_200",
    "ema_12", "ema_26", "ema_50",
    "wma_20",
    "macd", "macd_signal", "macd_diff",
    "adx", "adx_pos", "adx_neg",
    "aroon_up", "aroon_down",
    "cci", "dpo", "trix", "kst", "kst_signal",
    "vortex_pos", "vortex_neg",
    "psar_up_indicator", "psar_down_indicator",
    # Momentum
    "rsi", "roc", "tsi", "kama",
    "stoch_k", "stoch_d",
    "stochrsi_k", "stochrsi_d",
    "williams_r", "ultimate_oscillator", "awesome_oscillator",
    "ppo", "ppo_signal", "ppo_hist",
    "pvo", "pvo_signal", "pvo_hist",
    # Volatility
    "atr", "ulcer_index",
    "bb_width", "bb_pband",
    "dc_width", "dc_pband",
    "kc_width", "kc_pband",
    # Volume
    "obv", "chaikin_mf", "mfi", "nvi", "vpt",
    "ease_of_movement", "force_index",
    # Returns
    "daily_return", "daily_log_return",
]


def _prepare_features(df: pd.DataFrame, forward_days: int = 5) -> tuple[pd.DataFrame, pd.Series]:
    """Build feature matrix and classification target from indicator DataFrame.

    The target is 1 (buy) if the close price will be higher in *forward_days*
    trading sessions, else 0 (sell/hold).  The target is computed by shifting
    the Close price *backward* (i.e. ``Close.shift(-forward_days)``) so that
    each row's label reflects only *future* prices — no forward-looking data
    leaks into the features.

    Args:
        df: DataFrame with Close and all indicator columns from add_indicators().
        forward_days: Look-ahead window for computing the classification target.

    Returns:
        Tuple (X, y) where X contains feature columns and y is the binary target.

    Raises:
        ValueError: If there is insufficient data after feature engineering.
    """
    df = df.copy()
    # Shift -forward_days so the target is strictly forward-looking
    df["target"] = (df["Close"].shift(-forward_days) > df["Close"]).astype(int)
    # Add lag features
    for lag in [1, 3, 5]:
        df[f"return_lag{lag}"] = df["Close"].pct_change(lag)
    available_features = [
        c for c in FEATURE_COLS + ["return_lag1", "return_lag3", "return_lag5"]
        if c in df.columns
    ]
    df = df[available_features + ["target"]].dropna()
    X = df[available_features]
    y = df["target"]
    return X, y


# ---------------------------------------------------------------------------
# Predictor
# ---------------------------------------------------------------------------


class StockPredictor:
    """Ensemble stock predictor combining Random Forest and Gradient Boosting.

    Uses technical indicators as features to classify whether the stock will
    rise or fall over the next *forward_days* trading sessions, and provides
    a price-target estimate via Ridge regression.

    The classifier scaler (``scaler``) is fitted only on the training split.
    The Ridge regressor uses its own dedicated scaler (``lr_scaler``) fitted
    on the aligned regression training data to avoid leaking test information.

    Args:
        forward_days: Prediction horizon in trading days.
        config: Optional :class:`PipelineConfig` instance.  When provided,
            *forward_days* and all hyper-parameters are taken from *config*
            and the explicit *forward_days* argument is ignored.
    """

    def __init__(
        self,
        forward_days: int = 5,
        config: PipelineConfig | None = None,
    ):
        cfg = config or PipelineConfig(forward_days=forward_days)
        self.forward_days = cfg.forward_days
        self._config = cfg

        self.scaler = StandardScaler()
        self.lr_scaler = StandardScaler()  # dedicated scaler for Ridge
        self.rf = RandomForestClassifier(
            n_estimators=cfg.rf_n_estimators,
            max_depth=cfg.rf_max_depth,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )
        self.gb = GradientBoostingClassifier(
            n_estimators=cfg.gb_n_estimators,
            max_depth=cfg.gb_max_depth,
            random_state=42,
        )
        self.lr = Ridge()
        self._feature_cols: list[str] = []
        self._trained = False

    # ------------------------------------------------------------------
    # Training
    # ------------------------------------------------------------------

    def train(self, df: pd.DataFrame) -> dict:
        """Train all models on the indicator DataFrame.

        A :class:`~sklearn.model_selection.TimeSeriesSplit` cross-validation
        is run first to produce robust CV accuracy estimates; the final models
        are then re-fitted on the full 80 % training split.

        The Ridge regressor target is computed only on rows that belong to the
        *training* split, preventing any forward data leakage into the
        regression model.

        Args:
            df: DataFrame produced by technical_analysis.add_indicators().

        Returns:
            Dictionary with training metrics: rf_accuracy, gb_accuracy,
            ensemble_accuracy, cv_rf_accuracy, cv_gb_accuracy,
            train_samples, test_samples.

        Raises:
            ValueError: If there is insufficient data to train.
        """
        X, y = _prepare_features(df, self.forward_days)
        if len(X) < 50:
            raise ValueError(
                "Insufficient data to train the model (need at least 50 rows after feature engineering)."
            )
        self._feature_cols = list(X.columns)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        X_train_s = self.scaler.fit_transform(X_train.values)
        X_test_s = self.scaler.transform(X_test.values)

        # --- Time-series cross-validation ---
        cv_rf_scores: list[float] = []
        cv_gb_scores: list[float] = []
        tscv = TimeSeriesSplit(n_splits=self._config.cv_n_splits)
        X_arr = X_train.values
        y_arr = y_train.values
        for fold_train_idx, fold_val_idx in tscv.split(X_arr):
            fold_scaler = StandardScaler()
            Xf_train = fold_scaler.fit_transform(X_arr[fold_train_idx])
            Xf_val = fold_scaler.transform(X_arr[fold_val_idx])
            yf_train, yf_val = y_arr[fold_train_idx], y_arr[fold_val_idx]

            rf_fold = RandomForestClassifier(
                n_estimators=self._config.rf_n_estimators,
                max_depth=self._config.rf_max_depth,
                class_weight="balanced",
                random_state=42,
                n_jobs=-1,
            )
            gb_fold = GradientBoostingClassifier(
                n_estimators=self._config.gb_n_estimators,
                max_depth=self._config.gb_max_depth,
                random_state=42,
            )
            rf_fold.fit(Xf_train, yf_train)
            gb_fold.fit(Xf_train, yf_train)
            cv_rf_scores.append(accuracy_score(yf_val, rf_fold.predict(Xf_val)))
            cv_gb_scores.append(accuracy_score(yf_val, gb_fold.predict(Xf_val)))

        # --- Final fit on full training split ---
        self.rf.fit(X_train_s, y_train)
        self.gb.fit(X_train_s, y_train)

        # --- Ridge regression for price-target (% return) ---
        # Use only training-split rows to avoid leaking test data into the regressor.
        train_index = X_train.index
        # Forward return: shift by -forward_days gives the *future* return
        returns = df["Close"].pct_change(self.forward_days).shift(-self.forward_days).dropna()
        aligned_idx = train_index.intersection(returns.index).intersection(X.index)
        if len(aligned_idx) >= 10:
            aligned_X = X.loc[aligned_idx]
            aligned_y = returns.loc[aligned_idx]
            X_lr_s = self.lr_scaler.fit_transform(aligned_X.values)
            self.lr.fit(X_lr_s, aligned_y)
        else:
            logger.warning("Insufficient aligned rows (%d) to train Ridge regressor.", len(aligned_idx))

        rf_acc = accuracy_score(y_test, self.rf.predict(X_test_s))
        gb_acc = accuracy_score(y_test, self.gb.predict(X_test_s))
        ensemble_pred = (
            self.rf.predict_proba(X_test_s)[:, 1] + self.gb.predict_proba(X_test_s)[:, 1]
        ) / 2
        ensemble_acc = accuracy_score(y_test, (ensemble_pred >= 0.5).astype(int))

        self._trained = True
        return {
            "rf_accuracy": round(float(rf_acc), 4),
            "gb_accuracy": round(float(gb_acc), 4),
            "ensemble_accuracy": round(float(ensemble_acc), 4),
            "cv_rf_accuracy": round(float(np.mean(cv_rf_scores)), 4),
            "cv_gb_accuracy": round(float(np.mean(cv_gb_scores)), 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

    # ------------------------------------------------------------------
    # Prediction
    # ------------------------------------------------------------------

    def predict(self, df: pd.DataFrame) -> dict:
        """Generate predictions for the latest data point.

        Args:
            df: DataFrame produced by technical_analysis.add_indicators().

        Returns:
            Dictionary with:
                direction_probability: float [0, 1] — probability that price rises.
                predicted_direction: 'UP' or 'DOWN'.
                price_change_estimate_pct: estimated % price change over forward_days.
                confidence: 'HIGH' / 'MEDIUM' / 'LOW'.

        Raises:
            RuntimeError: If :meth:`train` has not been called yet.
            ValueError: If no valid data row is available for prediction.
        """
        if not self._trained:
            raise RuntimeError("Model has not been trained yet. Call train() first.")
        df = df.copy()
        for lag in [1, 3, 5]:
            df[f"return_lag{lag}"] = df["Close"].pct_change(lag)
        available_features = [c for c in self._feature_cols if c in df.columns]
        row = df[available_features].dropna().iloc[[-1]]
        if row.empty:
            raise ValueError("No valid data row available for prediction.")
        row_s = self.scaler.transform(row.values)

        rf_prob = float(self.rf.predict_proba(row_s)[0, 1])
        gb_prob = float(self.gb.predict_proba(row_s)[0, 1])
        direction_prob = (rf_prob + gb_prob) / 2

        try:
            row_lr_s = self.lr_scaler.transform(row.values)
            price_change_est = float(self.lr.predict(row_lr_s)[0]) * 100
        except Exception:  # noqa: BLE001
            price_change_est = 0.0

        predicted_dir = "UP" if direction_prob >= 0.5 else "DOWN"
        confidence_val = abs(direction_prob - 0.5) * 2  # 0 to 1
        if confidence_val >= 0.4:
            confidence = "HIGH"
        elif confidence_val >= 0.2:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "direction_probability": round(direction_prob, 4),
            "predicted_direction": predicted_dir,
            "price_change_estimate_pct": round(price_change_est, 4),
            "confidence": confidence,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str | Path) -> None:
        """Persist the trained predictor to disk using joblib.

        Args:
            path: File path (e.g. ``'model.pkl'``).  The parent directory is
                created if it does not already exist.

        Raises:
            RuntimeError: If the model has not been trained yet.
        """
        if not self._trained:
            raise RuntimeError("Model has not been trained yet. Call train() first.")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info("Predictor saved to %s", path)

    @classmethod
    def load(cls, path: str | Path) -> "StockPredictor":
        """Load a previously saved predictor from disk.

        Args:
            path: Path to the joblib file written by :meth:`save`.

        Returns:
            A fully trained :class:`StockPredictor` instance.

        Raises:
            FileNotFoundError: If *path* does not exist.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")
        predictor: StockPredictor = joblib.load(path)
        logger.info("Predictor loaded from %s", path)
        return predictor
