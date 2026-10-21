"""Small mutation runner used when no Windows mutator is installed.

One padded operator, or one return, changes per mutant. The source file is
restored before the function returns. A sample run is not a G13 pass.
"""

from __future__ import annotations

import argparse
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


def score_file(module: Path, tests: list[Path], limit: int = 40) -> SabotageScore:
    """Mutate `module` in place, run `tests`, and always restore the original."""
    original = module.read_text(encoding="utf-8")
    killed = 0
    survived = 0
    invalid = 0
    config = module.parent / "pytest-sabotage.ini"
    config.write_text("[pytest]\naddopts =\n", encoding="utf-8")
    try:
        for mutant in mutants_of(original, limit):
            module.write_text(mutant.source, encoding="utf-8")
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
                    *[str(path) for path in tests],
                ],
                cwd=module.parent,
                capture_output=True,
                text=True,
                check=False,
            )
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
    return SabotageScore(killed, survived, invalid)


def render_report(score: SabotageScore, module: Path) -> str:
    return (
        "# Sabotaje\n\n"
        "alcance: muestra\n"
        f"kill_score: {score.kill_score:.1f}\n"
        f"killed: {score.killed}\n"
        f"survived: {score.survived}\n"
        f"invalid: {score.invalid}\n"
        f"modulo: {module.as_posix()}\n"
        "\nEsta corrida es una muestra. No es el kill score del paquete.\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Muestra de mutación")
    parser.add_argument("--module", required=True)
    parser.add_argument("--test", action="append", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args(argv)
    module = Path(args.module)
    score = score_file(module, [Path(path) for path in args.test], args.limit)
    text = render_report(score, module)
    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
