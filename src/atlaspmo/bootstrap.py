"""Register the modules that exist in this build."""

from __future__ import annotations

from atlaspmo.analysis.paths.mode_a import PathsModeA
from atlaspmo.analysis.quality.module import QualityModule
from atlaspmo.registry import register_module, registered_modules


def bootstrap() -> None:
    known = {item.id for item in registered_modules()}
    if "quality" not in known:
        register_module(QualityModule())
    if "paths" not in known:
        register_module(PathsModeA())
