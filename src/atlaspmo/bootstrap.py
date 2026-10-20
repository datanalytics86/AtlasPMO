"""Register the modules that exist in this build."""

from __future__ import annotations

from atlaspmo.analysis.logic.clean import CleanModule
from atlaspmo.analysis.logic.module import LogicModule
from atlaspmo.analysis.paths.mode_a import PathsModeA
from atlaspmo.analysis.paths.mode_b import PathsModeB
from atlaspmo.analysis.quality.module import QualityModule
from atlaspmo.analysis.resources.module import EvmModule
from atlaspmo.analysis.risk.module import RiskModule
from atlaspmo.registry import register_module, registered_modules


def bootstrap() -> None:
    known = {item.id for item in registered_modules()}
    if "quality" not in known:
        register_module(QualityModule())
    if "paths" not in known:
        register_module(PathsModeA())
    if "paths_b" not in known:
        register_module(PathsModeB())
    if "logic" not in known:
        register_module(LogicModule())
    if "clean" not in known:
        register_module(CleanModule())
    if "risk" not in known:
        register_module(RiskModule())
    if "evm" not in known:
        register_module(EvmModule())
