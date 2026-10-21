"""The manifest records the run and does not rewrite the input XER."""

from __future__ import annotations

import json
from pathlib import Path

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.bootstrap import bootstrap
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.reports.export import excel_bytes, write_manifest
from atlaspmo.runner import run_selected

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "synthetic" / "minimal.xer"


def test_manifest_leaves_the_input_bytes_unchanged(tmp_path: Path) -> None:
    bootstrap()
    source = tmp_path / "in.xer"
    source.write_bytes(FIXTURE.read_bytes())
    before = source.read_bytes()
    schedule = schedule_from_xer(read_xer(source))
    results = run_selected(["quality"], AnalysisContext(schedule=schedule, input_name=source.name))
    write_manifest(tmp_path / "run_manifest.json", results, source, ROOT)
    assert source.read_bytes() == before
    payload = json.loads((tmp_path / "run_manifest.json").read_text(encoding="utf-8"))
    assert payload["input_name"] == "in.xer"
    assert payload["input_sha256"]
    assert payload["modules"] == ["quality"]
    assert excel_bytes(results).startswith(b"PK")
