"""Section 11 conformance is not measured in this run."""

from __future__ import annotations

from pathlib import Path

from scripts.run_conformance import main

ROOT = Path(__file__).resolve().parents[1]


def test_golden_folder_is_not_opened(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.delenv("ATLASPMO_GOLDEN_DIR", raising=False)
    assert main([]) == 0
    assert "golden: omitido" in capsys.readouterr().out
    folder = tmp_path / "caja"
    folder.mkdir()
    secret = folder / "secreto.xer"
    secret.write_bytes(b"SECRET")
    monkeypatch.setenv("ATLASPMO_GOLDEN_DIR", str(folder))
    assert main([]) == 0
    captured = capsys.readouterr().out
    assert "esta corrida no abre esa carpeta" in captured
    assert "secreto" not in captured
    assert secret.read_bytes() == b"SECRET"
    source = (ROOT / "scripts" / "run_conformance.py").read_text(encoding="utf-8")
    branch = source.split('os.environ.get("ATLASPMO_GOLDEN_DIR")', 1)[1]
    assert "iterdir" not in branch
    assert "listdir" not in branch
    assert "scandir" not in branch
    assert "glob" not in branch
    assert "read_" not in branch
