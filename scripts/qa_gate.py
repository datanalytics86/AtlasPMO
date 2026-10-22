"""Automatic QA gate for one AtlasPMO stage.

The user-profile pattern lives only in this file and in tests/test_qa_gate.py.
Those two paths are excluded from G8.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import shutil
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

# G8: absolute profile paths. The pattern stays here and in the gate tests.
USER_PROFILE_RE = re.compile(
    r"(?i)(?:[A-Za-z]:\\Users\\[A-Za-z0-9][A-Za-z0-9._-]*|/(?:home|Users)/[A-Za-z0-9][A-Za-z0-9._-]*)"
)
G8_EXCLUDED = {
    "scripts/qa_gate.py",
    "tests/test_qa_gate.py",
}
ANON_ERMHDR = re.compile(r"^(?:ANON|\d+\.\d+)?$")
NETWORK_IMPORTS = {
    "socket",
    "requests",
    "httpx",
    "aiohttp",
    "http.client",
    "urllib.request",
}
P6_TABLES = {
    "PROJECT",
    "CALENDAR",
    "PROJWBS",
    "TASK",
    "TASKPRED",
    "RSRC",
    "TASKRSRC",
    "RSRCRATE",
    "ACTVTYPE",
    "ACTVCODE",
    "TASKACTV",
    "UDFTYPE",
    "UDFVALUE",
    "RSRCCURVDATA",
}
FIELD_RE = re.compile(
    r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*(?:_hr_cnt|_date|_id|_type|_code|_name|_pct|_flag|_qty|_cost|_data|_order)$"
)
XER_FIELD_ROOTS = (
    "src/atlaspmo/io/",
    "src/atlaspmo/model/",
    "src/atlaspmo/calendars/",
)
PROTECTED_GLOBS = (
    "tests/fixtures/**/expected*",
    "tests/oracle/**",
    "docs/qa/skips.toml",
    "profiles/*.yaml",
    "scripts/qa_gate.py",
)
E0_BASELINE = {"G4", "G5", "G6", "G10", "G13"}
# v3 (ADR-019): coverage is a ratchet over this file; section 11 targets are
# enforced only once a stage lists them as active.
BASELINE_FILE = "docs/qa/baseline.json"
SECCION11_FILE = "docs/qa/seccion11.toml"
SECCION11_TESTS = "tests/perf/test_seccion11.py"
RATCHET_SLACK = 0.5
SKIP_REASONS = {"dependencia_opcional", "fixture_nicolas", "plataforma"}
INVARIANTS = {
    "a": "round_trip",
    "b": "clean_unchanged",
    "c": "implicit_redundant",
    "d": "driving_not_redundant",
    "e": "zero_variance",
}


@dataclass
class Control:
    id: str
    status: str
    detail: str

    @property
    def ok(self) -> bool:
        return self.status in {"pass", "linea_base", "info"}


def _root() -> Path:
    return Path(__file__).resolve().parents[1]


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _run(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return subprocess.CompletedProcess(command, 127, "", str(exc))


def _spawn_failed(proc: subprocess.CompletedProcess[str]) -> bool:
    blob = f"{proc.stdout}\n{proc.stderr}"
    return proc.returncode != 0 and ("os error 5" in blob or "Failed to spawn" in blob)


def check_g1(root: Path) -> Control:
    check = _run([sys.executable, "-m", "ruff", "check", "."], root)
    fmt = _run([sys.executable, "-m", "ruff", "format", "--check", "."], root)
    if check.returncode == 0 and fmt.returncode == 0:
        return Control("G1", "pass", "ruff check y ruff format --check en verde")
    tail = (check.stdout + check.stderr + fmt.stdout + fmt.stderr)[-1500:]
    return Control("G1", "fail", tail)


def check_g2(root: Path) -> Control:
    proc = _run([sys.executable, "-m", "mypy", "src"], root)
    if proc.returncode == 0:
        return Control("G2", "pass", "mypy src sin errores")
    return Control("G2", "fail", (proc.stdout + proc.stderr)[-1500:])


def _uv_pytest_commands() -> list[list[str]]:
    commands: list[list[str]] = []
    if shutil.which("uv"):
        commands.append(["uv", "run", "pytest", "-q"])
    commands.append(["py", "-3.12", "-m", "uv", "run", "pytest", "-q"])
    return commands


def _environment_gap(proc: subprocess.CompletedProcess[str]) -> bool:
    blob = f"{proc.stdout}\n{proc.stderr}"
    return (
        _spawn_failed(proc)
        or proc.returncode == 127
        or "No module named uv" in blob
        or "WinError 2" in blob
    )


def check_g3(root: Path) -> Control:
    module = _run([sys.executable, "-m", "pytest", "-q"], root)
    notes = [f"python -m pytest exit {module.returncode}"]
    if module.returncode != 0:
        notes.append((module.stdout + module.stderr)[-800:])
        return Control("G3", "fail", "\n".join(notes))
    for command in _uv_pytest_commands():
        direct = _run(command, root)
        if direct.returncode == 0:
            notes.append("uv run pytest exit 0")
            return Control("G3", "pass", "\n".join(notes))
        if not _environment_gap(direct):
            notes.append((direct.stdout + direct.stderr)[-800:])
            return Control("G3", "fail", "\n".join(notes))
    notes.append("uv run pytest no arranca aqui (ADR-004); corrio python -m pytest")
    return Control("G3", "pass", "\n".join(notes))


_STRICT_LINES = 90.0
_STRICT_BRANCHES = 85.0
_REST_LINES = 80.0
_STRICT_BUCKETS = {"model", "calendars", "engine", "logic"}


def _coverage_bucket(path: str) -> str:
    rel = path.replace("\\", "/")
    marker = "atlaspmo/"
    if marker not in rel:
        return "resto"
    tail = rel.split(marker, 1)[1]
    if tail.startswith("analysis/logic/"):
        return "logic"
    top = tail.split("/", 1)[0]
    if top in {"model", "calendars", "engine"}:
        return top
    return "resto"


def _pct(missing: int, total: int) -> float:
    if total == 0:
        return 100.0
    return 100.0 * (total - missing) / total


def judge_coverage(
    data: dict[str, object],
    baseline: dict[str, dict[str, float]] | None = None,
) -> Control:
    """Apply section 8.1 to a coverage JSON payload. Never invents a pass.

    With a baseline, each bucket may sit under the section 8.1 target but
    never more than RATCHET_SLACK points under its recorded baseline.
    """
    files = data.get("files")
    if not isinstance(files, dict) or not files:
        return Control("G4", "fail", "sin archivos medidos")
    totals: dict[str, list[int]] = {}
    for name, info in files.items():
        if not isinstance(info, dict):
            continue
        summary = info.get("summary")
        if not isinstance(summary, dict):
            continue
        bucket = _coverage_bucket(str(name))
        slot = totals.setdefault(bucket, [0, 0, 0, 0])
        slot[0] += int(summary.get("num_statements", 0))
        slot[1] += int(summary.get("missing_lines", 0))
        slot[2] += int(summary.get("num_branches", 0))
        slot[3] += int(summary.get("missing_branches", 0))
    if not totals:
        return Control("G4", "fail", "sin archivos medidos")
    problems: list[str] = []
    notes: list[str] = []
    gaps: list[str] = []
    for bucket, (stmts, miss, branches, bmiss) in sorted(totals.items()):
        lines = _pct(miss, stmts)
        branch = _pct(bmiss, branches)
        notes.append(f"{bucket} lineas {lines:.1f}% ramas {branch:.1f}%")
        strict = bucket in _STRICT_BUCKETS
        targets = [("lineas", lines, _STRICT_LINES if strict else _REST_LINES)]
        if strict and branches:
            targets.append(("ramas", branch, _STRICT_BRANCHES))
        recorded = (baseline or {}).get(bucket, {})
        for kind, value, target in targets:
            floor = target
            if baseline is not None and kind in recorded:
                floor = min(target, float(recorded[kind]) - RATCHET_SLACK)
            if value < floor:
                problems.append(f"{bucket} {kind} {value:.1f} < {floor:.1f}")
            elif value < target:
                gaps.append(f"{bucket} {kind} {value:.1f} bajo la meta {target:.0f}")
    measured = _pct(
        sum(slot[1] for slot in totals.values()), sum(slot[0] for slot in totals.values())
    )
    detail = f"cobertura_total: {measured:.1f}; " + "; ".join(notes)
    if gaps:
        detail += " | meta pendiente: " + "; ".join(gaps)
    if problems:
        return Control("G4", "fail", "; ".join(problems) + " | " + detail)
    return Control("G4", "pass", detail)


def check_g4(root: Path) -> Control:
    report = root / "coverage-gate.json"
    proc = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--cov=src/atlaspmo",
            "--cov-branch",
            "--cov-report=term-missing",
            f"--cov-report=json:{report.name}",
        ],
        root,
    )
    text = proc.stdout + proc.stderr
    try:
        if proc.returncode != 0:
            return Control("G4", "fail", text[-1500:])
        if not report.is_file():
            return Control("G4", "fail", "pytest en verde sin coverage-gate.json")
        judged = judge_coverage(
            json.loads(report.read_text(encoding="utf-8")), _coverage_baseline(root)
        )
        return Control("G4", judged.status, judged.detail + " | " + text[-400:])
    finally:
        report.unlink(missing_ok=True)
        dot = root / ".coverage"
        if dot.is_file():
            dot.unlink()


def _coverage_baseline(root: Path) -> dict[str, dict[str, float]] | None:
    path = root / BASELINE_FILE
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    buckets = data.get("buckets") if isinstance(data, dict) else None
    return buckets if isinstance(buckets, dict) else None


def check_g5(root: Path) -> Control:
    folder = root / "tests" / "property"
    missing = []
    if not folder.is_dir():
        missing.append("no existe tests/property")
    else:
        blob = "\n".join(path.read_text(encoding="utf-8") for path in folder.glob("*.py"))
        examples = _qa_examples(blob)
        for key, token in INVARIANTS.items():
            if token not in blob or "qa" not in blob:
                missing.append(f"invariante {key} ({token}) sin perfil qa")
        if examples is None or examples < 500:
            missing.append(f"perfil qa con {examples} ejemplos; hacen falta 500")
    if missing:
        return Control("G5", "fail", "; ".join(missing))
    return Control("G5", "pass", "invariantes a-e con perfil qa")


def _qa_examples(blob: str) -> int | None:
    match = re.search(
        r"register_profile\(\s*['\"]qa['\"][^)]*max_examples\s*=\s*(\d+)",
        blob,
    )
    if match:
        return int(match.group(1))
    loose = re.search(r"max_examples\s*=\s*(\d+)", blob)
    if loose and "qa" in blob:
        return int(loose.group(1))
    return None


def check_g6(root: Path) -> Control:
    perf = root / "tests" / "perf"
    if not perf.is_dir() or not any(perf.glob("test_*.py")):
        return Control("G6", "fail", "no medido: no hay tests/perf")
    proc = _run([sys.executable, "-m", "pytest", "-q", "-m", "perf", "tests/perf"], root)
    text = (proc.stdout + proc.stderr)[-1500:]
    if proc.returncode != 0:
        return Control("G6", "fail", text)
    targets = _section11_targets(root)
    if not targets:
        return Control("G6", "pass", text + "\nseccion11: sin metas activas")
    selector = " or ".join(f"test_s11_{name}" for name in targets)
    s11 = _run(
        [sys.executable, "-m", "pytest", "-q", "-m", "seccion11", SECCION11_TESTS, "-k", selector],
        root,
    )
    s11_text = (s11.stdout + s11.stderr)[-1500:]
    ran = _passed_count(s11.stdout) + len(re.findall(r"\bFAILED\b", s11.stdout))
    if s11.returncode != 0 or ran < len(targets):
        return Control("G6", "fail", f"seccion11 activas {targets}: " + s11_text)
    return Control("G6", "pass", text + f"\nseccion11 activas {targets}: " + s11_text)


def _section11_targets(root: Path) -> list[str]:
    path = root / SECCION11_FILE
    if not path.is_file():
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    active = data.get("activas", [])
    return [str(item) for item in active] if isinstance(active, list) else []


def _mark_name(node: ast.AST) -> str:
    current = node
    if isinstance(current, ast.Call):
        current = current.func
    if isinstance(current, ast.Attribute):
        return current.attr
    if isinstance(current, ast.Name):
        return current.id
    return ""


def _skipped_tests(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            continue
        marks: list[ast.AST] = list(node.decorator_list)
        marks.extend(child for child in ast.walk(node) if isinstance(child, ast.Call))
        if any(_mark_name(mark) in {"skip", "skipif", "xfail"} for mark in marks):
            names.append(node.name)
    return names


def _skip_listed(call: str, item: str) -> bool:
    return bool(item) and (
        item == call or item.startswith(call + "[") or item.startswith(call + " ")
    )


def check_g7(root: Path) -> Control:
    calls: list[str] = []
    tests = root / "tests"
    if tests.is_dir():
        for path in tests.rglob("*.py"):
            rel = _rel(path, root)
            calls.extend(f"{rel}::{name}" for name in _skipped_tests(path))
    listed = _skip_table(root)
    if not calls and not listed:
        return Control("G7", "pass", "no hay skip ni xfail")
    problems: list[str] = []
    listed_ids: list[str] = []
    for row in listed:
        reason = str(row.get("motivo", ""))
        if reason not in SKIP_REASONS:
            problems.append(f"motivo no aceptado: {reason}")
        listed_ids.append(str(row.get("test", "")))
    for call in calls:
        if not any(_skip_listed(call, item) for item in listed_ids):
            problems.append(f"skip sin fila: {call}")
    if problems:
        return Control("G7", "fail", "; ".join(problems))
    return Control("G7", "pass", f"{len(listed)} omisiones listadas; {len(calls)} marcas en tests")


def _skip_table(root: Path) -> list[dict[str, object]]:
    path = root / "docs" / "qa" / "skips.toml"
    if not path.is_file():
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    rows = data.get("skip", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def check_g8(root: Path) -> Control:
    problems: list[str] = []
    for path in _versioned(root):
        rel = _rel(path, root)
        if rel in G8_EXCLUDED or rel.startswith("tests/fixtures/"):
            continue
        suffix = path.suffix.lower()
        if suffix in {".xer", ".mpp"}:
            problems.append(f"{rel}: cronograma fuera de tests/fixtures")
        if suffix == ".xml":
            content = path.read_bytes()
            markers = (b"APIBusinessObjects", b"http://schemas.microsoft.com/project")
            if any(marker in content for marker in markers):
                problems.append(f"{rel}: XML de cronograma fuera de tests/fixtures")
        if rel.startswith("data/real/") or path.name == ".env" or rel.endswith("/.env"):
            problems.append(f"{rel}: archivo privado")
        if suffix in {".py", ".md", ".toml", ".yaml", ".yml", ".bat", ".json"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            if USER_PROFILE_RE.search(text):
                problems.append(f"{rel}: ruta de perfil de usuario")
    for path in (root / "tests" / "fixtures").rglob("*.xer"):
        first = path.read_text(encoding="cp1252", errors="replace").splitlines()[:1]
        header = first[0] if first else ""
        if not header.startswith("ERMHDR"):
            problems.append(f"{_rel(path, root)}: sin ERMHDR")
            continue
        for field in header.split("\t")[1:]:
            if not ANON_ERMHDR.match(field):
                problems.append(f"{_rel(path, root)}: ERMHDR no anonimo")
    problems.extend(_network_imports(root))
    config = root / ".streamlit" / "config.toml"
    if config.is_file():
        text = config.read_text(encoding="utf-8")
        if 'address = "localhost"' not in text or "gatherUsageStats = false" not in text:
            problems.append(".streamlit/config.toml no fija localhost sin estadisticas")
    else:
        problems.append("falta .streamlit/config.toml")
    if problems:
        return Control("G8", "fail", "; ".join(problems[:30]))
    return Control("G8", "pass", "sin cronogramas fuera de fixtures, sin rutas de perfil, sin red")


def _versioned(root: Path) -> list[Path]:
    proc = _run(["git", "ls-files"], root)
    if proc.returncode != 0:
        return [path for path in root.rglob("*") if path.is_file() and ".git" not in path.parts]
    found = []
    for line in proc.stdout.splitlines():
        path = root / line
        if path.is_file():
            found.append(path)
    return found


def _network_imports(root: Path) -> list[str]:
    problems: list[str] = []
    for path in (root / "src").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            else:
                continue
            for name in names:
                if name in NETWORK_IMPORTS or name.split(".")[0] in {
                    "requests",
                    "httpx",
                    "aiohttp",
                }:
                    problems.append(f"{_rel(path, root)}: import {name}")
    return problems


def check_g9(root: Path) -> Control:
    spec = root / "docs" / "XER_SPEC.md"
    if not spec.is_file():
        return Control("G9", "fail", "falta docs/XER_SPEC.md")
    documented = spec.read_text(encoding="utf-8")
    missing: list[str] = []
    for path in (root / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        rel = _rel(path, root)
        for token in set(re.findall(r"""['"]([A-Za-z][A-Za-z0-9_]*)['"]""", text)):
            if token.startswith(("duplicate_", "missing_", "open_", "no_")):
                continue
            is_table = token in P6_TABLES
            is_field = rel.startswith(XER_FIELD_ROOTS) and bool(FIELD_RE.match(token))
            if (is_table or is_field) and token not in documented:
                missing.append(f"{rel}:{token}")
    if missing:
        return Control("G9", "fail", "; ".join(sorted(missing)[:40]))
    return Control("G9", "pass", "tablas y campos literales de src/ estan en XER_SPEC.md")


