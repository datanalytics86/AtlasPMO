"""Approximations the phase-5 review now puts on the module result."""

from dataclasses import replace
from pathlib import Path

from atlaspmo.analysis.compare.module import CompareConfig, CompareModule
from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.logic.clean import CleanConfig, CleanModule
from atlaspmo.analysis.logic.module import LogicConfig, LogicModule
from atlaspmo.analysis.paths.mode_a import PathsConfig, PathsModeA
from atlaspmo.analysis.paths.mode_b import PathsBConfig, PathsModeB
from atlaspmo.analysis.quality.module import QualityConfig, QualityModule
from atlaspmo.analysis.resources.evm import earned_value
from atlaspmo.io.xer import read_xer
from test_cpm import _load, _task

_NOTE = "nota de carga visible"


def test_missing_float_and_hours_override_are_noted(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8")], [])
    missing = PathsModeA().run(AnalysisContext(schedule=schedule), PathsConfig())
    assert any("No entran a las bandas" in note for note in missing.approximations)
    override = PathsModeA().run(
        AnalysisContext(schedule=schedule),
        PathsConfig(hours_per_day=8),
    )
    assert any("reemplaza el del perfil" in note for note in override.approximations)
    quality = QualityModule().run(
        AnalysisContext(schedule=schedule),
        QualityConfig(hours_per_day=8),
    )
    assert any("reemplaza el del perfil" in note for note in quality.approximations)


def test_mode_b_names_the_probe(tmp_path: Path) -> None:
    schedule = _load(tmp_path, [_task("1", "A", "8")], [])
    result = PathsModeB().run(AnalysisContext(schedule=schedule), PathsBConfig())
    assert any("CP Test atrasa 8 horas" in note for note in result.approximations)


def test_parse_note_reaches_the_modules(tmp_path: Path) -> None:
    schedule = replace(
        _load(tmp_path, [_task("1", "A", "8")], []),
        parse_notes=(_NOTE,),
    )
    document = read_xer(tmp_path / "case.xer")
    context = AnalysisContext(schedule=schedule, document=document)
    assert _NOTE in LogicModule().run(context, LogicConfig()).approximations
    assert _NOTE in CleanModule().run(context, CleanConfig()).approximations
    assert _NOTE in QualityModule().run(context, QualityConfig()).approximations
    assert _NOTE in earned_value(schedule).approximations
    other = replace(schedule, parse_notes=("nota del update",))
    compared = CompareModule().run(
        AnalysisContext(schedule=schedule, other=other),
        CompareConfig(),
    )
    assert _NOTE in compared.approximations
    assert "nota del update" in compared.approximations
