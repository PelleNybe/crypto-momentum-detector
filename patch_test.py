import re

with open("tests/test_crypto_momentum.py", "r") as f:
    code = f.read()

# Fix the assert_called_once_with call
code = code.replace('mock_ticker.assert_called_once_with("BTC-USD")',
                    'mock_ticker.assert_called_once_with("BTC-USD", session=fetcher.session)')

with open("tests/test_crypto_momentum.py", "w") as f:
    f.write(code)

print("Patched test_crypto_momentum.py")
