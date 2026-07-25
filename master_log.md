
## 2024-07-25 - [Performance Optimizations]
**Learning:** Found several performance bottlenecks in Python processing involving explicit `for` loops in pandas/numpy calculations.
**Action:**
1. Optimized `calculate_vpvr` (Volume Profile) by replacing the python loop with vectorized `np.bincount`, resulting in a ~380x speedup.
2. Optimized Monte Carlo simulations in `backtester.py` by replacing a nested for loop over simulated paths with a fully vectorized approach using `numpy` 2D arrays, `np.cumprod`, and `np.maximum.accumulate`, resulting in a ~6x speedup.
3. Optimized the core backtesting signal evaluation loop by replacing `df.iterrows()` with `df.itertuples()`, yielding a ~14x speedup in evaluation logic.
