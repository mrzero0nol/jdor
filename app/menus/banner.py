import time
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
import random

def show_banner():
    """
    Displays a cyberpunk-themed animated banner for 'ukons'.
    """
    console = Console()
    
    title = Text("ukons", style="bold cyan")
    title.stylize("bold magenta", 0, 1)
    title.stylize("bold yellow", 2, 3)
    
    panel = Panel(
        Align.center(title, vertical="middle"),
        title="[bold white]MYnyak Engsel[/bold white]",
        subtitle="[cyan]CLI Client[/cyan]",
        border_style="bold green",
        height=7,
        padding=(1, 5)
    )

    console.clear()

    # Glitch effect animation
    glitch_chars = ['▓', '▒', '░', '█', ' ', '█', '░', '▒', '▓']
    
    with Live(panel, console=console, screen=True, vertical_overflow="visible") as live:
        for i in range(15):
            if i % 3 == 0:
                glitch_title = ""
                for char in "ukons":
                    if random.random() > 0.7:
                        glitch_title += random.choice(glitch_chars)
                    else:
                        glitch_title += char

                temp_title = Text(glitch_title, style="bold red")
                panel.renderable = Align.center(temp_title, vertical="middle")
                live.update(panel)
                time.sleep(random.uniform(0.05, 0.1))

            panel.renderable = Align.center(title, vertical="middle")
            live.update(panel)
            time.sleep(random.uniform(0.05, 0.1))

        # Settle on the final banner
        panel.renderable = Align.center(title, vertical="middle")
        live.update(panel)
        time.sleep(0.5)
