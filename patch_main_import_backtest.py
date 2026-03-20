import re

with open("main.py", "r") as f:
    code = f.read()

if "from crypto_momentum.backtester import Backtester" not in code:
    code = code.replace("from crypto_momentum.signal_generator import SignalGenerator", "from crypto_momentum.signal_generator import SignalGenerator\nfrom crypto_momentum.backtester import Backtester")

with open("main.py", "w") as f:
    f.write(code)

print("Import patched.")
