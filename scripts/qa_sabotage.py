"""Small mutation runner used when no Windows mutator is installed.

One padded operator, or one return, changes per mutant. The source file is
restored before the function returns. A sample run is not a G13 pass.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_SWAPS = (
    (" != ", " == "),
    (" == ", " != "),
    (" >= ", " > "),
    (" <= ", " < "),
    (" > ", " >= "),
    (" < ", " <= "),
)


@dataclass(frozen=True)
class Mutant:
    label: str
    source: str


@dataclass(frozen=True)
class SabotageScore:
    killed: int
    survived: int
    invalid: int

    @property
    def kill_score(self) -> float:
        total = self.killed + self.survived
        if total == 0:
            return 0.0
        return 100.0 * self.killed / total


def mutants_of(source: str, limit: int) -> list[Mutant]:
    """Return at most `limit` single-edit copies of `source`."""
    lines = source.splitlines(keepends=True)
    found: list[Mutant] = []
    for index, line in enumerate(lines):
        if line.lstrip().startswith("#"):
            continue
        for old, new in _SWAPS:
            if old not in line:
                continue
            edited = list(lines)
            edited[index] = line.replace(old, new, 1)
            found.append(Mutant(f"L{index + 1}:{old.strip()}->{new.strip()}", "".join(edited)))
            break
        stripped = line.strip()
        if stripped.startswith("return ") and stripped != "return None":
            newline = "\n" if line.endswith("\n") else ""
            indent = line[: len(line) - len(line.lstrip())]
            edited = list(lines)
            edited[index] = f"{indent}return None{newline}"
            found.append(Mutant(f"L{index + 1}:return-None", "".join(edited)))
        if len(found) >= limit:
            break
    return found[:limit]


def score_file(
    module: Path,
    tests: list[Path],
    limit: int = 40,
    cwd: Path | None = None,
    timeout: float | None = None,
) -> SabotageScore:
    """Mutate `module` in place, run `tests`, and always restore the original.

    ``cwd`` is the pytest root. The default is the module directory, which is
    enough for a single-file sample. A package under ``src`` needs the repo.
    """
    original = module.read_text(encoding="utf-8")
    killed = 0
    survived = 0
    invalid = 0
    root = cwd or module.parent
    config = root / "pytest-sabotage.ini"
    config.write_text("[pytest]\naddopts =\n", encoding="utf-8")
    try:
        for mutant in mutants_of(original, limit):
            module.write_text(mutant.source, encoding="utf-8")
            try:
                proc = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pytest",
                        "-q",
                        "-c",
                        config.name,
                        "-p",
                        "no:cacheprovider",
                        "--basetemp",
                        str(root / ".pytest-sabotage"),
                        *[str(path) for path in tests],
                    ],
                    cwd=root,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=timeout,
                )
            except subprocess.TimeoutExpired:
                killed += 1
                continue
            blob = f"{proc.stdout}\n{proc.stderr}"
            if proc.returncode == 0:
                survived += 1
            elif "SyntaxError" in blob or proc.returncode == 2:
                invalid += 1
            else:
                killed += 1
    finally:
        module.write_text(original, encoding="utf-8")
        config.unlink(missing_ok=True)
        shutil.rmtree(root / ".pytest-sabotage", ignore_errors=True)
    return SabotageScore(killed, survived, invalid)


def alcance_for(available: int, limit: int) -> str:
    """A run is complete only when every mutant of the file was attempted."""
    if available > 0 and limit >= available:
        return "completo"
    return "muestra"


def render_report(
    score: SabotageScore,
    module: Path,
    *,
    alcance: str = "muestra",
    label: str | None = None,
) -> str:
    """Render one score. ``alcance`` is ``completo`` only when every mutant ran."""
    shown = label or module.name
    note = (
        "Cada mutante de los modulos medidos entro en la corrida."
        if alcance == "completo"
        else "Esta corrida es una muestra. No es el kill score del paquete."
    )
    return (
        "# Sabotaje\n\n"
        f"alcance: {alcance}\n"
        f"kill_score: {score.kill_score:.1f}\n"
        f"killed: {score.killed}\n"
        f"survived: {score.survived}\n"
        f"invalid: {score.invalid}\n"
        f"modulo: {shown}\n"
        f"\n{note}\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Muestra de mutación")
    parser.add_argument("--module", required=True)
    parser.add_argument("--test", action="append", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--completo", action="store_true")
    args = parser.parse_args(argv)
    module = Path(args.module)
    original = module.read_text(encoding="utf-8")
    available = len(mutants_of(original, limit=1_000_000))
    limit = available if args.completo else args.limit
    alcance = alcance_for(available, limit)
    score = score_file(
        module,
        [Path(path) for path in args.test],
        limit,
        cwd=Path(__file__).resolve().parents[1],
    )
    text = render_report(score, module, alcance=alcance, label=module.name)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
