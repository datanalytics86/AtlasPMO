"""In-process catalog of analysis modules."""

from __future__ import annotations

from atlaspmo.analysis.contract import AnalysisModule

_MODULES: dict[str, AnalysisModule] = {}


def registered_modules() -> tuple[AnalysisModule, ...]:
    """Return modules sorted by id. Phase 0 registers none."""
    return tuple(_MODULES[key] for key in sorted(_MODULES))


def get_module(module_id: str) -> AnalysisModule:
    """Return one module or raise KeyError if it is not registered."""
    try:
        return _MODULES[module_id]
    except KeyError as exc:
        known = ", ".join(sorted(_MODULES)) or "(none)"
        raise KeyError(f"Unknown module id {module_id!r}. Registered: {known}") from exc


def register_module(module: AnalysisModule) -> None:
    """Add a module. Duplicate ids are a programming error."""
    if module.id in _MODULES:
        raise ValueError(f"Module id {module.id!r} is already registered")
    _MODULES[module.id] = module


def clear_modules() -> None:
    """Drop every registration. Tests use this to isolate cases."""
    _MODULES.clear()
