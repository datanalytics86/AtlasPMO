"""Write the hand-sized synthetic XER cases. Expectations live in the YAML files."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.io.synthetic import write_xer

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "fixtures" / "synthetic" / "cases"

TASK_FIELDS = [
    "task_id",
    "proj_id",
    "clndr_id",
    "task_code",
    "task_name",
    "task_type",
    "status_code",
    "cstr_type",
    "cstr_type2",
    "remain_drtn_hr_cnt",
    "total_float_hr_cnt",
    "target_start_date",
    "target_end_date",
    "early_start_date",
    "early_end_date",
    "act_start_date",
    "act_end_date",
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


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    _write("chain", _chain())
    _write("relmix", _relmix())
    _write("constraints", _constraints())
    _write("floatdur", _floatdur())
    _write("dates", _dates())
    _write("baseline", _baseline())
    _write("cpli", _cpli())
    _write("cycle", _cycle())
    print(OUT)


def _write(name: str, tables: list[dict[str, object]]) -> None:
    write_xer(OUT / f"{name}.xer", "ERMHDR\t20.12", tables)


def _base(
    projects: list[list[str]],
    tasks: list[list[str]],
    rels: list[list[str]],
) -> list[dict[str, object]]:
    return [
        {
            "name": "PROJECT",
            "fields": ["proj_id", "proj_short_name", "clndr_id", "last_recalc_date"],
            "rows": projects,
        },
        {
            "name": "CALENDAR",
            "fields": ["clndr_id", "clndr_name", "day_hr_cnt"],
            "rows": [["C1", "Base", "8"]],
        },
        {"name": "TASK", "fields": TASK_FIELDS, "rows": tasks},
        {"name": "TASKPRED", "fields": PRED_FIELDS, "rows": rels},
    ]


def _task(
    task_id: str,
    code: str,
    status: str = "TK_NotStart",
    kind: str = "TT_Task",
    cstr: str = "",
    cstr2: str = "",
    remain: str = "8",
    total: str = "0",
    proj: str = "1",
    target_start: str = "2026-03-01 08:00",
    target_end: str = "",
    early_start: str = "",
    early_end: str = "",
    act_start: str = "",
    act_end: str = "",
) -> list[str]:
    return [
        task_id,
        proj,
        "C1",
        code,
        code,
        kind,
        status,
        cstr,
        cstr2,
        remain,
        total,
        target_start,
        target_end,
        early_start,
        early_end,
        act_start,
        act_end,
    ]


def _rel(
    pred_id: str,
    pred: str,
    succ: str,
    kind: str = "PR_FS",
    lag: str = "0",
    proj: str = "1",
) -> list[str]:
    return [pred_id, succ, pred, proj, proj, kind, lag]


def _chain() -> list[dict[str, object]]:
    tasks = [_task(str(index), code) for index, code in enumerate("ABCD", start=1)]
    rels = [_rel(str(index), str(index), str(index + 1)) for index in range(1, 4)]
    return _base([["1", "CUR", "C1", ""]], tasks, rels)


def _relmix() -> list[dict[str, object]]:
    tasks = [_task(str(index), f"A{index}") for index in range(1, 5)]
    rels = [
        _rel("10", "1", "2", "PR_FS", "0"),
        _rel("11", "1", "3", "PR_FS", "8"),
        _rel("12", "1", "4", "PR_FS", "-8"),
        _rel("13", "2", "3", "PR_SS", "0"),
    ]
    return _base([["1", "CUR", "C1", ""]], tasks, rels)


def _constraints() -> list[dict[str, object]]:
    tasks = [
        _task("1", "A", cstr="CS_MSO"),
        _task("2", "B", cstr="CS_ALAP"),
        _task("3", "C"),
        _task("4", "D", cstr2="CS_MANDFIN"),
    ]
    rels = [_rel(str(index), str(index), str(index + 1)) for index in range(1, 4)]
    return _base([["1", "CUR", "C1", ""]], tasks, rels)


def _floatdur() -> list[dict[str, object]]:
    tasks = [
        _task("1", "A", remain="8", total="0"),
        _task("2", "B", remain="8", total="400"),
        _task("3", "C", remain="8", total="-8"),
        _task("4", "D", remain="400", total="16"),
    ]
    rels = [_rel(str(index), str(index), str(index + 1)) for index in range(1, 4)]
    return _base([["1", "CUR", "C1", ""]], tasks, rels)


def _dates() -> list[dict[str, object]]:
    tasks = [
        _task("1", "A", early_start="2026-01-10 08:00", early_end="2026-01-11 08:00"),
        _task("2", "B", early_start="2026-01-20 08:00", early_end="2026-01-21 08:00"),
        _task(
            "3",
            "C",
            status="TK_Active",
            act_start="2026-01-20 08:00",
            early_start="2026-01-20 08:00",
            early_end="2026-01-21 08:00",
        ),
        _task(
            "4",
            "D",
            status="TK_Complete",
            act_start="2026-01-01 08:00",
            act_end="2026-01-10 08:00",
        ),
    ]
    rels = [_rel(str(index), str(index), str(index + 1)) for index in range(1, 4)]
    return _base([["1", "CUR", "C1", "2026-01-15 00:00"]], tasks, rels)


def _baseline() -> list[dict[str, object]]:
    tasks = [
        _task("10", "A1", status="TK_Complete", act_end="2026-01-12 08:00", proj="1"),
        _task("11", "B1", proj="1"),
        _task("12", "C1", proj="1"),
        _task("20", "A1", proj="2", target_end="2026-01-10 08:00"),
        _task("21", "B1", proj="2", target_end="2026-01-20 08:00"),
        _task("22", "C1", proj="2", target_end="2026-03-01 08:00"),
    ]
    rels = [
        _rel("1", "10", "11"),
        _rel("2", "11", "12"),
    ]
    projects = [
        ["1", "CUR", "C1", "2026-02-01 00:00"],
        ["2", "BASE", "C1", ""],
    ]
    return _base(projects, tasks, rels)


def _cpli() -> list[dict[str, object]]:
    tables = _base(
        [["1", "CUR", "C1", ""]],
        [
            _task("1", "A", remain="16", total="8"),
            _task("2", "B", remain="24", total="8"),
            _task("3", "M", kind="TT_FinMile", remain="0", total="16"),
        ],
        [_rel("1", "1", "2"), _rel("2", "2", "3")],
    )
    task = tables[2]
    fields = list(task["fields"])
    fields.extend(["float_path", "float_path_order"])
    extras = [["1", "1"], ["1", "2"], ["1", "3"]]
    rows = [list(row) + extra for row, extra in zip(task["rows"], extras, strict=True)]
    task["fields"] = fields
    task["rows"] = rows
    return tables


def _cycle() -> list[dict[str, object]]:
    tasks = [_task("1", "A"), _task("2", "B")]
    rels = [_rel("1", "1", "2"), _rel("2", "2", "1")]
    return _base([["1", "CUR", "C1", ""]], tasks, rels)


if __name__ == "__main__":
    main()
