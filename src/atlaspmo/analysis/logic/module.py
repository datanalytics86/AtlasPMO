"""M3 as a registered module."""

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
from atlaspmo.analysis.logic.redundant import classify_links
from atlaspmo.engine.options import EngineOptions


class LogicConfig(BaseModel):
    progress: str = "retained"
    proj_id: str | None = None


class LogicModule:
    id = "logic"
    name_es = "Lógica redundante"
    description_es = "Marca vínculos redundantes solo si el CPM no se mueve al quitarlos."
    requires: set[Requirement] = {Requirement.CPM_ENGINE}
    config_model: type[BaseModel] = LogicConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, LogicConfig) else LogicConfig()
        if ctx.schedule is None:
            return ModuleResult(
                module_id=self.id,
                metrics={},
                findings=empty_findings(),
                tables={},
                approximations=["No hay cronograma cargado."],
                metadata=RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256),
            )
        schedule = ctx.schedule.select(chosen.proj_id)
        classes, result = classify_links(schedule, EngineOptions(chosen.progress))
        rows = [
            {
                "task_pred_id": item.task_pred_id,
                "status": item.status,
                "reason": item.reason,
            }
            for item in classes
        ]
        frame = pd.DataFrame(rows)
        confirmed = sum(1 for item in classes if item.status == "redundante_confirmado")
        return ModuleResult(
            module_id=self.id,
            metrics={"confirmed": Metric(float(confirmed), None, "info")},
            findings=empty_findings(),
            tables={"links": frame},
            approximations=list(
                dict.fromkeys([*schedule.parse_notes, *result.approximations])
            ),
            metadata=RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256),
        )
