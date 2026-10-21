"""Build a realistic synthetic XER for scale tests.

Tables and fields are the ones documented in docs/XER_SPEC.md.
The file is written only where the caller points; tests use a temp directory.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from atlaspmo.io.synthetic import write_xer

HEADER = "ERMHDR\t20.12"
TASK_FIELDS = [
    "task_id",
    "proj_id",
    "wbs_id",
    "clndr_id",
    "task_code",
    "task_name",
    "task_type",
    "status_code",
    "target_drtn_hr_cnt",
    "remain_drtn_hr_cnt",
    "cstr_type",
    "cstr_date",
]
PRED_FIELDS = [
    "task_pred_id",
    "task_id",
    "pred_task_id",
    "proj_id",
    "pred_proj_id",
    "pred_type",
    "lag_hr_cnt",
]


def build_tables(activities: int, *, series: bool) -> list[dict[str, object]]:
    """Return PROJECT, CALENDAR, PROJWBS, TASK and TASKPRED for one project."""
    if activities < 2:
        raise ValueError("activities must be at least 2")
    project = {
        "name": "PROJECT",
        "fields": ["proj_id", "proj_short_name", "proj_name", "clndr_id", "last_recalc_date"],
        "rows": [["1", "ESC", "Escala", "1", "2026-01-05 08:00"]],
    }
    calendar = {
        "name": "CALENDAR",
        "fields": ["clndr_id", "clndr_name", "proj_id", "day_hr_cnt", "clndr_data"],
        "rows": [["1", "Lunes a viernes", "1", "8", _calendar_text()]],
    }
    wbs = {
        "name": "PROJWBS",
        "fields": ["wbs_id", "proj_id", "wbs_short_name", "wbs_name"],
        "rows": [["1", "1", "ESC", "Escala"]],
    }
    tasks: list[list[str]] = []
    preds: list[list[str]] = []
    for index in range(1, activities + 1):
        progressed = index == 1
        tasks.append(
            [
                str(index),
                "1",
                "1",
                "1",
                f"A{index}",
                f"Actividad {index}",
                "TT_Task",
                "TK_Active" if progressed else "TK_NotStart",
                "16" if index % 17 == 0 else "8",
                "8" if progressed else ("16" if index % 17 == 0 else "8"),
                "CS_MSO" if index == activities else "",
                "2026-06-01 08:00" if index == activities else "",
            ]
        )
        if index == 1:
            continue
        pred_type = "PR_FS" if series or index % 11 else "PR_SS"
        lag = "0" if series or index % 13 else "8"
        preds.append([str(index - 1), str(index), str(index - 1), "1", "1", pred_type, lag])
        if not series and index > 3 and index % 29 == 0:
            preds.append([f"x{index}", str(index), str(index - 3), "1", "1", "PR_FF", "0"])
    return [
        project,
        calendar,
        wbs,
        {"name": "TASK", "fields": TASK_FIELDS, "rows": tasks},
        {"name": "TASKPRED", "fields": PRED_FIELDS, "rows": preds},
    ]


def _calendar_text() -> str:
    days = "".join(f"(0||{number}()((0||0(s|08:00|f|16:00)())))" for number in range(1, 8))
    return (
        f"(0||CalendarData()((0||DaysOfWeek()({days}))"
        "(0||Exceptions()((0||46000()())))(0||VIEW(ShowTotal|N)())))"
    )


def write_scale(path: Path, activities: int, *, series: bool = False) -> None:
    write_xer(path, HEADER, build_tables(activities, series=series))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Genera un XER de escala con tablas P6.")
    parser.add_argument("--activities", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--series", action="store_true")
    args = parser.parse_args(argv)
    write_scale(args.out, args.activities, series=args.series)
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