def _cited_test_files(line: str) -> list[str]:
    parts = [part.strip() for part in line.split("|")]
    cell = parts[4] if len(parts) > 4 else ""
    return re.findall(r"tests/[A-Za-z0-9_./-]+\.py", cell)


def check_g10(root: Path, etapa: str) -> Control:
    path = root / "docs" / "qa" / "TRAZABILIDAD.md"
    if not path.is_file():
        return Control("G10", "fail", "falta TRAZABILIDAD.md")
    rows = [
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith("| R-") and f"| {etapa} |" in line
    ]
    if not rows:
        return Control("G10", "fail", f"sin requisitos de {etapa}")
    missing: list[str] = []
    for line in rows:
        cited = _cited_test_files(line)
        ident = line.split("|")[1].strip()
        if not cited:
            missing.append(f"{ident} sin archivo de test")
            continue
        for rel in cited:
            if not (root / rel).is_file():
                missing.append(f"{ident} {rel}")
    if missing:
        return Control("G10", "fail", "test inexistente: " + ", ".join(missing[:20]))
    return Control(
        "G10",
        "pass",
        f"{len(rows)} requisitos de {etapa} citan un archivo de test que existe. "
        "El verde de la suite lo mide G3.",
    )


def check_g11(root: Path, base: str) -> Control:
    names = _protected_names(root, base)
    if not names:
        return Control("G11", "pass", "rutas protegidas sin cambios")
    log = _run(["git", "log", f"{base}..HEAD", "--format=%s%n%b", "--", *names], root)
    dirty = _run(["git", "diff", "--name-only", "HEAD", "--", *names], root)
    if dirty.stdout.strip():
        return Control("G11", "fail", "cambios sin commit en " + dirty.stdout.replace("\n", ", "))
    if log.returncode != 0:
        return Control("G11", "fail", log.stderr[-500:])
    if not re.search(r"ADR-\d+", log.stdout):
        return Control("G11", "fail", "el commit de rutas protegidas no cita un ADR")
    return Control("G11", "pass", "cambios protegidos citan un ADR")


