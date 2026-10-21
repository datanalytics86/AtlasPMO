"""pre-commit: the same privacy control as the gate."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.qa_gate import check_g8  # noqa: E402


def main() -> int:
    result = check_g8(ROOT)
    if result.status != "pass":
        print(result.detail, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
