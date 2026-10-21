"""pre-push: G8, and only origin/v2 is a legal destination."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.qa_gate import check_g8  # noqa: E402


def main() -> int:
    lines = [line.strip() for line in sys.stdin.read().splitlines() if line.strip()]
    for line in lines:
        parts = line.split()
        if len(parts) < 4:
            continue
        remote_ref = parts[2]
        if remote_ref != "refs/heads/v2":
            print(f"push rechazado: destino {remote_ref}, solo refs/heads/v2", file=sys.stderr)
            return 1
    result = check_g8(ROOT)
    if result.status != "pass":
        print(result.detail, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