def _protected_names(root: Path, base: str) -> list[str]:
    proc = _run(["git", "diff", "--name-only", f"{base}...HEAD"], root)
    dirty = _run(["git", "diff", "--name-only", "HEAD"], root)
    names = []
    for line in (proc.stdout + "\n" + dirty.stdout).splitlines():
        if _is_protected(line):
            names.append(line)
    return sorted(set(names))


def _is_protected(rel: str) -> bool:
    rel = rel.replace("\\", "/")
    if rel in {"docs/qa/skips.toml", "scripts/qa_gate.py", BASELINE_FILE, SECCION11_FILE}:
        return True
    if rel.startswith("tests/oracle/"):
        return True
    if rel.startswith("tests/fixtures/") and "expected" in Path(rel).name:
        return True
    return rel.startswith("profiles/") and rel.endswith(".yaml")


def _coverage_percent(detail: str) -> float | None:
    match = re.search(r"cobertura_total:\s*([0-9]+(?:\.[0-9]+)?)", detail)
    if match is None:
        return None
    return float(match.group(1))


def check_g12(
    root: Path,
    etapa: str,
    coverage: float | None = None,
    benchmarks: dict[str, float] | None = None,
) -> Control:
    previous = _previous_gate(root, etapa)
    if previous is None:
        return Control("G12", "pass", "sin etapa anterior; no hay regresion que medir")
    current = _run([sys.executable, "-m", "pytest", "-q"], root)
    count = _passed_count(current.stdout)
    old = int(previous.get("test_count") or 0)
    problems: list[str] = []
    if old and count < old:
        problems.append(f"tests {count} < {old}")
    stored = previous.get("coverage_percent")
    if coverage is not None and isinstance(stored, int | float) and float(stored) - coverage > 0.5:
        problems.append(f"cobertura {coverage:.1f} < {float(stored):.1f} - 0.5")
    old_benchmarks = previous.get("benchmarks")
    if isinstance(old_benchmarks, dict) and benchmarks:
        for key, previous_value in old_benchmarks.items():
            if key not in benchmarks or not isinstance(previous_value, int | float):
                continue
            current_value = float(benchmarks[key])
            if current_value > float(previous_value) * 1.2:
                problems.append(
                    f"benchmark {key} {current_value:.1f} > {float(previous_value):.1f} * 1.2"
                )
    if problems:
        return Control("G12", "fail", "; ".join(problems))
    return Control("G12", "pass", f"tests {count} frente a {old}")


