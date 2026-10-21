"""Each gate control has a case that passes and a case that fails."""

from __future__ import annotations

from pathlib import Path

from scripts.qa_gate import USER_PROFILE_RE, check_g7, check_g8, check_g9

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_AGENTS = {
    "xer-io",
    "motor-cpm",
    "logica-red",
    "calidad",
    "riesgo",
    "recursos-evm",
    "ui-reportes",
    "fixtures",
    "qa-spec",
    "qa-oraculo",
    "qa-revisor",
    "qa-sabotaje",
    "qa-privacidad",
}

PROFILE_SAMPLE = r"C:\Users\example\AtlasPMO"


def test_thirteen_agents_point_at_the_v2_spec():
    names = {path.stem for path in (ROOT / ".grok" / "agents").glob("*.md")}
    assert names == EXPECTED_AGENTS
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "docs/MEGAPROMPT_v2.md" in text


def test_profile_pattern_matches_a_real_shape_and_ignores_the_ellipsis():
    assert USER_PROFILE_RE.search(PROFILE_SAMPLE)
    assert USER_PROFILE_RE.search(r"C:\Users\...") is None


def _streamlit(root: Path) -> None:
    folder = root / ".streamlit"
    folder.mkdir(parents=True)
    (folder / "config.toml").write_text(
        '[server]\naddress = "localhost"\n\n[browser]\ngatherUsageStats = false\n',
        encoding="utf-8",
    )


def test_g8_fails_on_a_schedule_outside_fixtures(tmp_path: Path):
    _streamlit(tmp_path)
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "XER_SPEC.md").write_text("PROJECT\n", encoding="utf-8")
    leaked = tmp_path / "notes.xer"
    leaked.write_text("ERMHDR\t20.12\r\n%E\r\n", encoding="cp1252")
    result = check_g8(tmp_path)
    assert result.status == "fail"
    assert "notes.xer" in result.detail


def test_g8_passes_a_tree_without_schedules(tmp_path: Path):
    _streamlit(tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    result = check_g8(tmp_path)
    assert result.status == "pass"


def test_g7_fails_when_a_skip_is_not_listed(tmp_path: Path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_demo.py").write_text(
        "import pytest\n\n@pytest.mark.skip(reason='x')\ndef test_a():\n    assert True\n",
        encoding="utf-8",
    )
    result = check_g7(tmp_path)
    assert result.status == "fail"


def test_g7_passes_when_nothing_is_skipped(tmp_path: Path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_demo.py").write_text("def test_a():\n    assert True\n", encoding="utf-8")
    result = check_g7(tmp_path)
    assert result.status == "pass"


def test_g9_fails_when_a_table_is_missing_from_the_spec(tmp_path: Path):
    io = tmp_path / "src" / "atlaspmo" / "io"
    io.mkdir(parents=True)
    (io / "reader.py").write_text('TABLE = "PROJECT"\n', encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "XER_SPEC.md").write_text("Sin tablas.\n", encoding="utf-8")
    result = check_g9(tmp_path)
    assert result.status == "fail"
    assert "PROJECT" in result.detail
