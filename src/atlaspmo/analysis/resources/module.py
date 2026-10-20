"""M6 as a registered module."""

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
from atlaspmo.analysis.resources.evm import earned_value


class EvmConfig(BaseModel):
    proj_id: str | None = None


class EvmModule:
    id = "evm"
    name_es = "EVM y Earned Schedule"
    description_es = "PV, EV, AC y Earned Schedule a la fecha de corte."
    requires: set[Requirement] = {Requirement.RESOURCES}
    config_model: type[BaseModel] = EvmConfig

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        chosen = config if isinstance(config, EvmConfig) else EvmConfig()
        metadata = RunMetadata(app_version=__version__, input_sha256=ctx.input_sha256)
        if ctx.schedule is None:
            return ModuleResult(
                module_id=self.id,
                metrics={},
                findings=empty_findings(),
                tables={},
                approximations=["No hay cronograma cargado."],
                metadata=metadata,
            )
        outcome = earned_value(ctx.schedule.select(chosen.proj_id))
        return ModuleResult(
            module_id=self.id,
            metrics={
                "pv": _metric(outcome.pv),
                "ev": _metric(outcome.ev),
                "ac": _metric(outcome.ac),
                "spi": _metric(outcome.spi),
                "cpi": _metric(outcome.cpi),
                "es_hours": _metric(outcome.es_hours),
                "at_hours": _metric(outcome.at_hours),
                "spi_t": _metric(outcome.spi_t),
                "ieac_t": _metric(outcome.ieac_t),
                "resource_limit": Metric(None, None, "no_evaluable"),
            },
            findings=empty_findings(),
            tables={
                "activities": pd.DataFrame(list(outcome.activities)),
                "wbs": pd.DataFrame(list(outcome.wbs)),
                "resources": pd.DataFrame(list(outcome.resources)),
                "scurve": pd.DataFrame(list(outcome.scurve)),
            },
            approximations=list(outcome.approximations),
            metadata=metadata,
        )


def _metric(value: float | None) -> Metric:
    if value is None:
        return Metric(None, None, "no_evaluable")
    return Metric(value, None, "info")