def _passed_count(text: str) -> int:
    match = re.search(r"(\d+) passed", text)
    return int(match.group(1)) if match else 0


def _previous_gate(root: Path, etapa: str) -> dict[str, object] | None:
    number = int(etapa[1:])
    if number == 0:
        return None
    path = root / "docs" / "qa" / f"E{number - 1}" / "gate.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    return None


def check_g13(root: Path, etapa: str) -> Control:
    """Mutation score. Informative since v3 (ADR-019): it never blocks."""
    report = root / "docs" / "qa" / etapa / "sabotaje.md"
    if not report.is_file():
        return Control("G13", "info", "no medido: falta el informe de qa-sabotaje")
    text = report.read_text(encoding="utf-8")
    scope = re.search(r"alcance:\s*(\w+)", text)
    score = re.search(r"kill_score:\s*([0-9]+(?:\.[0-9]+)?)", text)
    if scope is None or scope.group(1) != "completo" or score is None:
        return Control("G13", "info", "no medido: el informe no es una corrida completa")
    value = float(score.group(1))
    problems: list[str] = []
    if value < 70:
        problems.append(f"kill_score {value:.1f} < 70")
    for name, minimum in (("engine", 85), ("calendars", 85), ("logic", 85)):
        found = re.search(rf"^{name}:\s*([0-9]+(?:\.[0-9]+)?)", text, re.MULTILINE)
        if found and float(found.group(1)) < minimum:
            problems.append(f"{name} {found.group(1)} < {minimum}")
    if problems:
        return Control("G13", "info", "; ".join(problems))
    return Control("G13", "pass", f"kill_score {value:.1f} alcance completo")


