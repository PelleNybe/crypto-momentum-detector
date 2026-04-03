import subprocess
import sys

try:
    result = subprocess.run(["python", "main.py", "--tickers", "BTC-USD", "ETH-USD"], capture_output=True, text=True, timeout=30)
    print("STDOUT:")
    print(result.stdout)
    print("STDERR:")
    print(result.stderr)
except subprocess.TimeoutExpired as e:
    print("Timeout")
    print("STDOUT:")
    print(e.stdout)
    print("STDERR:")
    print(e.stderr)
