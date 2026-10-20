"""Run the modules the user selected."""

from __future__ import annotations

from pydantic import BaseModel

from atlaspmo.analysis.contract import AnalysisContext, ModuleResult
from atlaspmo.registry import get_module


def run_selected(
    module_ids: list[str],
    ctx: AnalysisContext,
    configs: dict[str, BaseModel] | None = None,
) -> list[ModuleResult]:
    """Run each id in order. An unknown id raises KeyError and stops the batch."""
    chosen = configs or {}
    results: list[ModuleResult] = []
    for module_id in module_ids:
        module = get_module(module_id)
        config = chosen.get(module_id)
        if config is None:
            config = module.config_model()
        results.append(module.run(ctx, config))
    return results
