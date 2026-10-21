"""Schedule files stay inside tests/fixtures."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "reject_schedules",
    ROOT / "scripts" / "hooks" / "reject_schedules.py",
)
assert SPEC is not None
assert SPEC.loader is not None
hook = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hook)


def test_fixture_xer_is_allowed():
    assert hook.forbidden_reason("tests/fixtures/synthetic/minimal.xer") is None


def test_xer_outside_fixtures_is_rejected():
    reason = hook.forbidden_reason("notes/real.xer")
    assert reason is not None
    assert "outside" in reason


def test_parent_traversal_is_rejected():
    reason = hook.forbidden_reason("tests/fixtures/../secret.xer")
    assert reason is not None


def test_p6_xml_outside_fixtures_is_rejected(tmp_path: Path):
    path = tmp_path / "export.xml"
    path.write_bytes(b"<APIBusinessObjects></APIBusinessObjects>")
    assert hook.main([str(path)]) == 1


def test_plain_xml_is_allowed(tmp_path: Path):
    path = tmp_path / "note.xml"
    path.write_bytes(b"<note>hello</note>")
    assert hook.main([str(path)]) == 0


def test_env_and_real_data_are_rejected():
    assert hook.forbidden_reason(".env") is not None
    assert hook.forbidden_reason("notes/.env.local") is not None
    assert hook.forbidden_reason("data/real/plan.xer") is not None


def test_mspdi_marker_is_rejected(tmp_path: Path):
    path = tmp_path / "plan.xml"
    path.write_bytes(b'<Project xmlns="http://schemas.microsoft.com/project">')
    assert hook.main([str(path)]) == 1
