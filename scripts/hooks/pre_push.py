"""pre-push: G8, and only origin/v2 is a legal destination."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.qa_gate import check_g8  # noqa: E402

_ALLOWED_REFS = {"refs/heads/v2", "v2"}


def _remote_name(argv: list[str]) -> str:
    from_env = os.environ.get("PRE_COMMIT_REMOTE_NAME", "")
    if from_env:
        return from_env
    if len(argv) > 1 and not argv[1].startswith("-"):
        return argv[1]
    return ""


def _remote_refs(stdin: str | None) -> list[str]:
    refs: list[str] = []
    branch = os.environ.get("PRE_COMMIT_REMOTE_BRANCH", "")
    if branch:
        refs.append(branch)
    if stdin is not None:
        text = stdin
    elif branch:
        text = ""
    else:
        text = sys.stdin.read()
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            refs.append(parts[2])
    return refs


def main(argv: list[str] | None = None, stdin: str | None = None) -> int:
    args = list(sys.argv if argv is None else argv)
    remote = _remote_name(args)
    if remote != "origin":
        shown = remote or "(vacio)"
        print(f"push rechazado: remoto {shown}, solo origin", file=sys.stderr)
        return 1
    refs = _remote_refs(stdin)
    if not refs or any(ref not in _ALLOWED_REFS for ref in refs):
        shown = ", ".join(refs) or "(sin ref)"
        print(f"push rechazado: destino {shown}, solo refs/heads/v2", file=sys.stderr)
        return 1
    result = check_g8(ROOT)
    if result.status != "pass":
        print(result.detail, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
