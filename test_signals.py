from crypto_momentum.signal_generator import SignalGenerator
import pandas as pd
import numpy as np

def run_test():
    np.random.seed(42)
    df = pd.DataFrame({
        "RSI_14": np.random.uniform(20, 80, 100),
        "MACD": np.random.uniform(-1, 1, 100),
        "MACD_Signal": np.random.uniform(-1, 1, 100),
        "SMA_20": np.random.uniform(40, 60, 100),
        "SMA_50": np.random.uniform(40, 60, 100),
        "EMA_20": np.random.uniform(40, 60, 100),
        "EMA_50": np.random.uniform(40, 60, 100),
        "ATR_14": np.random.uniform(1, 5, 100),
        "Close": np.random.uniform(40, 60, 100),
        "BB_High": np.random.uniform(50, 70, 100),
        "BB_Low": np.random.uniform(30, 50, 100)
    })

    gen = SignalGenerator(df)
    res = gen.generate_signals()
    print(res["Signal"].value_counts())
run_test()
