import re

with open('README.md', 'r') as f:
    content = f.read()

new_features = """
## 🚀 New World-Class Features

### Technical Improvements:
1.  **📊 Advanced Outlier Detection**: Implementation of robust z-score based outlier detection and linear interpolation during data fetch ensuring indicator calculations are not skewed by price spikes (T5).
2.  **🧠 Gradient Boosting Ensemble Machine Learning**: The AI Predictive Engine now uses a `VotingClassifier` (Gradient Boosting, Random Forest, Logistic Regression) to vote on probability of positive return (T3).
3.  **📈 Time Series Cross-Validation**: Added `TimeSeriesSplit` cross-validation for a reliable historical ML model accuracy metric (T4).
4.  **🛡️ Realistic Backtesting Execution**: Backtester logic updated to incorporate proper Stop Loss and Take Profit evaluation natively checking daily highs and lows. (T1)
5.  **⚡ ATR Volatility-based Position Sizing**: Replaced flat % sizing with dynamic position sizing that scales based on trade risk and asset volatility. (T2)

### Visual Improvements:
1.  **📊 Feature Importance Dashboard (V1)**: The Streamlit UI now includes a Plotly Horizontal Bar chart showing exactly which metrics the AI model relied upon.
2.  **🧠 AI Confidence Gauge (V2)**: A Plotly Interactive Gauge chart visually mapping model confidence metrics in Streamlit.
3.  **📈 Equity Curve Visualization (V3)**: Added a plotted line-chart showing capital progression over time during backtests.
4.  **🛡️ Animated Terminal View (V4)**: Converted the static CLI table dump into a real-time updating dashboard using `rich.live`.
5.  **⚡ Interactive Trade Log (V5)**: Appended an interactive Pandas DataFrame rendering via `st.dataframe` to allow granular trade-by-trade inspection.

![Terminal Output](docs/assets/ui_default.svg)
"""

content = re.sub(r'## 🚀 New World-Class Features.*?!\[Terminal Output\]\(docs/assets/ui_default\.svg\)', new_features.strip(), content, flags=re.DOTALL)

with open('README.md', 'w') as f:
    f.write(content)
