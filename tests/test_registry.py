"""Registry starts empty and rejects unknown ids."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from atlaspmo import __version__
from atlaspmo.analysis.contract import (
    FINDING_COLUMNS,
    AnalysisContext,
    Metric,
    ModuleResult,
    Requirement,
    RunMetadata,
    empty_findings,
)
from atlaspmo.registry import clear_modules, get_module, register_module, registered_modules
from atlaspmo.runner import run_selected


class _Config(BaseModel):
    pass


class _Demo:
    id = "demo"
    name_es = "Demo"
    description_es = "Modulo de prueba"
    requires = {Requirement.CPM_ENGINE}
    config_model = _Config

    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult:
        return ModuleResult(
            module_id=self.id,
            metrics={"n": Metric(value=1.0, threshold=None, status="info")},
            findings=empty_findings(),
            tables={},
            approximations=[],
            metadata=RunMetadata(app_version=__version__),
        )


@pytest.fixture(autouse=True)
def _isolated_registry():
    clear_modules()
    yield
    clear_modules()


def test_registry_starts_empty():
    assert registered_modules() == ()


def test_unknown_module_raises():
    with pytest.raises(KeyError, match="missing"):
        get_module("missing")


def test_register_and_run():
    register_module(_Demo())
    results = run_selected(["demo"], AnalysisContext())
    assert results[0].module_id == "demo"
    assert list(results[0].findings.columns) == list(FINDING_COLUMNS)
    assert results[0].approximations == []


def test_duplicate_id_raises():
    register_module(_Demo())
    with pytest.raises(ValueError, match="demo"):
        register_module(_Demo())
