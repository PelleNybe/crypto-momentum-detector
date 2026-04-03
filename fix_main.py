with open("main.py", "r") as f:
    content = f.read()

content = content.replace('"[bold cyan]⚡ NeonPulse AI Crypto Terminal ⚡[/bold cyan]\n"', '"[bold cyan]⚡ NeonPulse AI Crypto Terminal ⚡[/bold cyan]\\n"')
content = content.replace('"[dim]Neural Network + Momentum Scanning + Risk Profiling[/dim]\n"', '"[dim]Neural Network + Momentum Scanning + Risk Profiling[/dim]\\n"')
with open("main.py", "w") as f:
    f.write(content)
