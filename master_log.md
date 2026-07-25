
## 2024-07-25 - [Performance Optimizations]
**Learning:** Found several performance bottlenecks in Python processing involving explicit `for` loops in pandas/numpy calculations.
**Action:**
1. Optimized `calculate_vpvr` (Volume Profile) by replacing the python loop with vectorized `np.bincount`, resulting in a ~380x speedup.
2. Optimized Monte Carlo simulations in `backtester.py` by replacing a nested for loop over simulated paths with a fully vectorized approach using `numpy` 2D arrays, `np.cumprod`, and `np.maximum.accumulate`, resulting in a ~6x speedup.
3. Optimized the core backtesting signal evaluation loop by replacing `df.iterrows()` with `df.itertuples()`, yielding a ~14x speedup in evaluation logic.
## 2024-07-25 - [Streamlit Caching & ML Threading Optimization]
**Learning:** Found that `process_ticker` inside `app.py` was recalculating data on every interaction, and `RandomForestClassifier` was single-threaded.
**Action:**
1. Extracted `process_ticker` out of `if analyze_button:` and decorated it with `@st.cache_data(ttl=3600, show_spinner=False)` to prevent duplicate API calls and identical model retraining.
2. Added `n_jobs=-1` to `RandomForestClassifier` inside `ai_predictor.py` to allow multi-threaded parallel model generation during predictions.
