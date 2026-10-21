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


_LINK_TYPES = ("PR_FS", "PR_SS", "PR_FF", "PR_SF")


def build_tables(activities: int, *, series: bool) -> list[dict[str, object]]:
    """Return PROJECT, CALENDAR, PROJWBS, TASK and TASKPRED for one project.

    A series is one FS chain on one calendar. A realistic network adds a
    second calendar, several WBS nodes, mixed link types, lags, a holiday
    exception, partial progress and about two predecessors per activity.
    """
    if activities < 2:
        raise ValueError("activities must be at least 2")
    wbs_count = 1 if series else max(2, min(4, activities // 5))
    project = {
        "name": "PROJECT",
        "fields": ["proj_id", "proj_short_name", "proj_name", "clndr_id", "last_recalc_date"],
        "rows": [["1", "ESC", "Escala", "1", "2026-01-05 08:00"]],
    }
    calendar = {
        "name": "CALENDAR",
        "fields": ["clndr_id", "clndr_name", "proj_id", "day_hr_cnt", "clndr_data"],
        "rows": _calendar_rows(series),
    }
    wbs = {
        "name": "PROJWBS",
        "fields": ["wbs_id", "proj_id", "wbs_short_name", "wbs_name"],
        "rows": [
            [str(item), "1", f"W{item}", f"Paquete {item}"] for item in range(1, wbs_count + 1)
        ],
    }
    tasks: list[list[str]] = []
    preds: list[list[str]] = []
    for index in range(1, activities + 1):
        target = "16" if index % 17 == 0 else "8"
        progressed = (not series and index % 7 == 1) or (series and index == 1)
        remain = "4" if progressed and not series else ("8" if progressed else target)
        tasks.append(
            [
                str(index),
                "1",
                str(1 + (index - 1) % wbs_count),
                "1" if series or index % 2 else "2",
                f"A{index}",
                f"Actividad {index}",
                "TT_Task",
                "TK_Active" if progressed else "TK_NotStart",
                target,
                remain,
                "CS_MSO" if index == activities else "",
                "2026-06-01 08:00" if index == activities else "",
            ]
        )
        if index == 1:
            continue
        pred_type = "PR_FS" if series else _LINK_TYPES[(index - 2) % 4]
        lag = "0" if series or index % 4 else "8"
        preds.append([str(index - 1), str(index), str(index - 1), "1", "1", pred_type, lag])
        if series or index <= 2:
            continue
        preds.append([f"e{index}", str(index), str(index - 2), "1", "1", "PR_SS", "0"])
        if index > 4 and index % 3 == 0:
            preds.append([f"f{index}", str(index), "1", "1", "1", "PR_FF", "8"])
    return [
        project,
        calendar,
        wbs,
        {"name": "TASK", "fields": TASK_FIELDS, "rows": tasks},
        {"name": "TASKPRED", "fields": PRED_FIELDS, "rows": preds},
    ]


def _calendar_rows(series: bool) -> list[list[str]]:
    rows = [["1", "Lunes a viernes", "1", "8", _weekday_with_holiday()]]
    if not series:
        rows.append(["2", "Media jornada siete dias", "1", "4", _half_day_week()])
    return rows


def _weekday_with_holiday() -> str:
    days = "".join(
        f"(0||{number}()((0||0(s|08:00|f|16:00)())))" if number < 6 else f"(0||{number}()())"
        for number in range(1, 8)
    )
    return (
        f"(0||CalendarData()((0||DaysOfWeek()({days}))"
        "(0||Exceptions()((0||46000()())))(0||VIEW(ShowTotal|N)())))"
    )


def _half_day_week() -> str:
    days = "".join(f"(0||{number}()((0||0(s|08:00|f|12:00)())))" for number in range(1, 8))
    return f"(0||CalendarData()((0||DaysOfWeek()({days}))(0||VIEW(ShowTotal|N)())))"


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
