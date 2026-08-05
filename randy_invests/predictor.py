"""Machine learning prediction module for stock price movements."""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


FEATURE_COLS = [
    "rsi",
    "macd",
    "macd_signal",
    "macd_diff",
    "sma_20",
    "sma_50",
    "ema_12",
    "ema_26",
    "bb_width",
    "atr",
    "stoch_k",
    "stoch_d",
    "obv",
]


def _prepare_features(df: pd.DataFrame, forward_days: int = 5) -> Tuple[pd.DataFrame, pd.Series]:
    """Build feature matrix and classification target from indicator DataFrame.

    The target is 1 (buy) if the close price will be higher in `forward_days`
    trading sessions, else 0 (sell/hold).

    Args:
        df: DataFrame with Close and all indicator columns from add_indicators().
        forward_days: Look-ahead window for computing the classification target.

    Returns:
        Tuple (X, y) where X contains feature columns and y is the binary target.

    Raises:
        ValueError: If there is insufficient data after feature engineering.
    """
    if len(df) < 10:
        raise ValueError("Insufficient data to train the model (need at least 50 rows after feature engineering).")
    df = df.copy()
    df["target"] = (df["Close"].shift(-forward_days) > df["Close"]).astype(int)
    # Add lag features
    for lag in [1, 3, 5]:
        df[f"return_lag{lag}"] = df["Close"].pct_change(lag)
    available_features = [c for c in FEATURE_COLS + ["return_lag1", "return_lag3", "return_lag5"] if c in df.columns]
    df = df[available_features + ["target"]].dropna()
    X = df[available_features]
    y = df["target"]
    return X, y


class StockPredictor:
    """Ensemble stock predictor combining Random Forest and Gradient Boosting.

    Uses technical indicators as features to classify whether the stock will
    rise or fall over the next `forward_days` trading sessions, and provides
    a price target estimate via linear regression.
    """

    def __init__(self, forward_days: int = 5):
        self.forward_days = forward_days
        self.scaler = StandardScaler()
        self.rf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42, n_jobs=-1)
        self.gb = GradientBoostingClassifier(n_estimators=100, max_depth=4, random_state=42)
        self.lr = Ridge()
        self._feature_cols: list[str] = []
        self._trained = False

    def train(self, df: pd.DataFrame) -> dict:
        """Train all models on the indicator DataFrame.

        Args:
            df: DataFrame produced by technical_analysis.add_indicators().

        Returns:
            Dictionary with training metrics: rf_accuracy, gb_accuracy, ensemble_accuracy,
            train_samples, test_samples.
        """
        X, y = _prepare_features(df, self.forward_days)
        if len(X) < 50:
            raise ValueError("Insufficient data to train the model (need at least 50 rows after feature engineering).")
        self._feature_cols = list(X.columns)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        X_train_s = self.scaler.fit_transform(X_train.values)
        X_test_s = self.scaler.transform(X_test.values)

        self.rf.fit(X_train_s, y_train)
        self.gb.fit(X_train_s, y_train)

        # Linear regression for price target (% return)
        returns = df["Close"].pct_change(self.forward_days).dropna()
        aligned = X.loc[returns.index.intersection(X.index)]
        aligned_returns = returns.loc[aligned.index]
        if len(aligned) >= 10:
            self.lr.fit(self.scaler.transform(aligned.values), aligned_returns)

        rf_acc = accuracy_score(y_test, self.rf.predict(X_test_s))
        gb_acc = accuracy_score(y_test, self.gb.predict(X_test_s))
        ensemble_pred = (self.rf.predict_proba(X_test_s)[:, 1] + self.gb.predict_proba(X_test_s)[:, 1]) / 2
        ensemble_acc = accuracy_score(y_test, (ensemble_pred >= 0.5).astype(int))

        self._trained = True
        return {
            "rf_accuracy": round(float(rf_acc), 4),
            "gb_accuracy": round(float(gb_acc), 4),
            "ensemble_accuracy": round(float(ensemble_acc), 4),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
        }

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
            price_change_est = float(self.lr.predict(row_s)[0]) * 100
        except Exception:
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
