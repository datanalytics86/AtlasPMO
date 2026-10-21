"""Write a minimal XER whose tables are the ones documented for P6."""

from __future__ import annotations

import argparse
from pathlib import Path

from atlaspmo.io.synthetic import write_xer

ROOT = Path(__file__).resolve().parents[1]

MINIMAL_TABLES: list[dict[str, object]] = [
    {
        "name": "PROJECT",
        "fields": ["proj_id", "proj_short_name", "clndr_id"],
        "rows": [["1", "MIN", "C1"]],
    },
    {
        "name": "CALENDAR",
        "fields": ["clndr_id", "clndr_name", "day_hr_cnt"],
        "rows": [["C1", "Base", "8"]],
    },
    {
        "name": "TASK",
        "fields": ["task_id", "proj_id", "clndr_id", "task_code", "task_name", "task_type"],
        "rows": [["1", "1", "C1", "A1", "Actividad", "TT_Task"]],
    },
    {
        "name": "TASKPRED",
        "fields": ["task_pred_id", "task_id", "pred_task_id", "pred_type", "lag_hr_cnt"],
        "rows": [],
    },
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
