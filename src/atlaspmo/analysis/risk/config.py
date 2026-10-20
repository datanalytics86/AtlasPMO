"""User-supplied risk inputs. None of these fields are read from the XER."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class DurationRange(BaseModel):
    task_code: str
    low: float
    mode: float
    high: float
    distribution: Literal["triangular", "beta_pert", "uniform"] = "triangular"


class RiskEvent(BaseModel):
    name: str
    probability: float
    impact_hours: float
    task_codes: list[str] = []


class CorrelationPair(BaseModel):
    left: str
    right: str
    coefficient: float


class RiskConfig(BaseModel):
    seed: int = 1
    iterations: int = 1000
    ranges: list[DurationRange] = []
    events: list[RiskEvent] = []
    correlations: list[CorrelationPair] = []
    tornado_hours: float = 8.0
    progress: str = "retained"
    proj_id: str | None = None
