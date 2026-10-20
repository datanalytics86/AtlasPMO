"""The phase-0 conformance script must not read schedules."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "run_conformance",
    ROOT / "scripts" / "run_conformance.py",
)
assert SPEC is not None and SPEC.loader is not None
stub = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stub)


def test_stub_exits_and_leaves_files_untouched(tmp_path: Path, monkeypatch, capsys):
    secret = tmp_path / "secret.xer"
    secret.write_bytes(b"SECRET")
    monkeypatch.setenv("ATLASPMO_GOLDEN_DIR", str(tmp_path))
    assert stub.main() == 0
    assert secret.read_bytes() == b"SECRET"
    assert "secret" not in capsys.readouterr().out
