"""M5 as a registered module. Sampling stays out of the UI."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel

from atlaspmo import __version__
from atlaspmo.analysis.contract import (
    AnalysisContext,
    Metric,
    ModuleResult,
    Requirement,
    RunMetadata,
    empty_findings,
)
from atlaspmo.analysis.risk.config import RiskConfig
from atlaspmo.analysis.risk.montecarlo import run_risk


class RiskModule:
    id = "risk"
    name_es = "Riesgo (Monte Carlo)"
    description_es = "Sensibilidad y Monte Carlo. Con varianza cero reproduce el CPM."
    requires: set[Requirement] = {Requirement.CPM_ENGINE}
    config_model: type[BaseModel] = RiskConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, RiskConfig) else RiskConfig()
        metadata = RunMetadata(
            app_version=__version__,
            input_sha256=ctx.input_sha256,
            parameters={
                "iterations": str(chosen.iterations),
                "tornado_hours": str(chosen.tornado_hours),
            },
            seed=chosen.seed,
        )
        if ctx.schedule is None:
            return ModuleResult(
                module_id=self.id,
                metrics={},
                findings=empty_findings(),
                tables={},
                approximations=["No hay cronograma cargado."],
                metadata=metadata,
            )
        outcome = run_risk(ctx.schedule.select(chosen.proj_id), chosen)
        count = len(outcome.finishes)
        cumulative = [] if count == 0 else [(index + 1) / count for index in range(count)]
        finishes = pd.DataFrame(
            {"project_finish": list(outcome.finishes), "cumulative": cumulative}
        )
        return ModuleResult(
            module_id=self.id,
            metrics={
                "iterations": Metric(float(outcome.iterations), None, "info"),
                "ssi": Metric(
                    _extreme([item.ssi for item in outcome.activities]),
                    None,
                    outcome.ssi_status,
                ),
                "cruciality": Metric(
                    _extreme([item.cruciality for item in outcome.activities]),
                    None,
                    outcome.sensitivity_status,
                ),
                "spearman": Metric(
                    _extreme([item.spearman for item in outcome.activities]),
                    None,
                    outcome.sensitivity_status,
                ),
            },
            findings=empty_findings(),
            tables={
                "finishes": finishes,
                "activities": pd.DataFrame([item.__dict__ for item in outcome.activities]),
                "tornado": pd.DataFrame([item.__dict__ for item in outcome.tornado]),
                "milestones": pd.DataFrame([item.__dict__ for item in outcome.milestones]),
                "convergence": pd.DataFrame([item.__dict__ for item in outcome.convergence]),
            },
            approximations=list(outcome.approximations),
            metadata=metadata,
        )


def _extreme(values: list[float | None]) -> float | None:
    numbers = [item for item in values if item is not None]
    if not numbers:
        return None
    return max(numbers, key=abs)
