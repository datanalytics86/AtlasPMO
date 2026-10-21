"""The omission policy stays declared. This file does not add a skip."""

from __future__ import annotations

from pathlib import Path

from scripts.run_conformance import main

ROOT = Path(__file__).resolve().parents[1]


def test_skip_policy_names_the_allowed_reasons() -> None:
    text = (ROOT / "docs" / "qa" / "skips.toml").read_text(encoding="utf-8")
    assert text.startswith("# Omisiones aceptadas por G7.")
    assert "dependencia_opcional" in text
    assert "fixture_nicolas" in text
    assert "plataforma" in text


def test_missing_p6_verified_is_omitted(capsys) -> None:
    source = (ROOT / "scripts" / "run_conformance.py").read_text(encoding="utf-8")
    assert 'print("p6_verified: omitido")' in source
    folder = ROOT / "tests" / "fixtures" / "p6_verified"
    aside = folder.with_name("p6_verified_aside")
    folder.rename(aside)
    try:
        assert main([]) == 0
        assert "p6_verified: omitido" in capsys.readouterr().out
    finally:
        aside.rename(folder)
