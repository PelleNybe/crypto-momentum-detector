
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
## 2026-07-25 - [Threading and Data Fetching Optimizations]
**Learning:** Found AI Predictor to be slow due to single-threaded execution, and concurrent fetching in process_ticker was only across tickers, not per ticker.
**Action:**
1. Changed n_jobs=-1 in VotingClassifier and cross_val_score inside ai_predictor.py.
2. Reduced n_splits from 5 to 3 in TimeSeriesSplit.
3. Implemented ThreadPoolExecutor inside process_ticker (main.py and app.py) for concurrent historical and HTF data fetching.

## 2024-07-25 - [App.py Multithreading UI]
**Learning:** Found that `process_ticker_cached` in `app.py` is being run sequentially or partly concurrently, but `concurrent.futures.ThreadPoolExecutor` was already somewhat implemented at line 250 in `app.py`.
## 2024-07-25 - [App.py concurrent tickers bug]
**Learning:** In `app.py`, `ThreadPoolExecutor` is being used, but `futures` iterates through `for future in futures` which is a dictionary loop on futures and accesses `future.result()` in the loop synchronously in creation order rather than completion order. We should use `concurrent.futures.as_completed(futures)` for true parallel UI updating and speed. Same for `main.py`.
## 2024-07-25 - [App.py Streamlit execution improvement]
**Learning:** SignalGenerator in `crypto_momentum/signal_generator.py` looks clean and uses fully vectorized pandas operations to determine Buy/Sell zones (loc and boolean masks). No optimization needed here as it is O(1) in pandas context.
## 2024-07-25 - [ai_predictor.py optimization]
**Learning:** `ai_predictor.py` uses `VotingClassifier` with Grid/Random forest, scaled and trained dynamically per ticker. The data pre-processing is vectorized using pandas, but doing this across tickers scales O(n_tickers). The use of `n_jobs=-1` on Random Forest and `VotingClassifier` runs parallel ML model builds per ticker. Since this runs inside `ThreadPoolExecutor`, we have thread contention (Thread Pool runs `n_tickers` workers, and each worker runs `n_cpu` threads).
**Action:** Restrict `n_jobs=1` inside the ML models to avoid thread contention context switching overhead, since the primary parallelism comes from ticker distribution.
## 2024-07-25 - [backtester.py performance]
**Learning:** `backtester.py` simulates trade by trade logic and does not currently vectorise equity curve tracking since decisions rely on previous state variables. Given it uses `itertuples`, it's relatively well optimized for Python iteration. `itertuples()` is generally 10x-20x faster than `iterrows()`. Monte Carlo was already fully vectorized. We can consider it optimized.

## 2024-07-25 - [Performance Optimizations]
**Learning:** Found several performance bottlenecks in Python processing involving explicit `for` loops and heavy lookups.
**Action:**
1. Optimized `clean_outliers` in `crypto_momentum/data_fetcher.py` by replacing a per-column loop with vectorized calculations across all price columns, avoiding Python iteration entirely.
2. Optimized the core backtesting signal evaluation loop (`crypto_momentum/backtester.py`) by pre-checking column existence and using native attribute access via `itertuples()` to avoid the slow `getattr()` inside the hot loop.
3. Optimized feature importance calculation in `ai_predictor.py` by vectorized addition of feature importances and truncating the dictionary to the top 5, avoiding sorting massive UI bloat arrays and doing it manually in Python loops.
