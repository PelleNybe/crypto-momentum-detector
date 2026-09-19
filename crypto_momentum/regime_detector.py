import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    def __init__(self, data: pd.DataFrame, n_components: int = 3):
        self.data = data.copy()
        self.n_components = n_components
        self.model = GaussianMixture(
            n_components=n_components, covariance_type="full", random_state=42
        )
        self.scaler = StandardScaler()

    def _prepare_features(self) -> pd.DataFrame:
        df = self.data.copy()

        # We need sufficient data
        if len(df) < 30:
            return pd.DataFrame()

        # Feature 1: Returns
        df["Return"] = df["Close"].pct_change()

        # Feature 2: Volatility (Rolling standard deviation of returns)
        df["Volatility"] = df["Return"].rolling(window=14).std()

        # Feature 3: Volume Trend (Relative volume)
        if "Volume" in df.columns:
            df["Volume_MA"] = df["Volume"].rolling(window=14).mean()
            df["Relative_Volume"] = df["Volume"] / df["Volume_MA"]
        else:
            df["Relative_Volume"] = 1.0

        # Drop NaNs created by rolling windows
        df = df.dropna(subset=["Return", "Volatility", "Relative_Volume"])

        return df

    def _label_regimes(self, df: pd.DataFrame) -> dict:
        """
        Maps abstract cluster IDs (0, 1, 2) to human-readable names based on their statistical properties.
        """
        cluster_stats = df.groupby("Cluster").agg(
            mean_return=("Return", "mean"), mean_volatility=("Volatility", "mean")
        )

        # Sort by return to identify bear/bull
        sorted_by_return = cluster_stats.sort_values(by="mean_return")

        bear_cluster = sorted_by_return.index[0]
        bull_cluster = sorted_by_return.index[-1]

        # Find the remaining cluster (likely chop/ranging)
        remaining_clusters = [
            c for c in cluster_stats.index if c not in (bear_cluster, bull_cluster)
        ]
        chop_cluster = remaining_clusters[0] if remaining_clusters else bear_cluster

        # Refine labels based on volatility
        labels = {}
        for cluster in cluster_stats.index:
            vol = cluster_stats.loc[cluster, "mean_volatility"]
            overall_median_vol = df["Volatility"].median()
            vol_label = (
                "High Volatility" if vol > overall_median_vol else "Low Volatility"
            )

            if cluster == bull_cluster:
                labels[cluster] = f"{vol_label} Bull"
            elif cluster == bear_cluster:
                labels[cluster] = f"{vol_label} Bear"
            else:
                labels[cluster] = f"{vol_label} Chop"

        return labels

    def detect_regimes(self) -> pd.DataFrame:
        feature_df = self._prepare_features()

        if feature_df.empty:
            # Fallback if not enough data
            self.data["AI_Regime"] = "Unknown"
            self.data["AI_Regime_Encoded"] = -1
            return self.data

        features = ["Return", "Volatility", "Relative_Volume"]
        X = feature_df[features].values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Fit and predict
        try:
            self.model.fit(X_scaled)
            clusters = self.model.predict(X_scaled)
            feature_df["Cluster"] = clusters

            # Map to human labels
            label_mapping = self._label_regimes(feature_df)
            feature_df["AI_Regime"] = feature_df["Cluster"].map(label_mapping)

            # Realign with original dataframe index
            # We want to fill the initial rows that were dropped by rolling windows with the first known regime
            self.data["AI_Regime"] = feature_df["AI_Regime"]
            self.data["AI_Regime"] = self.data["AI_Regime"].bfill().fillna("Unknown")

            self.data["AI_Regime_Encoded"] = feature_df["Cluster"]
            self.data["AI_Regime_Encoded"] = (
                self.data["AI_Regime_Encoded"].bfill().fillna(-1)
            )

        except Exception as e:
            logger.error(f"Error in Market Regime Detection: {e}")
            self.data["AI_Regime"] = "Unknown"
            self.data["AI_Regime_Encoded"] = -1

        return self.data
