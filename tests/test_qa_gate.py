"""Each gate control has a case that passes and a case that fails."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.qa_gate import (
    USER_PROFILE_RE,
    check_g1,
    check_g2,
    check_g3,
    check_g4,
    check_g5,
    check_g6,
    check_g7,
    check_g8,
    check_g9,
    check_g10,
    check_g11,
    check_g12,
    check_g13,
    judge_coverage,
)

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


def test_g9_passes_when_the_table_is_documented(tmp_path: Path):
    io = tmp_path / "src" / "atlaspmo" / "io"
    io.mkdir(parents=True)
    (io / "reader.py").write_text('TABLE = "PROJECT"\n', encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "XER_SPEC.md").write_text("PROJECT es una tabla.\n", encoding="utf-8")
    assert check_g9(tmp_path).status == "pass"


def test_g8_fails_on_a_network_import(tmp_path: Path):
    _streamlit(tmp_path)
    src = tmp_path / "src"
    src.mkdir()
    (src / "app.py").write_text("import socket\n", encoding="utf-8")
    result = check_g8(tmp_path)
    assert result.status == "fail"
    assert "socket" in result.detail


def test_project_config_denies_real_data_and_dotenv():
    text = (ROOT / ".grok" / "config.toml").read_text(encoding="utf-8")
    for tool in ("Read", "Edit", "Grep"):
        assert f"{tool}(**/data/real/**)" in text
        assert f"{tool}(**/.env)" in text


def test_g1_fails_on_an_unused_import(tmp_path: Path):
    (tmp_path / "bad.py").write_text("import os\n", encoding="utf-8")
    assert check_g1(tmp_path).status == "fail"


def test_g1_passes_a_clean_tree(tmp_path: Path):
    (tmp_path / "ok.py").write_text("x = 1\n", encoding="utf-8")
    assert check_g1(tmp_path).status == "pass"


def test_g2_fails_on_a_bad_return(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "bad.py").write_text("def f() -> int:\n    return 'a'\n", encoding="utf-8")
    assert check_g2(tmp_path).status == "fail"


def test_g2_passes_a_typed_module(tmp_path: Path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "ok.py").write_text("def f() -> int:\n    return 1\n", encoding="utf-8")
    assert check_g2(tmp_path).status == "pass"


def _completed(command: list[str], code: int, stdout: str) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, code, stdout, "")


def test_g3_fails_when_pytest_fails(tmp_path: Path, monkeypatch):
    def fake(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
        return _completed(command, 1, "1 failed")

    monkeypatch.setattr("scripts.qa_gate._run", fake)
    assert check_g3(tmp_path).status == "fail"


def test_g3_passes_when_pytest_passes_and_uv_is_unavailable(tmp_path: Path, monkeypatch):
    def fake(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
        if command[:3] == [sys.executable, "-m", "pytest"]:
            return _completed(command, 0, "1 passed")
        return _completed(command, 127, "No module named uv")

    monkeypatch.setattr("scripts.qa_gate._run", fake)
    result = check_g3(tmp_path)
    assert result.status == "pass"
    assert "ADR-004" in result.detail


def test_g4_fails_when_pytest_fails(tmp_path: Path, monkeypatch):
    def fake(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
        return _completed(command, 1, "1 failed")

    monkeypatch.setattr("scripts.qa_gate._run", fake)
    assert check_g4(tmp_path).status == "fail"


def _coverage(bucket_file: str, missing_lines: int) -> dict[str, object]:
    return {
        "files": {
            bucket_file: {
                "summary": {
                    "num_statements": 100,
                    "missing_lines": missing_lines,
                    "num_branches": 20,
                    "missing_branches": 0,
                }
            }
        }
    }


def test_judge_coverage_fails_under_the_engine_line(tmp_path: Path):
    result = judge_coverage(_coverage("src/atlaspmo/engine/cpm.py", 20))
    assert result.status == "fail"
    assert "engine" in result.detail


def test_judge_coverage_passes_when_thresholds_hold():
    result = judge_coverage(_coverage("src/atlaspmo/engine/cpm.py", 0))
    assert result.status == "pass"


def test_g4_passes_when_the_json_meets_the_threshold(tmp_path: Path, monkeypatch):
    def fake(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
        payload = _coverage("src/atlaspmo/engine/cpm.py", 0)
        (root / "coverage-gate.json").write_text(json.dumps(payload), encoding="utf-8")
        return _completed(command, 0, "1 passed")

    monkeypatch.setattr("scripts.qa_gate._run", fake)
    assert check_g4(tmp_path).status == "pass"
    assert not (tmp_path / "coverage-gate.json").exists()


def test_g5_fails_without_property_tests(tmp_path: Path):
    assert check_g5(tmp_path).status == "fail"


def test_g5_passes_when_the_five_invariants_use_the_qa_profile(tmp_path: Path):
    folder = tmp_path / "tests" / "property"
    folder.mkdir(parents=True)
    (folder / "test_props.py").write_text(
        "\n".join(
            [
                "from hypothesis import settings",
                "settings.register_profile('qa', max_examples=500)",
                "def test_round_trip():",
                "    assert 'round_trip'",
                "def test_clean_unchanged():",
                "    assert 'clean_unchanged'",
                "def test_implicit_redundant():",
                "    assert 'implicit_redundant'",
                "def test_driving_not_redundant():",
                "    assert 'driving_not_redundant'",
                "def test_zero_variance():",
                "    assert 'zero_variance'",
                "",
            ]
        ),
        encoding="utf-8",
    )
    assert check_g5(tmp_path).status == "pass"


def test_g6_fails_without_perf_tests(tmp_path: Path):
    assert check_g6(tmp_path).status == "fail"


def test_g6_passes_a_marked_perf_test(tmp_path: Path):
    folder = tmp_path / "tests" / "perf"
    folder.mkdir(parents=True)
    (folder / "test_fast.py").write_text(
        "import pytest\n\n@pytest.mark.perf\ndef test_fast():\n    assert True\n",
        encoding="utf-8",
    )
    (tmp_path / "pytest.ini").write_text(
        "[pytest]\nmarkers =\n    perf: benchmark\n",
        encoding="utf-8",
    )
    assert check_g6(tmp_path).status == "pass"


def _trace(root: Path, row: str) -> None:
    qa = root / "docs" / "qa"
    qa.mkdir(parents=True)
    (qa / "TRAZABILIDAD.md").write_text(
        "| ID | Etapa | Requisito | Test | Oráculo |\n" + row + "\n",
        encoding="utf-8",
    )


def test_g10_fails_when_the_cited_file_is_missing(tmp_path: Path):
    _trace(tmp_path, "| R-001 | E9 | x | tests/no_such.py | y |")
    assert check_g10(tmp_path, "E9").status == "fail"


def test_g10_passes_when_the_cited_file_exists(tmp_path: Path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_ok.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")
    _trace(tmp_path, "| R-001 | E9 | x | tests/test_ok.py::test_ok | y |")
    assert check_g10(tmp_path, "E9").status == "pass"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def _repo(root: Path) -> None:
    _git(root, "init")
    _git(root, "config", "user.email", "qa@example.com")
    _git(root, "config", "user.name", "qa")


def test_g11_passes_when_no_protected_path_changed(tmp_path: Path):
    _repo(tmp_path)
    (tmp_path / "README.md").write_text("hola\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    _git(tmp_path, "commit", "-m", "docs: readme")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True).strip()
    assert check_g11(tmp_path, head).status == "pass"


def test_g11_fails_when_the_gate_commit_omits_an_adr(tmp_path: Path):
    _repo(tmp_path)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    gate = scripts / "qa_gate.py"
    gate.write_text("x = 1\n", encoding="utf-8")
    _git(tmp_path, "add", "scripts/qa_gate.py")
    _git(tmp_path, "commit", "-m", "feat: base")
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp_path, text=True).strip()
    gate.write_text("x = 2\n", encoding="utf-8")
    _git(tmp_path, "add", "scripts/qa_gate.py")
    _git(tmp_path, "commit", "-m", "fix: gate sin cita")
    assert check_g11(tmp_path, base).status == "fail"


def test_g12_passes_on_e0_without_a_previous_stage(tmp_path: Path):
    assert check_g12(tmp_path, "E0").status == "pass"


def test_g12_fails_when_the_count_drops(tmp_path: Path, monkeypatch):
    folder = tmp_path / "docs" / "qa" / "E0"
    folder.mkdir(parents=True)
    (folder / "gate.json").write_text('{"test_count": 40}', encoding="utf-8")

    def fake(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
        return _completed(command, 0, "3 passed")

    monkeypatch.setattr("scripts.qa_gate._run", fake)
    assert check_g12(tmp_path, "E1").status == "fail"


def test_g12_passes_when_the_count_holds(tmp_path: Path, monkeypatch):
    folder = tmp_path / "docs" / "qa" / "E0"
    folder.mkdir(parents=True)
    (folder / "gate.json").write_text('{"test_count": 3}', encoding="utf-8")

    def fake(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
        return _completed(command, 0, "10 passed")

    monkeypatch.setattr("scripts.qa_gate._run", fake)
    assert check_g12(tmp_path, "E1").status == "pass"


def _sabotage(root: Path, etapa: str, text: str) -> None:
    folder = root / "docs" / "qa" / etapa
    folder.mkdir(parents=True)
    (folder / "sabotaje.md").write_text(text, encoding="utf-8")


def test_g13_fails_without_a_report(tmp_path: Path):
    assert check_g13(tmp_path, "E0").status == "fail"


def test_g13_fails_on_a_sample(tmp_path: Path):
    _sabotage(tmp_path, "E0", "alcance: muestra\nkill_score: 100\n")
    assert check_g13(tmp_path, "E0").status == "fail"


def test_g13_fails_under_the_threshold(tmp_path: Path):
    _sabotage(tmp_path, "E0", "alcance: completo\nkill_score: 10\nengine: 10\n")
    assert check_g13(tmp_path, "E0").status == "fail"


def test_g13_passes_a_complete_score_at_the_threshold(tmp_path: Path):
    _sabotage(tmp_path, "E0", "alcance: completo\nkill_score: 90\nengine: 90\n")
    assert check_g13(tmp_path, "E0").status == "pass"
