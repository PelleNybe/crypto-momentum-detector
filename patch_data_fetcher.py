import re

with open("crypto_momentum/data_fetcher.py", "r") as f:
    code = f.read()

new_imports = """import yfinance as yf
import pandas as pd
import logging
import requests_cache
"""

code = code.replace("import yfinance as yf\nimport pandas as pd\nimport logging\n", new_imports)

init_method = """    def __init__(self, ticker_symbol: str = "BTC-USD", cache_db: str = ".yfinance_cache"):
        \"\"\"
        Initialize the DataFetcher with a specific cryptocurrency ticker.
        yfinance uses symbols like 'BTC-USD', 'ETH-USD'.
        \"\"\"
        self.ticker_symbol = ticker_symbol
        self.session = requests_cache.CachedSession(cache_db, expire_after=3600)  # cache for 1 hour
"""

code = re.sub(r'    def __init__\(self, ticker_symbol: str = "BTC-USD"\):\n        \"\"\"\n        Initialize the DataFetcher.*?\n        \"\"\"\n        self\.ticker_symbol = ticker_symbol\n', init_method, code, flags=re.DOTALL)

fetch_method = """        try:
            ticker = yf.Ticker(self.ticker_symbol, session=self.session)
            df = ticker.history(period=period, interval=interval)"""

code = code.replace("""        try:
            ticker = yf.Ticker(self.ticker_symbol)
            df = ticker.history(period=period, interval=interval)""", fetch_method)

with open("crypto_momentum/data_fetcher.py", "w") as f:
    f.write(code)

print("Patched data_fetcher.py")
