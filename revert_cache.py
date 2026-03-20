import re

with open("crypto_momentum/data_fetcher.py", "r") as f:
    code = f.read()

# Revert session parameter
code = code.replace(
    "ticker = yf.Ticker(self.ticker_symbol, session=self.session)",
    "ticker = yf.Ticker(self.ticker_symbol)",
)

with open("crypto_momentum/data_fetcher.py", "w") as f:
    f.write(code)

with open("tests/test_crypto_momentum.py", "r") as f:
    code = f.read()

code = code.replace(
    'mock_ticker.assert_called_once_with("BTC-USD", session=fetcher.session)',
    'mock_ticker.assert_called_once_with("BTC-USD")',
)

with open("tests/test_crypto_momentum.py", "w") as f:
    f.write(code)

print("Reverted cache logic")
