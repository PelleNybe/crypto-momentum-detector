<div align="center">

# ⚡ NeonPulse: Advanced AI Crypto Trading Terminal

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=600&size=24&pause=1000&color=00FFFF&center=true&vCenter=true&width=800&lines=Welcome+to+the+Future+of+Algorithmic+Trading;AI-Powered+Momentum+Detection;Advanced+Monte+Carlo+Simulations;Institutional-Grade+Backtesting;Beautiful+Cyberpunk+Aesthetics" alt="Typing SVG" /></a>

<br/>

[![Tests](https://img.shields.io/github/actions/workflow/status/PelleNybe/crypto-momentum-detector/tests.yml?branch=main&label=tests&style=for-the-badge&logo=github&color=blue)](https://github.com/PelleNybe/crypto-momentum-detector/actions)
[![Python Version](https://img.shields.io/pypi/pyversions/crypto-momentum-detector.svg?style=for-the-badge&logo=python&logoColor=white&color=blue)](https://pypi.org/project/crypto-momentum-detector/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Issues](https://img.shields.io/github/issues/PelleNybe/crypto-momentum-detector.svg?style=for-the-badge&logo=github&color=red)](https://github.com/PelleNybe/crypto-momentum-detector/issues)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge&logo=github)](http://makeapullrequest.com)
[![Streamlit](https://img.shields.io/badge/Built_with-Streamlit-FF4B4B.svg?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io/)
[![Powered by AI](https://img.shields.io/badge/Powered_by-AI-purple.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)]()

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

<br/>

<h2><b>⚡ A world-class, AI-powered application to analyze cryptocurrency momentum, run Monte Carlo simulations, and generate actionable trading signals with a jaw-dropping UI! ⚡</b></h2>

<br/>

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjM1YzlkOGU4MjM2ZjY4ZjY4YmRjYzE2ZDZlNzY1MWRkODMwMjJjZiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/JtBZm3Getg3dqxEX1E/giphy.gif" width="600" alt="Crypto Trading Animation" style="border-radius: 15px; box-shadow: 0 8px 16px rgba(0,0,0,0.5); border: 2px solid #00FFFF;">

</div>

<br/>

## 🌟 Discover the Future of Algorithmic Trading

Welcome to the **NeonPulse AI Crypto Terminal**. Built for elite traders, quants, and crypto enthusiasts who demand **speed**, **machine learning precision**, and **beautiful aesthetics**.

Whether you're a day trader hunting for quick setups or a quant researching strategies, this tool equips you with state-of-the-art analysis so you can execute with absolute confidence.

---

## 🚀 Key Features & Capabilities

<details>
<summary><b>🛠️ Performance Improvements (Click to expand)</b></summary>
<br>

1.  **🚀 Vectorized Volume Profile (VPVR)**: Replaced iterative DataFrame looping with `numpy.bincount` for ~380x faster volume profile calculation.
2.  **⚡ Optimized Monte Carlo Engine**: Switched Monte Carlo backtesting from sequential loops to fully vectorized NumPy matrix operations resulting in a ~6x speedup, and optimized random sampling using integer indexing.
3.  **🏎️ Faster Backtest Execution**: Changed Pandas `iterrows` to `itertuples` in the core backtester loop, dramatically reducing overhead by ~14x.
4.  **📉 Memory Efficient ML**: AI Predictor now uses `float32` numpy arrays for feature processing, significantly reducing memory footprint.
5.  **🚀 Vectorized Signal Generator**: Replaced `.loc` index assignments with lightning-fast `np.where` for Stop Loss and Take Profit calculations.
</details>

<details>
<summary><b>🧠 Technical & AI Advancements (Click to expand)</b></summary>
<br>

1.  **📊 Advanced Outlier Detection**: Implementation of robust z-score based outlier detection and linear interpolation during data fetch ensuring indicator calculations are not skewed by price spikes.
2.  **🧠 Gradient Boosting Ensemble Machine Learning**: The AI Predictive Engine now uses a `VotingClassifier` (Gradient Boosting, Random Forest, Logistic Regression) to vote on probability of positive return.
3.  **🔒 Secure Data Caching**: Cached Parquet data files now enforce strict `0o600` POSIX permissions ensuring robust local security.
3.  **📈 Time Series Cross-Validation**: Added `TimeSeriesSplit` cross-validation for a reliable historical ML model accuracy metric.
4.  **🛡️ Realistic Backtesting Execution**: Backtester logic updated to incorporate proper Stop Loss and Take Profit evaluation natively checking daily highs and lows.
5.  **⚡ ATR Volatility-based Position Sizing**: Replaced flat % sizing with dynamic position sizing that scales based on trade risk and asset volatility.
</details>

<details>
<summary><b>🎨 Visual & UI Enhancements (Click to expand)</b></summary>
<br>

1.  **📊 Feature Importance Dashboard**: The Streamlit UI now includes a Plotly Horizontal Bar chart showing exactly which metrics the AI model relied upon.
2.  **🧠 AI Confidence Gauge**: A Plotly Interactive Gauge chart visually mapping model confidence metrics in Streamlit.
3.  **📈 Equity Curve Visualization**: Added a plotted line-chart showing capital progression over time during backtests.
4.  **🛡️ Animated Terminal View**: Converted the static CLI table dump into a real-time updating dashboard using `rich.live`.
5.  **⚡ Interactive Trade Log**: Appended an interactive Pandas DataFrame rendering via `st.dataframe` to allow granular trade-by-trade inspection.
</details>

<br/>

### 🎯 Advanced Trading Toolkit

*   **📊 On-Balance Volume (OBV) Divergence Detection**: Automatically flags critical hidden bullish and bearish divergences between price action and cumulative volume flow.
*   **🧠 Advanced Pattern Recognition Engine**: Scans rolling local extremums to instantly identify Double Top and Double Bottom formations with high precision.
*   **🛡️ Dynamic Trailing Stop Loss (Chandelier Exit)**: Maximizes profit capture by utilizing an ATR-based Chandelier Exit that scales with volatility, replacing static stops.
*   **🌐 Market Regime Filter**: Leverages ADX and DI indicators to classify the market state into "Trending Bullish", "Trending Bearish", or "Ranging", allowing for context-aware signals.
*   **⚡ Stochastic RSI Confluence**: Pinpoints exact momentum shifts using Stochastic RSI %K and %D crossovers for laser-accurate entry timing.
*   **📈 Volume Weighted Average Price (VWAP)**: A fundamental indicator used by institutional traders, displayed on the interactive candlestick chart to gauge average price matched with volume.
*   **🏆 Advanced Backtesting Metrics**: Now includes **Sharpe Ratio**, **Sortino Ratio**, and **Profit Factor**, giving you institutional-grade insights into strategy performance alongside Monte Carlo risk of ruin.

---

## 📸 System Screenshots

### 💻 Animated Terminal UI
<div align="center">
  <img src="docs/assets/ui_default.svg" width="90%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">
</div>

### 📈 Backtest & Equity Curve Analysis
<div align="center">
  <img src="docs/assets/ui_backtest.svg" width="90%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">
</div>

### 🌐 Multi-Timeframe (MTF) Dashboard
<div align="center">
  <img src="docs/assets/ui_mtf.svg" width="90%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">
</div>

### 🚀 Multiple Assets Portfolio View
<div align="center">
  <img src="docs/assets/ui_multiple.svg" width="90%" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">
</div>

---

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 🛠️ Installation

Get up and running in less than 2 minutes! Ensure you have **Python 3.8+** installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/PelleNybe/crypto-momentum-detector.git
    cd crypto-momentum-detector
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

*(Optional but highly recommended): Install caching engines for blazing fast subsequent runs:*
```bash
pip install pyarrow fastparquet
```

---

## 💻 Usage & Commands

Experience the new beautiful **Deep Tech / Cyberpunk** Streamlit UI by simply running:

```bash
streamlit run app.py
```

*Prefer the blazing-fast terminal execution? Use the robust CLI tool:*

### 🟢 Quick Start (CLI Default Run)
Analyze the default tickers (BTC-USD, ETH-USD) with default settings (6 months period, 1 day interval):
```bash
python main.py
```

### 🟠 Advanced Power User (CLI)
Specify your own basket of altcoins, set the timeframe, export the results to a CSV, and utilize MTF analysis for maximum accuracy:
```bash
python main.py --tickers SOL-USD ADA-USD DOT-USD --period 1y --interval 1wk --use-mtf --export signals.csv
```

### 🟣 AI Monte Carlo Backtesting (CLI)
Run a historical backtest through the Monte Carlo simulation engine and see detailed performance metrics including Median Return and Risk of Ruin:
```bash
python main.py --backtest --period 1y --tickers BTC-USD
```

---

## ⚙️ Configuration Glossary

<details>
<summary><b>🔥 Click to reveal all available CLI arguments 🔥</b></summary>
<br>

| Argument | Description | Example |
| :--- | :--- | :--- |
| `--tickers` | Space-separated list of cryptocurrency symbols | `--tickers BTC-USD XRP-USD SOL-USD` |
| `--period` | Historical data period to fetch (`1mo`, `3mo`, `6mo`, `1y`, `max`) | `--period 1y` |
| `--interval` | Timeframe interval between data points (`1h`, `1d`, `1wk`) | `--interval 1d` |
| `--export` | File path to export the detailed results as a CSV | `--export my_trades.csv` |
| `--backtest` | Flag to run a historical backtest and display performance | `--backtest` |
| `--save-svg` | Save the terminal output as an SVG file | `--save-svg` |
| `--use-mtf` | Flag to enable Multi-Timeframe analysis to confirm macro trends | `--use-mtf` |

</details>

---

## 🧪 Testing and Reliability

We believe in robust, production-grade code. This project uses `pytest` for unit testing, including mocked API responses to ensure the logic remains sound without hitting external rate limits.

```bash
# Run the test suite
python -m pytest tests/
```

---

<br/>

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 👨‍💻 Meet the Developer & The Company

<div align="center">

### **Pelle Nyberg**
*Visionary Software Engineer & Quantitative Developer*

[![GitHub Badge](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/PelleNybe)
[![LinkedIn Badge](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/pellenyberg/)
[![Website Badge](https://img.shields.io/badge/Portfolio-000000?style=for-the-badge&logo=About.me&logoColor=white)](https://pellenybe.github.io)
[![Project](https://img.shields.io/badge/Crypto_Project-FF9900?style=for-the-badge&logo=bitcoin&logoColor=white)](https://cryptop.coraxcolab.com)

With a deep passion for financial markets, algorithmic trading, and cutting-edge software architecture, Pelle bridges the gap between complex quantitative analysis and beautifully engineered, user-centric tools.

<br/>
<br/>

<img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Briefcase.png" alt="Briefcase" width="60" height="60" />

### **Corax CoLAB**
*Innovating the Future of Digital Solutions*

[![Website Badge](https://img.shields.io/badge/Corax_CoLAB-1E1E1E?style=for-the-badge&logo=React&logoColor=61DAFB)](https://coraxcolab.com)

At **Corax CoLAB**, we build scalable, high-performance software solutions. From robust trading algorithms and data pipelines to full-stack web applications, Corax CoLAB is dedicated to pushing the boundaries of what technology can achieve. Visit us to see how we are shaping the future.

</div>

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
</div>

## 📜 License

This project is open-sourced software licensed under the **[MIT License](LICENSE)**.

<br/>

<div align="center">
  <i>"In trading, vision is everything. In development, execution is everything."</i><br/>
  <b>Made with <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Smilies/Beating%20Heart.png" alt="Beating Heart" width="20" height="20" /> by Pelle Nyberg @ Corax CoLAB</b>
</div>
