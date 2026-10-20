"""CPM conformance runner.

Phase 2 implements the comparison. This stub never reads schedule files,
including a directory named by ATLASPMO_GOLDEN_DIR.
"""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "Conformidad CPM no está implementada. Llega en la Fase 2.",
        file=sys.stderr,
    )
    print("Este script no lee cronogramas.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
