"""Automatic QA gate for one AtlasPMO stage.

The user-profile pattern lives only in this file and in tests/test_qa_gate.py.
Those two paths are excluded from G8.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
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
        return self.status in {"pass", "linea_base"}


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


def check_g3(root: Path) -> Control:
    module = _run([sys.executable, "-m", "pytest", "-q"], root)
    direct = _run([sys.executable, "-m", "uv", "run", "pytest", "-q"], root)
    notes = [f"python -m pytest exit {module.returncode}"]
    if module.returncode != 0:
        notes.append((module.stdout + module.stderr)[-800:])
        return Control("G3", "fail", "\n".join(notes))
    if direct.returncode == 0:
        notes.append("uv run pytest exit 0")
        return Control("G3", "pass", "\n".join(notes))
    if _spawn_failed(direct):
        notes.append(
            "uv run pytest no arranca (os error 5, ADR-004); la suite corrio con python -m pytest"
        )
        return Control("G3", "pass", "\n".join(notes))
    notes.append((direct.stdout + direct.stderr)[-800:])
    return Control("G3", "fail", "\n".join(notes))


def check_g4(root: Path) -> Control:
    proc = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--cov=src/atlaspmo",
            "--cov-branch",
            "--cov-report=term-missing",
        ],
        root,
    )
    text = proc.stdout + proc.stderr
    if proc.returncode != 0:
        return Control("G4", "fail", text[-1500:])
    return Control(
        "G4",
        "linea_base",
        "Cobertura medida. El umbral de la seccion 8.1 no se declara cumplido en E0. "
        + text[-800:],
    )


def check_g5(root: Path) -> Control:
    folder = root / "tests" / "property"
    missing = []
    if not folder.is_dir():
        missing.append("no existe tests/property")
    else:
        blob = "\n".join(path.read_text(encoding="utf-8") for path in folder.glob("*.py"))
        for key, token in INVARIANTS.items():
            if token not in blob or "qa" not in blob:
                missing.append(f"invariante {key} ({token}) sin perfil qa")
            if "max_examples=500" not in blob and 'register_profile("qa"' not in blob:
                missing.append("perfil qa sin 500 ejemplos")
                break
    if missing:
        return Control("G5", "fail", "; ".join(missing))
    return Control("G5", "pass", "invariantes a-e con perfil qa")


def check_g6(root: Path) -> Control:
    perf = root / "tests" / "perf"
    if not perf.is_dir() or not any(perf.glob("test_*.py")):
        return Control("G6", "fail", "no medido: no hay tests/perf")
    proc = _run([sys.executable, "-m", "pytest", "-q", "-m", "perf", "tests/perf"], root)
    text = (proc.stdout + proc.stderr)[-1500:]
    if proc.returncode != 0:
        return Control("G6", "fail", text)
    return Control("G6", "pass", text)


def _skip_calls(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = ""
        func = node.func
        if isinstance(func, ast.Attribute):
            name = func.attr
        elif isinstance(func, ast.Name):
            name = func.id
        if name in {"skip", "skipif", "xfail"}:
            found.append(f"{path}:{node.lineno}:{name}")
    return found


def check_g7(root: Path) -> Control:
    calls: list[str] = []
    for path in (root / "tests").rglob("*.py"):
        calls.extend(_skip_calls(path))
    listed = _skip_table(root)
    if not calls and not listed:
        return Control("G7", "pass", "no hay skip ni xfail")
    problems = []
    for row in listed:
        reason = str(row.get("motivo", ""))
        if reason not in SKIP_REASONS:
            problems.append(f"motivo no aceptado: {reason}")
    if calls and not listed:
        problems.append("hay skip en tests y skips.toml no los lista: " + ", ".join(calls))
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
    open_rows = [line.split("|")[1].strip() for line in rows if "tests/" not in line]
    if open_rows:
        return Control("G10", "fail", "sin test planificado: " + ", ".join(open_rows[:20]))
    return Control(
        "G10", "linea_base", f"{len(rows)} requisitos de {etapa}; el verde se exige desde E1"
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
    if rel in {"docs/qa/skips.toml", "scripts/qa_gate.py"}:
        return True
    if rel.startswith("tests/oracle/"):
        return True
    if rel.startswith("tests/fixtures/") and "expected" in Path(rel).name:
        return True
    return rel.startswith("profiles/") and rel.endswith(".yaml")


def check_g12(root: Path, etapa: str) -> Control:
    previous = _previous_gate(root, etapa)
    if previous is None:
        return Control("G12", "pass", "sin etapa anterior; no hay regresion que medir")
    current = _run([sys.executable, "-m", "pytest", "-q"], root)
    count = _passed_count(current.stdout)
    old = int(previous.get("test_count") or 0)
    if count < old:
        return Control("G12", "fail", f"tests {count} < {old}")
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
    report = root / "docs" / "qa" / etapa / "sabotaje.md"
    if not report.is_file():
        return Control("G13", "fail", "no medido: falta el informe de qa-sabotaje")
    text = report.read_text(encoding="utf-8")
    if "kill_score" not in text:
        return Control("G13", "fail", "el informe no trae kill_score")
    return Control("G13", "pass", text[-500:])


def run_gate(etapa: str, root: Path | None = None, base: str = "HEAD") -> tuple[list[Control], int]:
    root = root or _root()
    controls = [
        check_g1(root),
        check_g2(root),
        check_g3(root),
        check_g4(root),
        check_g5(root),
        check_g6(root),
        check_g7(root),
        check_g8(root),
        check_g9(root),
        check_g10(root, etapa),
        check_g11(root, base),
        check_g12(root, etapa),
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


def write_report(etapa: str, controls: list[Control], code: int, root: Path) -> None:
    folder = root / "docs" / "qa" / etapa
    folder.mkdir(parents=True, exist_ok=True)
    payload = {
        "etapa": etapa,
        "exit_code": code,
        "controls": [asdict(item) for item in controls],
    }
    (folder / "gate.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [f"# Gate {etapa}", "", f"Codigo de salida: {code}", ""]
    for item in controls:
        lines.append(f"- **{item.id}** {item.status}: {item.detail.splitlines()[0][:240]}")
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
