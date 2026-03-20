import re

with open("main.py", "r") as f:
    code = f.read()

# Add backtester import
code = code.replace("from crypto_momentum.signal_generator import SignalGenerator",
                    "from crypto_momentum.signal_generator import SignalGenerator\nfrom crypto_momentum.backtester import Backtester")

# Change process_ticker signature
code = code.replace("def process_ticker(ticker, period, interval):",
                    "def process_ticker(ticker, period, interval, backtest=False):")

# Add backtest to process_ticker logic
backtest_logic = """
        generator = SignalGenerator(df_indicators)
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

        return latest"""

code = re.sub(r'        generator = SignalGenerator\(df_indicators\)\n        latest = generator.get_latest_signal\(\)\n\n        if not latest:\n            return \{"ticker": ticker, "status": "Insufficient Data", "error": True\}\n\n        latest\["ticker"\] = ticker\n        latest\["error"\] = False\n        return latest', backtest_logic, code)


# Update CLI args
cli_args = """    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="File path to export the results as CSV (e.g., results.csv)"
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run a backtest on historical data and show performance"
    )"""
code = code.replace("""    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="File path to export the results as CSV (e.g., results.csv)"
    )""", cli_args)

# Add argument parsing
parse_args = """    interval = args.interval
    export_path = args.export
    backtest = args.backtest"""
code = code.replace("""    interval = args.interval
    export_path = args.export""", parse_args)


# Update table setup
table_setup = """    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="dim", width=12)
    table.add_column("Date", justify="center")
    table.add_column("Price (USD)", justify="right")
    table.add_column("RSI (14)", justify="right")
    table.add_column("MACD", justify="right")
    table.add_column("BB (L-H)", justify="center")
    table.add_column("Signal", justify="center")
    if backtest:
        table.add_column("BT Return %", justify="right")"""
code = code.replace("""    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="dim", width=12)
    table.add_column("Date", justify="center")
    table.add_column("Price (USD)", justify="right")
    table.add_column("RSI (14)", justify="right")
    table.add_column("MACD", justify="right")
    table.add_column("BB (L-H)", justify="center")
    table.add_column("Signal", justify="center")""", table_setup)

# Update future submit
future_submit = "futures = {executor.submit(process_ticker, ticker, period, interval, backtest): ticker for ticker in tickers}"
code = code.replace("futures = {executor.submit(process_ticker, ticker, period, interval): ticker for ticker in tickers}", future_submit)


# Update row addition error case
row_error = """        if result['error']:
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
            export_data.append(row_data)"""
code = re.sub(r'        if result\[\'error\'\]:\n            table.add_row\(ticker, result\[\'status\'\], "-", "-", "-", "-", "\[red\]ERROR\[/red\]"\)\n            export_data.append\(\{.*?\n            \}\)', row_error, code, flags=re.DOTALL)


# Update row addition success case
row_success = """            signal_str = f"[{signal_color}]{signal}[/{signal_color}]"

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
            export_data.append(row_data)"""
code = re.sub(r'            signal_str = f"\[\{signal_color\}\]\{signal\}\[/\{signal_color\}\]"\n\n            table\.add_row\(\n                ticker,\n                latest\[\'Date\'\],\n                f"\$\{latest\[\'Price\'\]:\.2f\}",\n                rsi_str,\n                macd_str,\n                f"\$\{latest\[\'BB_Low\'\]:\.0f\} - \$\{latest\[\'BB_High\'\]:\.0f\}",\n                signal_str\n            \)\n            export_data\.append\(\{\n                "Ticker": ticker,\n                "Date": latest\[\'Date\'\],\n                "Price \(USD\)": f"\{latest\[\'Price\'\]:\.2f\}",\n                "RSI \(14\)": f"\{rsi:\.2f\}",\n                "MACD": f"\{latest\[\'MACD\'\]:\.2f\}",\n                "BB_Low": f"\{latest\[\'BB_Low\'\]:\.2f\}",\n                "BB_High": f"\{latest\[\'BB_High\'\]:\.2f\}",\n                "Signal": signal\n            \}\)', row_success, code, flags=re.DOTALL)


# Update export fields
export_fields = """            with open(export_path, 'w', newline='') as csvfile:
                fieldnames = ["Ticker", "Date", "Price (USD)", "RSI (14)", "MACD", "BB_Low", "BB_High", "Signal"]
                if backtest:
                    fieldnames.append("BT_Return_Pct")
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)"""
code = code.replace("""            with open(export_path, 'w', newline='') as csvfile:
                fieldnames = ["Ticker", "Date", "Price (USD)", "RSI (14)", "MACD", "BB_Low", "BB_High", "Signal"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)""", export_fields)

with open("main.py", "w") as f:
    f.write(code)

print("Patched main.py for backtest")