def run_gate(etapa: str, root: Path | None = None, base: str = "HEAD") -> tuple[list[Control], int]:
    root = root or _root()
    coverage_control = check_g4(root)
    controls = [
        check_g1(root),
        check_g2(root),
        check_g3(root),
        coverage_control,
        check_g5(root),
        check_g6(root),
        check_g7(root),
        check_g8(root),
        check_g9(root),
        check_g10(root, etapa),
        check_g11(root, base),
        check_g12(root, etapa, _coverage_percent(coverage_control.detail)),
        check_g13(root, etapa),
    ]
    if etapa == "E0":
        adjusted = []
        for item in controls:
            if item.id in E0_BASELINE and item.status == "fail":
                adjusted.append(Control(item.id, "linea_base", item.detail))
            else:
                adjusted.append(item)
        controls = adjusted
    blocking = [item for item in controls if item.status == "fail"]
    return controls, (1 if blocking else 0)


def _redact(text: str) -> str:
    return USER_PROFILE_RE.sub("<perfil>", text)


def write_report(etapa: str, controls: list[Control], code: int, root: Path) -> None:
    folder = root / "docs" / "qa" / etapa
    folder.mkdir(parents=True, exist_ok=True)
    payload = {
        "etapa": etapa,
        "exit_code": code,
        "test_count": max((_passed_count(item.detail) for item in controls), default=0),
        "coverage_percent": next(
            (
                value
                for value in (_coverage_percent(item.detail) for item in controls)
                if value is not None
            ),
            None,
        ),
        "benchmarks": {},
        "controls": [
            {"id": item.id, "status": item.status, "detail": _redact(item.detail)}
            for item in controls
        ],
    }
    (folder / "gate.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [f"# Gate {etapa}", "", f"Codigo de salida: {code}", ""]
    for item in controls:
        lines.append(f"- **{item.id}** {item.status}: {_redact(item.detail).splitlines()[0][:240]}")
    (folder / "gate.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate QA de AtlasPMO")
    parser.add_argument("--etapa", required=True)
    parser.add_argument("--base", default="108f11a")
    args = parser.parse_args(argv)
    controls, code = run_gate(args.etapa, base=args.base)
    write_report(args.etapa, controls, code, _root())
    for item in controls:
        print(f"{item.id}\t{item.status}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
