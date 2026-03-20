import re

with open("main.py", "r") as f:
    code = f.read()

# Update process_ticker signature
code = code.replace("def process_ticker(ticker, period, interval, backtest=False):",
                    "def process_ticker(ticker, period, interval, backtest=False, strategy_params=None):")

# Add params to generator
gen_code = """        if strategy_params is None:
            strategy_params = {}
        generator = SignalGenerator(df_indicators, **strategy_params)"""
code = code.replace("        generator = SignalGenerator(df_indicators)", gen_code)


# Add CLI args
cli_args = """    parser.add_argument(
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
    parser.add_argument("--rsi-strong-sell", type=int, default=70, help="RSI threshold for strong sell")"""
code = code.replace("""    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run a backtest on historical data and show performance"
    )""", cli_args)

# Extract params
parse_code = """    backtest = args.backtest

    strategy_params = {
        'rsi_buy_min': args.rsi_buy_min,
        'rsi_buy_max': args.rsi_buy_max,
        'rsi_sell_min': args.rsi_sell_min,
        'rsi_sell_max': args.rsi_sell_max,
        'rsi_strong_buy': args.rsi_strong_buy,
        'rsi_strong_sell': args.rsi_strong_sell
    }"""
code = code.replace("    backtest = args.backtest", parse_code)


# Update future submit
future_submit = "futures = {executor.submit(process_ticker, ticker, period, interval, backtest, strategy_params): ticker for ticker in tickers}"
code = code.replace("futures = {executor.submit(process_ticker, ticker, period, interval, backtest): ticker for ticker in tickers}", future_submit)


with open("main.py", "w") as f:
    f.write(code)

print("Patched main.py for config")
