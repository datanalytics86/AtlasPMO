"""Gantt from a CPM table. The UI does not calculate dates."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def gantt_figure(frame: pd.DataFrame) -> go.Figure:
    """One horizontal bar per row that has early_start and early_finish."""
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
        figure.add_bar(
            y=[str(code)],
            x=[width],
            base=[start],
            orientation="h",
            name=str(code),
        )
    figure.update_layout(barmode="overlay", showlegend=False)
    return figure
