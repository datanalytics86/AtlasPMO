"""Module contract shared by every analysis module."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

import pandas as pd
from pydantic import BaseModel

from atlaspmo.io.xer import XerFile
from atlaspmo.model.schedule import Schedule


class Requirement(StrEnum):
    """Inputs a module may declare before it can run."""

    BASELINE = "BASELINE"
    RESOURCES = "RESOURCES"
    TWO_VERSIONS = "TWO_VERSIONS"
    CPM_ENGINE = "CPM_ENGINE"


class FindingSource(StrEnum):
    """Normative origin of a finding."""

    DCMA = "DCMA"
    GAO = "GAO"
    AACE = "AACE"
    ATLASPMO = "ATLASPMO"


class Severity(StrEnum):
    """Finding severity. User-facing labels stay in Spanish."""

    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    INFO = "info"


class ObjectType(StrEnum):
    """Schedule object a finding points at."""

    PROJECT = "project"
    ACTIVITY = "activity"
    RELATIONSHIP = "relationship"
    RESOURCE = "resource"


FINDING_COLUMNS: tuple[str, ...] = (
    "rule_id",
    "rule_name_es",
    "source",
    "severity",
    "object_type",
    "object_id",
    "task_code",
    "value",
    "threshold",
    "passed",
    "message_es",
)


def empty_findings() -> pd.DataFrame:
    """Return a findings table with the contract columns and no rows."""
    return pd.DataFrame(columns=list(FINDING_COLUMNS))


@dataclass(frozen=True)
class AnalysisContext:
    """Inputs for a module run. The schedule is optional so the registry tests stay valid."""

    schedule: Schedule | None = None
    other: Schedule | None = None
    document: XerFile | None = None
    input_sha256: str | None = None
    input_name: str | None = None


@dataclass(frozen=True)
class RunMetadata:
    """Reproducibility record for one module run."""

    app_version: str
    git_commit: str | None = None
    input_sha256: str | None = None
    parameters: dict[str, str] = field(default_factory=dict)
    profile: str | None = None
    seed: int | None = None


@dataclass
class Metric:
    """KPI value compared with a threshold."""

    value: float | None
    threshold: float | None
    status: str


@dataclass
class ModuleResult:
    """Output of one analysis module."""

    module_id: str
    metrics: dict[str, Metric]
    findings: pd.DataFrame
    tables: dict[str, pd.DataFrame]
    approximations: list[str]
    metadata: RunMetadata


class AnalysisModule(Protocol):
    """Every analysis module satisfies this contract."""

    id: str
    name_es: str
    description_es: str
    requires: set[Requirement]
    config_model: type[BaseModel]

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        """Execute the module. Implementations record every approximation."""
