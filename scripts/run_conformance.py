"""Compare a folder of synthetic XER files with the CPM engine.

p6_verified and ATLASPMO_GOLDEN_DIR are skipped when the folder is missing.
This script does not print names from the golden directory.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

from atlaspmo.engine.conformance import conformance
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer

ROOT = Path(__file__).resolve().parents[1]


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    folder = Path(args[0]) if args else ROOT / "tests" / "fixtures" / "synthetic" / "cpm"
    if not folder.is_dir():
        print(f"sinteticos: no está {folder.name}")
    else:
        for path in sorted(folder.glob("*.xer")):
            report = conformance(schedule_from_xer(read_xer(path)))
            digest = hashlib.sha256(path.name.encode("utf-8")).hexdigest()[:8]
            ratio = "sin campos comparables" if report.ratio is None else f"{report.ratio:.0%}"
            print(f"{digest} comparados={report.compared} coinciden={report.matched} {ratio}")
    verified = ROOT / "tests" / "fixtures" / "p6_verified"
    if not verified.is_dir():
        print("p6_verified: omitido")
    if not os.environ.get("ATLASPMO_GOLDEN_DIR"):
        print("golden: omitido")
    else:
        print("golden: definido; esta corrida no abre esa carpeta")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
