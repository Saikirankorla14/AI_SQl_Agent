"""
charts/renderer.py
Auto-generate the best Plotly chart for a query result DataFrame.
Chart type is chosen by the LLM (via agent/llm.py).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from agent.llm import pick_chart_type


def render_chart(df: pd.DataFrame, question: str, show: bool = True) -> go.Figure:
    """
    Determine the best chart type for `df` given the original `question`,
    build a Plotly figure, and optionally open it in the browser.

    Returns the Figure object so callers can save or embed it.
    """
    if df.empty:
        raise ValueError("Cannot render a chart for an empty result set.")

    columns = list(df.columns)
    chart_type = pick_chart_type(columns, question)

    fig = _build_figure(df, columns, chart_type)
    fig.update_layout(
        template="plotly_white",
        font_family="monospace",
        margin=dict(t=40, b=40, l=40, r=40),
    )

    if show:
        fig.show()

    return fig


def _build_figure(df: pd.DataFrame, columns: list[str], chart_type: str) -> go.Figure:
    x_col = columns[0]
    y_col = columns[1] if len(columns) > 1 else columns[0]

    # Coerce numeric y if possible
    df = df.copy()
    try:
        df[y_col] = pd.to_numeric(df[y_col])
    except (ValueError, TypeError):
        pass

    if chart_type == "bar":
        return px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")

    if chart_type == "line":
        return px.line(df, x=x_col, y=y_col, title=f"{y_col} over {x_col}", markers=True)

    if chart_type == "pie":
        return px.pie(df, names=x_col, values=y_col, title=f"{y_col} distribution")

    if chart_type == "scatter":
        color_col = columns[2] if len(columns) > 2 else None
        return px.scatter(df, x=x_col, y=y_col, color=color_col,
                          title=f"{y_col} vs {x_col}")

    # Fallback: table
    fig = go.Figure(data=[go.Table(
        header=dict(values=columns, fill_color="#1a1a2e", font_color="white", align="left"),
        cells=dict(values=[df[c].tolist() for c in columns], align="left"),
    )])
    fig.update_layout(title="Query Results")
    return fig


def save_chart(fig: go.Figure, path: str = "output/chart.html") -> str:
    """Save a Plotly figure as a self-contained HTML file."""
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.write_html(path)
    return path
