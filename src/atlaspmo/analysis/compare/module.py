"""M7 as a registered module."""

from __future__ import annotations

import pandas as pd
from pydantic import BaseModel

from atlaspmo import __version__
from atlaspmo.analysis.compare.diff import compare_schedules
from atlaspmo.analysis.contract import (
    AnalysisContext,
    Metric,
    ModuleResult,
    Requirement,
    RunMetadata,
    empty_findings,
)


class CompareConfig(BaseModel):
    key: str = "task_code"


class CompareModule:
    id = "compare"
    name_es = "Comparación de updates"
    description_es = "Diferencias entre dos cronogramas emparejados por task_code."
    requires: set[Requirement] = {Requirement.TWO_VERSIONS}
    config_model: type[BaseModel] = CompareConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, CompareConfig) else CompareConfig()
        metadata = RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256)
        if chosen.key != "task_code":
            return _empty(
                self.id,
                metadata,
                ["Solo está implementado el emparejamiento por task_code."],
            )
        if ctx.schedule is None or ctx.other is None:
            return _empty(self.id, metadata, ["Falta el segundo cronograma."])
        report = compare_schedules(ctx.schedule, ctx.other)
        frame = pd.DataFrame(
            [
                {"kind": item.kind, "task_code": item.task_code, "detail": item.detail}
                for item in report.changes
            ]
        )
        return ModuleResult(
            module_id=self.id,
            metrics={
                "added": Metric(float(report.added), None, "info"),
                "removed": Metric(float(report.removed), None, "info"),
                "links_changed": Metric(float(report.links_changed), None, "info"),
                "critical_enter": Metric(float(report.critical_enter), None, "info"),
                "critical_exit": Metric(float(report.critical_exit), None, "info"),
                "float_eroded": Metric(float(report.float_eroded), None, "info"),
            },
            findings=empty_findings(),
            tables={"changes": frame},
            approximations=list(report.notes),
            metadata=metadata,
        )


def _empty(module_id: str, metadata: RunMetadata, notes: list[str]) -> ModuleResult:
    return ModuleResult(
        module_id=module_id,
        metrics={},
        findings=empty_findings(),
        tables={},
        approximations=notes,
        metadata=metadata,
    )
