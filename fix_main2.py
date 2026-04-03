with open("main.py", "r") as f:
    content = f.read()

# Update format_ai_confidence to handle dict
new_format = """
def format_ai_confidence(val):
    if isinstance(val, dict):
        val = val.get("confidence", 50.0)
    if val >= 60:
        return f"[bold cyan]{val:.1f}%[/bold cyan]"
    if val <= 40:
        return f"[bold red]{val:.1f}%[/bold red]"
    return f"[bold yellow]{val:.1f}%[/bold yellow]"
"""

import re
content = re.sub(r'def format_ai_confidence\(val\):.*?return f"\[bold yellow\]\{val:.1f\}%\[/bold yellow\]"', new_format.strip(), content, flags=re.DOTALL)

with open("main.py", "w") as f:
    f.write(content)
