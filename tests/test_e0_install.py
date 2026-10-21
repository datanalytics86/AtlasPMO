"""The dev group is importable, and the install was recorded without admin rights."""

from __future__ import annotations

from pathlib import Path

import hypothesis
import pytest_benchmark
import pytest_cov

ROOT = Path(__file__).resolve().parents[1]


def test_dev_tools_import_and_the_install_was_recorded():
    text = (ROOT / "docs" / "qa" / "E0" / "acciones.md").read_text(encoding="utf-8")
    assert "uv sync --group dev" in text
    assert "sin administrador" in text
    assert hypothesis.__name__ == "hypothesis"
    assert pytest_benchmark.__name__ == "pytest_benchmark"
    assert pytest_cov.__name__ == "pytest_cov"
