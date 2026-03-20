<div align="center">

# 🚀 Crypto Momentum Detector 📈

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen.svg)]()

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">

**A powerful CLI tool to analyze cryptocurrency momentum, calculate technical indicators, and generate actionable trading signals.**

<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjM1YzlkOGU4MjM2ZjY4ZjY4YmRjYzE2ZDZlNzY1MWRkODMwMjJjZiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/JtBZm3Getg3dqxEX1E/giphy.gif" width="400" alt="Crypto Trading Animation">

</div>

---

## ✨ Features

- 📊 **Historical Data Fetching**: Retrieves Open, High, Low, Close, and Volume data for any supported cryptocurrency pair (e.g., BTC-USD, ETH-USD) using `yfinance`.
- ⚡ **Concurrent Execution**: Analyzes multiple tickers in parallel using `ThreadPoolExecutor` for optimal performance.
- 📉 **Technical Indicators**: Calculates crucial indicators using the `ta` library:
  - 🔸 Relative Strength Index (RSI - 14 periods)
  - 🔸 Moving Average Convergence Divergence (MACD)
  - 🔸 Simple Moving Averages (SMA - 20 and 50 periods)
  - 🔸 Exponential Moving Averages (EMA - 20 and 50 periods)
  - 🔸 Average True Range (ATR - 14 periods)
  - 🔸 Bollinger Bands
- 🎯 **Signal Generation**: Evaluates indicators to output precise trading signals: `BUY`, `SELL`, `HOLD`, `STRONG BUY`, and `STRONG SELL`.
- 🛠️ **Customizable Strategies**: Adjust RSI thresholds for buying and selling signals directly from the command line.
- ⏪ **Advanced Backtesting Module**: Simulate trading based on historical signals to calculate realistic returns over a specified period, accounting for fees, slippage, max drawdown, and win rates.
- 🎨 **Rich CLI Output**: Beautifully formatted terminal tables using the `rich` library to present findings clearly, complete with progress bars, visual sparklines, portfolio summary metrics, and trading recommendations panels.
- 💾 **Parquet Caching**: Implements local Parquet file caching for robust, ultra-fast historical and MTF data loads to prevent rate limiting.
- 🛡️ **Risk Management Metrics**: Calculates and exposes ATR-based Stop Loss (SL) and Take Profit (TP) levels directly in the terminal output to make signals instantly actionable.
- 🗺️ **Multi-Timeframe Analysis (MTF)**: Validates generated signals against higher timeframe trend directions for confirmation.
- 📝 **Data Export**: Export your momentum analysis, risk metrics, and backtesting results to a CSV file for tracking and further analysis.

---

## 🛠️ Installation

Ensure you have Python 3.8+ installed.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/PelleNybe/crypto-momentum-detector.git
   cd crypto-momentum-detector
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

Run the CLI tool using `main.py`. You can specify the tickers, historical data period, data interval, and an export path.

### 🟢 Basic Usage

Analyze the default tickers (BTC-USD, ETH-USD) with default settings (6 months period, 1 day interval):

```bash
python main.py
```

### 🟠 Advanced Usage

Specify your own tickers, timeframe, and export the results to a CSV file, utilizing MTF analysis:

```bash
python main.py --tickers SOL-USD ADA-USD DOT-USD --period 1y --interval 1wk --use-mtf --export signals.csv
```

### 🟣 Backtesting and Custom Strategies

Run a backtest on historical data to see how the strategy would have performed, and tweak parameters:

```bash
python main.py --backtest --period 1y --rsi-buy-min 35 --rsi-strong-buy 25
```

---

## ⚙️ Configuration & Arguments

<details>
<summary><b>Click to expand available arguments</b></summary>
<br>

- `--tickers`: A space-separated list of cryptocurrency symbols (e.g., `BTC-USD`, `XRP-USD`).
- `--period`: The duration of historical data to analyze (e.g., `1mo`, `3mo`, `6mo`, `1y`).
- `--interval`: The timeframe interval between data points (e.g., `1h`, `1d`, `1wk`).
- `--export`: File path to export the results as CSV (e.g., `results.csv`).
- `--backtest`: Runs a historical backtest and displays detailed performance metrics.
- `--use-mtf`: Enables Multi-Timeframe analysis to confirm signals against higher timeframes.
- `--rsi-buy-min`: Minimum RSI for a regular buy signal (Default: 40).
- `--rsi-buy-max`: Maximum RSI for a regular buy signal (Default: 70).
- `--rsi-sell-min`: Minimum RSI for a regular sell signal (Default: 30).
- `--rsi-sell-max`: Maximum RSI for a regular sell signal (Default: 60).
- `--rsi-strong-buy`: RSI threshold for a strong buy signal (Default: 30).
- `--rsi-strong-sell`: RSI threshold for a strong sell signal (Default: 70).

</details>

---

## 🧠 Strategy Logic Overview

<details>
<summary><b>Click to dive into the trading logic</b></summary>
<br>

- **📈 Bullish / Buy**: RSI is in an uptrend (default 40-70), MACD is above its signal line, closing price is above the 20 EMA, and (if `--use-mtf` is active) the higher timeframe trend is bullish.
- **📉 Bearish / Sell**: RSI is in a downtrend (default 30-60), MACD is below its signal line, closing price is below the 20 EMA, and (if `--use-mtf` is active) the higher timeframe trend is bearish.
- **💥 Strong Signals**: Extreme overbought (default RSI > 70) or oversold (default RSI < 30) conditions combined with MACD reversals generate strong buy/sell signals.
- **🛡️ Risk Management**: Take Profit and Stop Loss figures are scaled based on the Average True Range (ATR) relative to the closing price, providing a dynamic risk profile for every generated setup.

</details>

---

## 🧪 Testing

This project uses `pytest` for unit testing. To run the tests, execute:

```bash
python -m pytest tests/
```

---

## 📝 License

See the `LICENSE` file for details.

<div align="center">
  <img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%">
  <p><i>Made with ❤️ by the Crypto Momentum Detector Team</i></p>
</div>
