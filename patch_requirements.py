import re

with open("requirements.txt", "r") as f:
    content = f.read()

content = content.replace("streamlit>=1.62.0", "streamlit")

with open("requirements.txt", "w") as f:
    f.write(content)
