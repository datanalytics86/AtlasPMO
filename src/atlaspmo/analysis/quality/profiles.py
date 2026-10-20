"""YAML threshold profiles. Missing file falls back to the built-in DCMA set."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True)
class Profile:
    id: str
    nombre: str
    hours_per_day: float | None
    duration_field: str
    exclude_loe: bool
    exclude_wbs_summary: bool
    exclude_milestones_from_duration: bool
    hard_constraints: frozenset[str]
    high_float_days: float
    high_duration_days: float
    critical_float_days: float
    convergence_predecessors: int
    logic_max: float
    leads_max: float
    lags_max: float
    fs_min: float
    hard_max: float
    high_float_max: float
    negative_float_max: float
    high_duration_max: float
    invalid_dates_max: float
    resources_max: float | None
    missed_max: float
    cpli_min: float
    bei_min: float
    weights: dict[str, float]
    required_code_type_ids: tuple[str, ...]


def load_profile(name: str, hours_per_day: float | None = None) -> tuple[Profile, str | None]:
    """Return the profile and a note when the YAML file is missing."""
    path = ROOT / "profiles" / f"{name}.yaml"
    if not path.is_file():
        profile = _builtin(name)
        if hours_per_day is not None:
            profile = _with_hours(profile, hours_per_day)
        return profile, f"No está profiles/{name}.yaml. Se usaron los umbrales de código."
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"perfil {name} no es un mapa")
    profile = _from_mapping(name, raw)
    if hours_per_day is not None:
        profile = _with_hours(profile, hours_per_day)
    return profile, None


def _with_hours(profile: Profile, hours: float) -> Profile:
    return Profile(
        id=profile.id,
        nombre=profile.nombre,
        hours_per_day=hours,
        duration_field=profile.duration_field,
        exclude_loe=profile.exclude_loe,
        exclude_wbs_summary=profile.exclude_wbs_summary,
        exclude_milestones_from_duration=profile.exclude_milestones_from_duration,
        hard_constraints=profile.hard_constraints,
        high_float_days=profile.high_float_days,
        high_duration_days=profile.high_duration_days,
        critical_float_days=profile.critical_float_days,
        convergence_predecessors=profile.convergence_predecessors,
        logic_max=profile.logic_max,
        leads_max=profile.leads_max,
        lags_max=profile.lags_max,
        fs_min=profile.fs_min,
        hard_max=profile.hard_max,
        high_float_max=profile.high_float_max,
        negative_float_max=profile.negative_float_max,
        high_duration_max=profile.high_duration_max,
        invalid_dates_max=profile.invalid_dates_max,
        resources_max=profile.resources_max,
        missed_max=profile.missed_max,
        cpli_min=profile.cpli_min,
        bei_min=profile.bei_min,
        weights=profile.weights,
        required_code_type_ids=profile.required_code_type_ids,
    )


def _from_mapping(name: str, raw: dict[str, object]) -> Profile:
    weights = raw.get("weights", {})
    if not isinstance(weights, dict):
        raise ValueError("weights debe ser un mapa")
    hard = raw.get("hard_constraints", [])
    if not isinstance(hard, list):
        raise ValueError("hard_constraints debe ser una lista")
    required = raw.get("required_code_type_ids", [])
    if not isinstance(required, list):
        raise ValueError("required_code_type_ids debe ser una lista")
    return Profile(
        id=str(raw.get("id", name)),
        nombre=str(raw.get("nombre", name)),
        hours_per_day=_optional_float(raw.get("hours_per_day")),
        duration_field=str(raw.get("duration_field", "remain")),
        exclude_loe=bool(raw.get("exclude_loe", True)),
        exclude_wbs_summary=bool(raw.get("exclude_wbs_summary", True)),
        exclude_milestones_from_duration=bool(raw.get("exclude_milestones_from_duration", True)),
        hard_constraints=frozenset(str(item) for item in hard),
        high_float_days=_as_float(raw.get("high_float_days"), 44),
        high_duration_days=_as_float(raw.get("high_duration_days"), 44),
        critical_float_days=_as_float(raw.get("critical_float_days"), 0),
        convergence_predecessors=_as_int(raw.get("convergence_predecessors"), 4),
        logic_max=_as_float(raw.get("logic_max"), 0.05),
        leads_max=_as_float(raw.get("leads_max"), 0.0),
        lags_max=_as_float(raw.get("lags_max"), 0.05),
        fs_min=_as_float(raw.get("fs_min"), 0.90),
        hard_max=_as_float(raw.get("hard_max"), 0.05),
        high_float_max=_as_float(raw.get("high_float_max"), 0.05),
        negative_float_max=_as_float(raw.get("negative_float_max"), 0.0),
        high_duration_max=_as_float(raw.get("high_duration_max"), 0.05),
        invalid_dates_max=_as_float(raw.get("invalid_dates_max"), 0),
        resources_max=_optional_float(raw.get("resources_max")),
        missed_max=_as_float(raw.get("missed_max"), 0.05),
        cpli_min=_as_float(raw.get("cpli_min"), 0.95),
        bei_min=_as_float(raw.get("bei_min"), 0.95),
        weights={str(key): _as_float(value, 0) for key, value in weights.items()},
        required_code_type_ids=tuple(str(item) for item in required),
    )


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    return _as_float(value, 0.0)


def _as_float(value: object, default: float) -> float:
    if isinstance(value, bool) or value is None:
        return default
    if isinstance(value, (int, float, str)):
        return float(value)
    return default


def _as_int(value: object, default: int) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return default
    return int(value)


def _builtin(name: str) -> Profile:
    return _from_mapping(
        name,
        {
            "id": name,
            "nombre": name,
            "hard_constraints": ["CS_MSO", "CS_MEO", "CS_MANDSTART", "CS_MANDFIN"],
            "weights": {key: 1 for key in _WEIGHT_KEYS},
        },
    )


_WEIGHT_KEYS = (
    "logic",
    "leads",
    "lags",
    "relationship_types",
    "hard_constraints",
    "high_float",
    "negative_float",
    "high_duration",
    "invalid_dates",
    "missed_tasks",
    "cpli",
    "bei",
)
