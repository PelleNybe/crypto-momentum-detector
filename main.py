import argparse
import sys
import concurrent.futures
import csv
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

from crypto_momentum.data_fetcher import DataFetcher
from crypto_momentum.indicators import MomentumIndicators
from crypto_momentum.signal_generator import SignalGenerator
from crypto_momentum.backtester import Backtester

console = Console()

def process_ticker(ticker, period, interval, backtest=False, strategy_params=None):
    try:
        fetcher = DataFetcher(ticker_symbol=ticker)
        data = fetcher.fetch_historical_data(period=period, interval=interval)

        if data.empty:
            return {"ticker": ticker, "status": "No Data", "error": True}

        indicators = MomentumIndicators(data)
        df_indicators = indicators.calculate_all()


        if strategy_params is None:
            strategy_params = {}
        generator = SignalGenerator(df_indicators, **strategy_params)
        latest = generator.get_latest_signal()

        if not latest:
            return {"ticker": ticker, "status": "Insufficient Data", "error": True}

        latest["ticker"] = ticker
        latest["error"] = False

        if backtest:
            df_with_signals = generator.generate_signals()
            bt = Backtester(df_with_signals)
            bt_results = bt.run()
            latest["backtest"] = bt_results

        return latest

    except Exception as e:
        return {"ticker": ticker, "status": f"Error: {e}", "error": True}

def main():
    parser = argparse.ArgumentParser(description="Crypto Momentum Detector CLI")
    parser.add_argument(
        "--tickers",
        type=str,
        nargs="+",
        default=["BTC-USD", "ETH-USD"],
        help="List of cryptocurrency tickers to analyze (e.g., BTC-USD ETH-USD)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="6mo",
        help="Historical data period to fetch (e.g., 1mo, 3mo, 6mo, 1y)"
    )
    parser.add_argument(
        "--interval",
        type=str,
        default="1d",
        help="Interval of historical data (e.g., 1h, 1d, 1wk)"
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="File path to export the results as CSV (e.g., results.csv)"
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run a backtest on historical data and show performance"
    )

    # Strategy parameters
    parser.add_argument("--rsi-buy-min", type=int, default=40, help="Minimum RSI for regular buy")
    parser.add_argument("--rsi-buy-max", type=int, default=70, help="Maximum RSI for regular buy")
    parser.add_argument("--rsi-sell-min", type=int, default=30, help="Minimum RSI for regular sell")
    parser.add_argument("--rsi-sell-max", type=int, default=60, help="Maximum RSI for regular sell")
    parser.add_argument("--rsi-strong-buy", type=int, default=30, help="RSI threshold for strong buy")
    parser.add_argument("--rsi-strong-sell", type=int, default=70, help="RSI threshold for strong sell")

    args = parser.parse_args()
    tickers = args.tickers
    period = args.period
    interval = args.interval
    export_path = args.export
    backtest = args.backtest

    strategy_params = {
        'rsi_buy_min': args.rsi_buy_min,
        'rsi_buy_max': args.rsi_buy_max,
        'rsi_sell_min': args.rsi_sell_min,
        'rsi_sell_max': args.rsi_sell_max,
        'rsi_strong_buy': args.rsi_strong_buy,
        'rsi_strong_sell': args.rsi_strong_sell
    }

    console.print(Panel.fit(
        f"[bold blue]Crypto Momentum Detector[/bold blue]\n"
        f"Analyzing: {', '.join(tickers)}\n"
        f"Period: {period} | Interval: {interval}",
        title="Settings", border_style="blue"
    ))

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="dim", width=12)
    table.add_column("Date", justify="center")
    table.add_column("Price (USD)", justify="right")
    table.add_column("RSI (14)", justify="right")
    table.add_column("MACD", justify="right")
    table.add_column("BB (L-H)", justify="center")
    table.add_column("Signal", justify="center")
    if backtest:
        table.add_column("BT Return %", justify="right")

    results = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_ticker, ticker, period, interval, backtest, strategy_params): ticker for ticker in tickers}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Sort results by ticker to maintain a predictable order
    results.sort(key=lambda x: x['ticker'])

    export_data = []

    for result in results:
        ticker = result['ticker']
        if result['error']:
            if backtest:
                table.add_row(ticker, result['status'], "-", "-", "-", "-", "[red]ERROR[/red]", "-")
            else:
                table.add_row(ticker, result['status'], "-", "-", "-", "-", "[red]ERROR[/red]")
            row_data = {
                "Ticker": ticker,
                "Date": result['status'],
                "Price (USD)": "-",
                "RSI (14)": "-",
                "MACD": "-",
                "BB_Low": "-",
                "BB_High": "-",
                "Signal": "ERROR"
            }
            if backtest:
                row_data["BT_Return_Pct"] = "-"
            export_data.append(row_data)
        else:
            latest = result
            rsi = latest['RSI']
            rsi_color = "green" if rsi < 30 else "red" if rsi > 70 else "white"
            rsi_str = f"[{rsi_color}]{rsi:.2f}[/{rsi_color}]"

            macd_diff = latest['MACD'] - latest['MACD_Signal']
            macd_color = "green" if macd_diff > 0 else "red"
            macd_str = f"[{macd_color}]{latest['MACD']:.2f}[/{macd_color}]"

            signal = latest['Action']
            if "BUY" in signal:
                signal_color = "bold green"
            elif "SELL" in signal:
                signal_color = "bold red"
            else:
                signal_color = "bold yellow"
            signal_str = f"[{signal_color}]{signal}[/{signal_color}]"

            if backtest:
                bt_return = latest['backtest'].get('Return %', 0)
                bt_color = "green" if bt_return > 0 else "red"
                bt_str = f"[{bt_color}]{bt_return:.2f}%[/{bt_color}]"
                table.add_row(
                    ticker,
                    latest['Date'],
                    f"${latest['Price']:.2f}",
                    rsi_str,
                    macd_str,
                    f"${latest['BB_Low']:.0f} - ${latest['BB_High']:.0f}",
                    signal_str,
                    bt_str
                )
            else:
                table.add_row(
                    ticker,
                    latest['Date'],
                    f"${latest['Price']:.2f}",
                    rsi_str,
                    macd_str,
                    f"${latest['BB_Low']:.0f} - ${latest['BB_High']:.0f}",
                    signal_str
                )

            row_data = {
                "Ticker": ticker,
                "Date": latest['Date'],
                "Price (USD)": f"{latest['Price']:.2f}",
                "RSI (14)": f"{rsi:.2f}",
                "MACD": f"{latest['MACD']:.2f}",
                "BB_Low": f"{latest['BB_Low']:.2f}",
                "BB_High": f"{latest['BB_High']:.2f}",
                "Signal": signal
            }
            if backtest:
                row_data["BT_Return_Pct"] = f"{latest['backtest'].get('Return %', 0):.2f}%"
            export_data.append(row_data)

    console.print(table)

    if export_path:
        try:
            with open(export_path, 'w', newline='') as csvfile:
                fieldnames = ["Ticker", "Date", "Price (USD)", "RSI (14)", "MACD", "BB_Low", "BB_High", "Signal"]
                if backtest:
                    fieldnames.append("BT_Return_Pct")
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in export_data:
                    writer.writerow(row)
            console.print(f"[green]Results successfully exported to {export_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error exporting results to {export_path}: {e}[/red]")

if __name__ == "__main__":
    main()
