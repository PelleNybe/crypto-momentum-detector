import re

with open("crypto_momentum/data_fetcher.py", "r") as f:
    content = f.read()

# Define the new method
new_method = """    def clean_outliers(
        self, df: pd.DataFrame, window: int = 20, num_std: float = 4.0
    ) -> pd.DataFrame:
        \"\"\"Removes significant outliers from the price data using a rolling z-score and interpolates them.
        Optimized: Vectorized calculation across all price columns to eliminate the python loop.\"\"\"
        if df.empty or len(df) < window:
            return df

        import numpy as np

        df_clean = df.copy()
        cols_to_clean = [col for col in ["Open", "High", "Low", "Close"] if col in df_clean.columns]

        if not cols_to_clean:
            return df_clean

        # Vectorized rolling window calculations across all columns
        rolling_mean = df_clean[cols_to_clean].rolling(window=window, min_periods=1, center=True).mean()
        rolling_std = df_clean[cols_to_clean].rolling(window=window, min_periods=1, center=True).std()

        # For the first few rows where std is 0 or NaN, fill with overall std for each column
        overall_std = df_clean[cols_to_clean].std()
        rolling_std = rolling_std.bfill().fillna(overall_std)

        z_scores = np.abs((df_clean[cols_to_clean] - rolling_mean) / (rolling_std + 1e-9))

        # Create mask and replace outliers with NaN
        outlier_mask = z_scores > num_std
        if outlier_mask.to_numpy().any():
            # .mask() replaces values where the condition is True with NaN
            df_clean[cols_to_clean] = df_clean[cols_to_clean].mask(outlier_mask)
            df_clean[cols_to_clean] = df_clean[cols_to_clean].interpolate(
                method="linear", limit_direction="both"
            )

        return df_clean"""

# Replace old method with regex
pattern = r"    def clean_outliers\(.*?return df_clean"
replaced = re.sub(pattern, new_method, content, flags=re.DOTALL)

with open("crypto_momentum/data_fetcher.py", "w") as f:
    f.write(replaced)

print("Patched data_fetcher.py")
