"""Delete only the confirmed redundant TASKPRED rows."""

from __future__ import annotations

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
from atlaspmo.engine.cpm import CpmResult, schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import XerFile
from atlaspmo.model.schedule import Schedule


class CleanConfig(BaseModel):
    progress: str = "retained"
    lag_calendar: str = "predecessor"
    float_kind: str = "minimum"
    critical_hours: float = 0.0


class CleanModule:
    id = "clean"
    name_es = "Limpieza de XER"
    description_es = "Borra solo filas TASKPRED confirmadas como redundantes."
    requires: set[Requirement] = {Requirement.CPM_ENGINE}
    config_model: type[BaseModel] = CleanConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, CleanConfig) else CleanConfig()
        options = EngineOptions(
            chosen.progress,
            chosen.lag_calendar,
            chosen.float_kind,
            chosen.critical_hours,
        )
        if ctx.schedule is None or ctx.document is None:
            return _empty(["Hace falta el cronograma y el XER original."], ctx)
        cleaned, before, after, removed = clean_document(ctx.document, ctx.schedule, options)
        same = _same_result(before, after)
        notes = [
            *ctx.schedule.parse_notes,
            *before.approximations,
            f"bytes={len(cleaned.to_bytes())}",
        ]
        if not same:
            notes.append("No se escribió el XER: el delta de fechas u holgura no es cero.")
        return ModuleResult(
            module_id=self.id,
            metrics={
                "removed_links": Metric(float(removed), None, "info"),
                "dates_unchanged": Metric(
                    1.0 if same else 0.0,
                    1.0,
                    "cumple" if same else "no_cumple",
                ),
            },
            findings=empty_findings(),
            tables={},
            approximations=list(dict.fromkeys(notes)),
            metadata=RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256),
        )


def clean_document(
    document: XerFile,
    schedule: Schedule,
    options: EngineOptions | None = None,
) -> tuple[XerFile, CpmResult, CpmResult, int]:
    """Drop confirmed TASKPRED lines and reschedule the cleaned file."""
    chosen = options or EngineOptions()
    classes, before = classify_links(schedule, chosen)
    drop_ids = {item.task_pred_id for item in classes if item.status == "redundante_confirmado"}
    indexes = {
        link.line_index
        for link in schedule.relationships
        if link.task_pred_id in drop_ids and link.line_index is not None
    }
    cleaned = document.drop_rows("TASKPRED", indexes)
    after = schedule_cpm(schedule_from_xer(cleaned), chosen)
    if not _same_result(before, after):
        return document, before, after, 0
    return cleaned, before, after, len(indexes)


def _same_result(left: CpmResult, right: CpmResult) -> bool:
    if left.project_finish != right.project_finish:
        return False
    if set(left.by_id) != set(right.by_id):
        return False
    for key, item in left.by_id.items():
        other = right.by_id[key]
        if item.early_start != other.early_start or item.early_finish != other.early_finish:
            return False
        if item.late_start != other.late_start or item.late_finish != other.late_finish:
            return False
        if item.total_float_hours != other.total_float_hours:
            return False
        if item.free_float_hours != other.free_float_hours:
            return False
    return True


def _empty(notes: list[str], ctx: AnalysisContext) -> ModuleResult:
    return ModuleResult(
        module_id="clean",
        metrics={},
        findings=empty_findings(),
        tables={},
        approximations=notes,
        metadata=RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256),
    )
