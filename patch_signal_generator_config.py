import re

with open("crypto_momentum/signal_generator.py", "r") as f:
    code = f.read()

# Update __init__
init_code = """    def __init__(self, data: pd.DataFrame, rsi_buy_min: int = 40, rsi_buy_max: int = 70,
                 rsi_sell_min: int = 30, rsi_sell_max: int = 60, rsi_strong_buy: int = 30, rsi_strong_sell: int = 70):
        \"\"\"
        Initializes the SignalGenerator with data containing momentum indicators.

        Args:
            data (pd.DataFrame): Dataframe that should include 'RSI_14', 'MACD', 'MACD_Signal',
                                 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'ATR_14' and 'Close'.
            rsi_buy_min (int): Minimum RSI for a regular buy signal.
            rsi_buy_max (int): Maximum RSI for a regular buy signal.
            rsi_sell_min (int): Minimum RSI for a regular sell signal.
            rsi_sell_max (int): Maximum RSI for a regular sell signal.
            rsi_strong_buy (int): RSI threshold for a strong buy signal (below this).
            rsi_strong_sell (int): RSI threshold for a strong sell signal (above this).
        \"\"\"
        self.data = data
        self.rsi_buy_min = rsi_buy_min
        self.rsi_buy_max = rsi_buy_max
        self.rsi_sell_min = rsi_sell_min
        self.rsi_sell_max = rsi_sell_max
        self.rsi_strong_buy = rsi_strong_buy
        self.rsi_strong_sell = rsi_strong_sell"""
code = re.sub(r'    def __init__\(self, data: pd\.DataFrame\):\n        \"\"\"\n        Initializes the SignalGenerator.*?\n        \"\"\"\n        self\.data = data', init_code, code, flags=re.DOTALL)


# Update generate_signals conditions
cond_code = """        is_bullish = (rsi > self.rsi_buy_min) & (rsi < self.rsi_buy_max) & (macd > macd_signal) & (close > ema_20)
        is_bearish = (rsi < self.rsi_sell_max) & (rsi > self.rsi_sell_min) & (macd < macd_signal) & (close < ema_20)

        strong_buy_cond = (rsi < self.rsi_strong_buy) & (macd > macd_signal) & (close < bb_low)
        strong_sell_cond = (rsi > self.rsi_strong_sell) & (macd < macd_signal) & (close > bb_high)"""
code = re.sub(r'        is_bullish = \(rsi > 40\) & \(rsi < 70\) & \(macd > macd_signal\) & \(close > ema_20\)\n        is_bearish = \(rsi < 60\) & \(rsi > 30\) & \(macd < macd_signal\) & \(close < ema_20\)\n\n        strong_buy_cond = \(rsi < 30\) & \(macd > macd_signal\) & \(close < bb_low\)\n        strong_sell_cond = \(rsi > 70\) & \(macd < macd_signal\) & \(close > bb_high\)', cond_code, code)

with open("crypto_momentum/signal_generator.py", "w") as f:
    f.write(code)

print("Patched signal_generator.py for config")
