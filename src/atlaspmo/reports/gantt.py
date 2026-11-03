"""Gantt from a CPM table. The UI does not calculate dates."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

_DRIVING = "#b00020"
_OTHER = "#9aa0a6"


def gantt_figure(frame: pd.DataFrame, driving: set[str] | None = None) -> go.Figure:
    """One horizontal bar per row. Driving codes use a separate color."""
    marked = driving or set()
    figure = go.Figure()
    if "task_code" not in frame.columns:
        return figure
    for row in frame.itertuples(index=False):
        start = getattr(row, "early_start", None)
        finish = getattr(row, "early_finish", None)
        code = getattr(row, "task_code", None)
        if start is None or finish is None or code is None:
            continue
        width = (finish - start).total_seconds() * 1000
        color = _DRIVING if str(code) in marked else _OTHER
        figure.add_bar(
            y=[str(code)],
            x=[width],
            base=[start],
            orientation="h",
            name=str(code),
            marker_color=color,
        )
    figure.update_layout(barmode="overlay", showlegend=False)
    return figure
