import pandas as pd
import numpy as np
from sklearn.ensemble import (
    GradientBoostingClassifier,
    RandomForestClassifier,
    VotingClassifier,
)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit, cross_val_score
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class AIPredictor:
    """
    An AI module that uses a Gradient Boosting Classifier to predict the probability
    of a positive price movement in the next period.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        gb = GradientBoostingClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
        )
        rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        lr = LogisticRegression(random_state=42, max_iter=1000)

        self.model = VotingClassifier(
            estimators=[("gb", gb), ("rf", rf), ("lr", lr)], voting="soft"
        )
        self.scaler = StandardScaler()
        self.is_trained = False

    def prepare_features(self):
        """Prepares features and target variable for the model."""
        if self.df.empty or len(self.df) < 50:
            return None, None

        features = [
            "RSI_14",
            "MACD",
            "MACD_Hist",
            "ATR_14",
            "Close",
            "SMA_20",
            "SMA_50",
            "ADX",
            "Stoch_RSI_K",
            "Stoch_RSI_D",
            "VWAP",
            "Volume",
        ]

        # Check if features exist
        available_features = [f for f in features if f in self.df.columns]
        if len(available_features) < len(features):
            return None, None

        df_ml = self.df.copy()

        # Calculate derived features
        df_ml["Price_Change"] = df_ml["Close"].pct_change(fill_method=None)
        df_ml["SMA_Diff"] = (df_ml["SMA_20"] - df_ml["SMA_50"]) / df_ml["SMA_50"]

        # Target: 1 if next period's return is positive, 0 otherwise
        df_ml["Target"] = (df_ml["Close"].shift(-1) > df_ml["Close"]).astype(int)

        # Drop rows with NaN values created by indicators or shift
        df_ml = df_ml.dropna()

        ml_features = available_features + ["Price_Change", "SMA_Diff"]
        X = df_ml[ml_features]
        y = df_ml["Target"]

        return X, y, ml_features

    def train_and_predict(self) -> dict:
        """
        Trains the model on historical data and predicts the probability
        of a positive return for the current (latest) period.
        """
        X, y, feature_cols = self.prepare_features()

        if X is None or len(X) < 30:
            logger.warning("Not enough data to train AI Predictor.")
            return {"confidence": 50.0, "cv_accuracy": 0.0, "feature_importances": {}}

        try:
            # We train on all data except the last row
            X_train = X.iloc[:-1]
            y_train = y.iloc[:-1]

            # The last row is our current state we want to predict
            X_latest = X.iloc[[-1]]

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_latest_scaled = self.scaler.transform(X_latest)

            # Cross validation
            tscv = TimeSeriesSplit(n_splits=5)
            cv_scores = cross_val_score(
                self.model, X_train_scaled, y_train, cv=tscv, scoring="accuracy"
            )
            cv_accuracy = cv_scores.mean() * 100

            # Train model
            self.model.fit(X_train_scaled, y_train)
            self.is_trained = True

            # Predict probability of class 1 (positive return)
            prob = self.model.predict_proba(X_latest_scaled)[0][1]

            # Convert to percentage
            confidence_score = prob * 100

            # Get feature importances from GB and RF models
            feature_importances = {}
            for name, clf in self.model.named_estimators_.items():
                if hasattr(clf, "feature_importances_"):
                    for i, col in enumerate(feature_cols):
                        feature_importances[col] = (
                            feature_importances.get(col, 0)
                            + clf.feature_importances_[i]
                        )

            # Average the importances
            num_models_with_fi = sum(
                1
                for clf in self.model.named_estimators_.values()
                if hasattr(clf, "feature_importances_")
            )
            if num_models_with_fi > 0:
                for k in feature_importances:
                    feature_importances[k] /= num_models_with_fi

            # Sort importances
            feature_importances = dict(
                sorted(
                    feature_importances.items(), key=lambda item: item[1], reverse=True
                )
            )

            return {
                "confidence": confidence_score,
                "cv_accuracy": cv_accuracy,
                "feature_importances": feature_importances,
            }

        except Exception as e:
            logger.error(f"Error in AI Predictor: {e}")
            return {"confidence": 50.0, "cv_accuracy": 0.0, "feature_importances": {}}
