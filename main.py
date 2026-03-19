import argparse
import sys
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

from crypto_momentum.data_fetcher import DataFetcher
from crypto_momentum.indicators import MomentumIndicators
from crypto_momentum.signal_generator import SignalGenerator

console = Console()

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

    args = parser.parse_args()
    tickers = args.tickers
    period = args.period
    interval = args.interval

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

    for ticker in tickers:
        try:
            fetcher = DataFetcher(ticker_symbol=ticker)
            data = fetcher.fetch_historical_data(period=period, interval=interval)

            if data.empty:
                table.add_row(ticker, "No Data", "-", "-", "-", "[red]ERROR[/red]")
                continue

            indicators = MomentumIndicators(data)
            df_indicators = indicators.calculate_all()

            generator = SignalGenerator(df_indicators)
            latest = generator.get_latest_signal()

            if not latest:
                table.add_row(ticker, "Insufficient Data", "-", "-", "-", "[red]ERROR[/red]")
                continue

            # Format colors based on values
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

            table.add_row(
                ticker,
                latest['Date'],
                f"${latest['Price']:.2f}",
                rsi_str,
                macd_str,
                f"${latest['BB_Low']:.0f} - ${latest['BB_High']:.0f}",
                signal_str
            )

        except Exception as e:
            console.print(f"[red]Error analyzing {ticker}: {e}[/red]")

    console.print(table)

if __name__ == "__main__":
    main()
