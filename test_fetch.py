from app import process_ticker

strategy_params = {
    "rsi_buy_min": 40,
    "rsi_buy_max": 70,
    "rsi_sell_min": 30,
    "rsi_sell_max": 60,
    "rsi_strong_buy": 30,
    "rsi_strong_sell": 70,
}

res = process_ticker("BTC-USD", "6mo", "1d", False, strategy_params, False)
print(res)
