import time
import pandas as pd
import numpy as np
from crypto_momentum.data_fetcher import DataFetcher

# Create dummy data
df = pd.DataFrame({
    "Open": np.random.normal(100, 10, 10000),
    "High": np.random.normal(105, 10, 10000),
    "Low": np.random.normal(95, 10, 10000),
    "Close": np.random.normal(102, 10, 10000)
})

# Insert some outliers
df.loc[100, "Close"] = 500
df.loc[200, "High"] = 10

fetcher = DataFetcher(cache_dir=".test_cache")

start_time = time.time()
clean_df = fetcher.clean_outliers(df)
end_time = time.time()

print(f"Time taken: {end_time - start_time:.4f} seconds")
print(f"Cleaned df shape: {clean_df.shape}")
