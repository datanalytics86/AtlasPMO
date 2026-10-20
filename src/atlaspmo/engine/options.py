"""Scheduling choices. They are not read from unverified PROJECT columns."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineOptions:
    """Defaults are a product choice until a p6_verified file says otherwise."""

    progress: str = "retained"
    lag_calendar: str = "predecessor"
    float_kind: str = "minimum"
    critical_hours: float = 0.0
