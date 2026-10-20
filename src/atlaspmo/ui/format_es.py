"""es-CL number and date formatting for the UI and reports."""

from __future__ import annotations

from datetime import date


def format_number(value: float, decimals: int = 2) -> str:
    """Format with a comma decimal mark and a dot as the thousands separator."""
    if decimals < 0:
        raise ValueError("decimals must be >= 0")
    sign = "-" if value < 0 else ""
    rendered = f"{abs(value):,.{decimals}f}"
    rendered = rendered.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return sign + rendered


def format_date(value: date) -> str:
    """Format a date as dd-mm-aaaa."""
    return value.strftime("%d-%m-%Y")
