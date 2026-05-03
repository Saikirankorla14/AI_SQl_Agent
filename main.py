"""
main.py
AI SQL Agent — CLI entry point.

Usage:
    python main.py

Special commands (type at the prompt):
    /history    — show recent query history
    /schema     — print all tables and columns
    /clear      — clear query history
    /help       — show available commands
    exit | quit — exit the agent
"""

import sys

from agent.db import get_schema, run_query, test_connection
from agent.llm import nl_to_sql, explain_sql
from charts.renderer import render_chart
from utils.display import (
    console, print_banner, print_sql, print_explanation,
    print_dataframe, print_error, print_success, print_info, print_history,
)
from utils.history import QueryHistory

history = QueryHistory(persist_path="output/history.json")


# ── helpers ───────────────────────────────────────────────────────────────────

def cmd_schema(schema: dict):
    from rich.tree import Tree
    tree = Tree("[bold]Database schema[/bold]")
    for table, cols in schema.items():
        branch = tree.add(f"[cyan]{table}[/cyan]")
        for col in cols:
            branch.add(f"[dim]{col}[/dim]")
    console.print(tree)


def cmd_history():
    print_history(history.last(10))


def cmd_help():
    console.print("""
[bold]Available commands:[/bold]
  [cyan]/schema[/cyan]   — list all tables and columns
  [cyan]/history[/cyan]  — show the last 10 queries
  [cyan]/clear[/cyan]    — clear query history
  [cyan]/help[/cyan]     — show this message
  [cyan]exit[/cyan]      — quit the agent
""")


# ── main loop ─────────────────────────────────────────────────────────────────

def main():
    print_banner()

    # 1. Test DB connection
    print_info("Connecting to database…")
    if not test_connection():
        print_error("Cannot reach the database. Check DB_URL in your .env file.")
        sys.exit(1)
    print_success("Database connected.")

    # 2. Load schema once
    print_info("Loading schema…")
    schema = get_schema()
    print_success(f"Schema loaded — {len(schema)} table(s) found.\n")

    # 3. REPL
    while True:
        try:
            question = console.input("[bold bright_blue]Ask your database:[/bold bright_blue] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not question:
            continue

        # Built-in commands
        if question.lower() in ("exit", "quit"):
            console.print("[dim]Goodbye.[/dim]")
            break
        if question == "/schema":
            cmd_schema(schema)
            continue
        if question == "/history":
            cmd_history()
            continue
        if question == "/clear":
            history.clear()
            print_success("History cleared.")
            continue
        if question == "/help":
            cmd_help()
            continue

        # ── NL → SQL ──────────────────────────────────────────────────────────
        try:
            sql = nl_to_sql(question, schema)
        except Exception as e:
            print_error(f"LLM error: {e}")
            continue

        print_sql(sql)

        # ── Explanation ───────────────────────────────────────────────────────
        try:
            explanation = explain_sql(sql)
            print_explanation(explanation)
        except Exception:
            pass  # Explanation is non-critical

        # ── Confirmation ──────────────────────────────────────────────────────
        try:
            confirm = console.input("[bold]Run this query? [Y/n]:[/bold] ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print()
            continue

        if confirm == "n":
            console.print("[dim]Skipped.[/dim]\n")
            continue

        # ── Execute ───────────────────────────────────────────────────────────
        try:
            df = run_query(sql)
        except (ValueError, RuntimeError) as e:
            print_error(str(e))
            history.add(question, sql, row_count=0, error=str(e))
            continue

        history.add(question, sql, row_count=len(df))
        print_dataframe(df)

        # ── Chart ─────────────────────────────────────────────────────────────
        if not df.empty and len(df.columns) >= 2:
            try:
                chart_confirm = console.input("[bold]Generate chart? [Y/n]:[/bold] ").strip().lower()
                if chart_confirm != "n":
                    render_chart(df, question, show=True)
            except Exception as e:
                print_error(f"Chart error: {e}")

        console.print()


if __name__ == "__main__":
    main()
