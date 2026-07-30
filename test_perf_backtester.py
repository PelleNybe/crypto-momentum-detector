import time
import pandas as pd
import numpy as np
from crypto_momentum.backtester import Backtester

# Create dummy data
np.random.seed(42)
df = pd.DataFrame({
    "Open": np.random.normal(100, 10, 10000),
    "High": np.random.normal(105, 10, 10000),
    "Low": np.random.normal(95, 10, 10000),
    "Close": np.random.normal(102, 10, 10000),
    "Signal": np.random.choice(["BUY", "SELL", "HOLD", "STRONG BUY", "STRONG SELL"], 10000, p=[0.05, 0.05, 0.88, 0.01, 0.01]),
    "Stop_Loss": np.random.normal(90, 5, 10000),
    "Take_Profit": np.random.normal(110, 5, 10000)
}, index=pd.date_range("2020-01-01", periods=10000, freq="h"))

tester = Backtester(df)

start_time = time.time()
res = tester.run()
end_time = time.time()

print(f"Time taken: {end_time - start_time:.4f} seconds")
