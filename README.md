# Crypto Momentum Detector

Crypto Momentum Detector is a command-line interface (CLI) tool designed to analyze the momentum of cryptocurrencies. It fetches historical data using Yahoo Finance, calculates key technical indicators, and generates actionable trading signals based on predefined or customizable momentum strategies. It also features a backtesting engine to evaluate strategy performance over time.

## Features

- **Historical Data Fetching**: Retrieves Open, High, Low, Close, and Volume data for any supported cryptocurrency pair (e.g., BTC-USD, ETH-USD) using `yfinance`.
- **Concurrent Execution**: Analyzes multiple tickers in parallel using `ThreadPoolExecutor` for optimal performance.
- **Technical Indicators**: Calculates crucial indicators using the `ta` library:
  - Relative Strength Index (RSI - 14 periods)
  - Moving Average Convergence Divergence (MACD)
  - Simple Moving Averages (SMA - 20 and 50 periods)
  - Exponential Moving Averages (EMA - 20 and 50 periods)
  - Average True Range (ATR - 14 periods)
  - Bollinger Bands
- **Signal Generation**: Evaluates indicators to output precise trading signals: `BUY`, `SELL`, `HOLD`, `STRONG BUY`, and `STRONG SELL`.
- **Customizable Strategies**: Adjust RSI thresholds for buying and selling signals directly from the command line.
- **Backtesting Module**: Simulate trading based on historical signals to calculate theoretical returns over a specified period.
- **Rich CLI Output**: Beautifully formatted terminal tables using the `rich` library to present findings clearly.
- **Data Export**: Export your momentum analysis and backtesting results to a CSV file for tracking and further analysis.

## Installation

Ensure you have Python 3.8+ installed.

1. Clone the repository:
   ```bash
   git clone https://github.com/PelleNybe/crypto-momentum-detector.git
   cd crypto-momentum-detector
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the CLI tool using `main.py`. You can specify the tickers, historical data period, data interval, and an export path.

### Basic Usage

Analyze the default tickers (BTC-USD, ETH-USD) with default settings (6 months period, 1 day interval):

```bash
python main.py
```

### Advanced Usage

Specify your own tickers, timeframe, and export the results to a CSV file:

```bash
python main.py --tickers SOL-USD ADA-USD DOT-USD --period 1y --interval 1wk --export signals.csv
```

### Backtesting and Custom Strategies

Run a backtest on historical data and tweak the strategy parameters:

```bash
python main.py --backtest --period 1y --rsi-buy-min 35 --rsi-strong-buy 25
```

### Arguments

- `--tickers`: A space-separated list of cryptocurrency symbols (e.g., `BTC-USD`, `XRP-USD`).
- `--period`: The duration of historical data to analyze (e.g., `1mo`, `3mo`, `6mo`, `1y`).
- `--interval`: The timeframe interval between data points (e.g., `1h`, `1d`, `1wk`).
- `--export`: File path to export the results as CSV (e.g., `results.csv`).
- `--backtest`: Runs a historical backtest and displays performance metrics.
- `--rsi-buy-min`: Minimum RSI for a regular buy signal (Default: 40).
- `--rsi-buy-max`: Maximum RSI for a regular buy signal (Default: 70).
- `--rsi-sell-min`: Minimum RSI for a regular sell signal (Default: 30).
- `--rsi-sell-max`: Maximum RSI for a regular sell signal (Default: 60).
- `--rsi-strong-buy`: RSI threshold for a strong buy signal (Default: 30).
- `--rsi-strong-sell`: RSI threshold for a strong sell signal (Default: 70).

## Testing

This project uses `pytest` for unit testing. To run the tests, execute:

```bash
python -m pytest tests/
```

## Strategy Logic Overview

- **Bullish / Buy**: RSI is in an uptrend (default 40-70), MACD is above its signal line, and the closing price is above the 20 EMA.
- **Bearish / Sell**: RSI is in a downtrend (default 30-60), MACD is below its signal line, and the closing price is below the 20 EMA.
- **Strong Signals**: Extreme overbought (default RSI > 70) or oversold (default RSI < 30) conditions combined with MACD reversals generate strong buy/sell signals.

## License

See the `LICENSE` file for details.
