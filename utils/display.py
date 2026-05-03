"""
utils/display.py
Terminal display helpers using the Rich library.
Provides pretty tables, SQL highlighting, banners, and status messages.
"""

from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import pandas as pd

console = Console()


def print_banner():
    banner = Text()
    banner.append("  AI SQL Agent  ", style="bold white on #1a1a2e")
    console.print()
    console.print(Panel(banner, subtitle="[dim]Powered by Groq + SQLAlchemy[/dim]",
                         border_style="bright_blue"))
    console.print()


def print_sql(sql: str):
    syntax = Syntax(sql, "sql", theme="monokai", line_numbers=False, word_wrap=True)
    console.print(Panel(syntax, title="[bold cyan]Generated SQL[/bold cyan]",
                         border_style="cyan"))


def print_explanation(text: str):
    console.print(Panel(f"[italic]{text}[/italic]",
                         title="[bold green]What this query does[/bold green]",
                         border_style="green"))


def print_dataframe(df: pd.DataFrame):
    if df.empty:
        console.print("[yellow]No rows returned.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta",
                  border_style="dim", row_styles=["", "dim"])

    for col in df.columns:
        table.add_column(str(col), overflow="fold")

    for _, row in df.iterrows():
        table.add_row(*[str(v) for v in row.values])

    console.print(table)
    console.print(f"[dim]{len(df)} row(s) returned.[/dim]")


def print_error(message: str):
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str):
    console.print(f"[bold green]✓[/bold green] {message}")


def print_info(message: str):
    console.print(f"[bold blue]→[/bold blue] {message}")


def print_history(entries: list):
    if not entries:
        console.print("[dim]No history yet.[/dim]")
        return

    table = Table(title="Recent Queries", border_style="dim", show_lines=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Question", style="cyan")
    table.add_column("Rows", justify="right", width=6)
    table.add_column("Time", style="dim", width=20)

    for i, e in enumerate(entries, 1):
        status = f"[red]ERR[/red]" if e.error else str(e.row_count)
        table.add_row(str(i), e.question, status, e.timestamp)

    console.print(table)
