"""M1 quality module. DCMA 12 is not registered here."""

from __future__ import annotations

from pydantic import BaseModel

from atlaspmo import __version__
from atlaspmo.analysis.contract import AnalysisContext, ModuleResult, Requirement, RunMetadata
from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile


class QualityConfig(BaseModel):
    profile: str = "dcma_estricto"
    proj_id: str | None = None
    baseline_proj_id: str | None = None
    hours_per_day: float | None = None


class QualityModule:
    id = "quality"
    name_es = "Calidad (DCMA y GAO)"
    description_es = "Chequeos DCMA salvo la prueba de ruta, más GAO automatizable."
    requires: set[Requirement] = set()
    config_model: type[BaseModel] = QualityConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, QualityConfig) else QualityConfig()
        profile, note = load_profile(chosen.profile, chosen.hours_per_day)
        approximations = [note] if note else []
        if ctx.schedule is None:
            from atlaspmo.analysis.contract import empty_findings

            approximations.append("No hay cronograma cargado.")
            return ModuleResult(
                module_id=self.id,
                metrics={},
                findings=empty_findings(),
                tables={},
                approximations=approximations,
                metadata=RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256),
            )
        current = ctx.schedule.select(chosen.proj_id)
        baseline = (
            ctx.schedule.select(chosen.baseline_proj_id) if chosen.baseline_proj_id else None
        )
        metrics, findings, notes = evaluate(current, profile, baseline)
        approximations.extend(notes)
        return ModuleResult(
            module_id=self.id,
            metrics=metrics,
            findings=findings,
            tables={},
            approximations=approximations,
            metadata=RunMetadata(
                app_version=__version__,
                input_sha256=ctx.input_sha256,
                parameters={"profile": chosen.profile, "proj_id": chosen.proj_id or ""},
                profile=profile.id,
            ),
        )
