"""Write the phase-0 structural XER fixture.

Column names in the emitted file are synthetic. They are not P6 fields.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from atlaspmo.io.synthetic import write_xer

ROOT = Path(__file__).resolve().parents[1]

MINIMAL_TABLES: list[dict[str, object]] = [
    {
        "name": "SYNTH",
        "fields": ["col_a", "col_b"],
        "rows": [["1", "ni\u00f1o"]],
    }
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a structural synthetic XER.")
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "tests" / "fixtures" / "synthetic" / "minimal.xer",
    )
    args = parser.parse_args(argv)
    write_xer(args.out, "ERMHDR", MINIMAL_TABLES)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
