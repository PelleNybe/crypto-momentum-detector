import pandas as pd
import numpy as np


def clean_outliers(
    df: pd.DataFrame, window: int = 20, num_std: float = 4.0
) -> pd.DataFrame:
    """Removes significant outliers from the price data using a rolling z-score and interpolates them."""
    if df.empty or len(df) < window:
        return df

    df_clean = df.copy()
    for col in ["Open", "High", "Low", "Close"]:
        if col in df_clean.columns:
            rolling_mean = (
                df_clean[col].rolling(window=window, min_periods=1, center=True).mean()
            )
            rolling_std = (
                df_clean[col].rolling(window=window, min_periods=1, center=True).std()
            )

            # For the first few rows where std is 0 or NaN, fill with overall std
            rolling_std = rolling_std.bfill().fillna(df_clean[col].std())

            z_scores = np.abs((df_clean[col] - rolling_mean) / (rolling_std + 1e-9))

            # Mask outliers
            outlier_mask = z_scores > num_std
            if outlier_mask.any():
                df_clean.loc[outlier_mask, col] = np.nan
                df_clean[col] = df_clean[col].interpolate(
                    method="linear", limit_direction="both"
                )

    return df_clean
