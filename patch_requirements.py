import re

with open("requirements.txt", "r") as f:
    content = f.read()

content = content.replace("pandas>=3.0.5", "pandas>=2.0.0")

with open("requirements.txt", "w") as f:
    f.write(content)
