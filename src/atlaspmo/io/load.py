"""Build a Schedule from a parsed XER file.

Only columns listed in docs/XER_SPEC.md are read. Anything else stays in
the raw line and is ignored by the model.
"""

from __future__ import annotations

from datetime import datetime

from atlaspmo.io.xer import XerFile, XerTable
from atlaspmo.model.schedule import (
    Activity,
    ActivityCode,
    Assignment,
    Calendar,
    Project,
    Relationship,
    Schedule,
    Wbs,
)

_DATE_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


def schedule_from_xer(document: XerFile) -> Schedule:
    """Map the cited columns of one XER document into a Schedule."""
    absent: set[str] = set()
    notes: list[str] = []
    projects = _projects(document.table("PROJECT"), absent, notes)
    calendars = _calendars(document.table("CALENDAR"), absent, notes)
    wbs = _wbs(document.table("PROJWBS"), absent)
    activities = _activities(document.table("TASK"), absent, notes)
    relationships = _relationships(document.table("TASKPRED"), absent, notes)
    assignments, cost_present = _assignments(document.table("TASKRSRC"), absent, notes)
    codes = _codes(document.table("TASKACTV"), absent)
    known = ("PROJECT", "CALENDAR", "PROJWBS", "TASK", "TASKPRED", "TASKRSRC", "TASKACTV")
    absent_tables = frozenset(name for name in known if document.table(name) is None)
    return Schedule(
        projects=tuple(projects),
        calendars=tuple(calendars),
        wbs=tuple(wbs),
        activities=tuple(activities),
        relationships=tuple(relationships),
        assignments=tuple(assignments),
        activity_codes=tuple(codes),
        absent_columns=frozenset(absent),
        absent_tables=absent_tables,
        parse_notes=tuple(notes),
        cost_column_present=cost_present,
    )


def _text(
    table: XerTable | None,
    values: dict[str, str],
    column: str,
    absent: set[str],
) -> str | None:
    if table is None or not table.has_field(column):
        if table is not None:
            absent.add(f"{table.name}.{column}")
        return None
    raw = values.get(column, "")
    if raw == "":
        return None
    return raw


def _number(
    table: XerTable | None,
    values: dict[str, str],
    column: str,
    absent: set[str],
    notes: list[str],
) -> float | None:
    if table is None:
        return None
    raw = _text(table, values, column, absent)
    if raw is None:
        return None
    token = raw.strip()
    if "," in token and "." not in token:
        token = token.replace(",", ".")
        note = f"{table.name}.{column}: coma decimal interpretada como punto"
        if note not in notes:
            notes.append(note)
    try:
        return float(token)
    except ValueError:
        note = f"{table.name}.{column}: valor numérico no leído ({raw})"
        if note not in notes:
            notes.append(note)
        return None


def _date(
    table: XerTable | None,
    values: dict[str, str],
    column: str,
    absent: set[str],
    notes: list[str],
) -> datetime | None:
    if table is None:
        return None
    raw = _text(table, values, column, absent)
    if raw is None:
        return None
    token = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(token, fmt)
        except ValueError:
            continue
    note = f"{table.name}.{column}: fecha no reconocida ({raw})"
    if note not in notes:
        notes.append(note)
    return None


def _projects(table: XerTable | None, absent: set[str], notes: list[str]) -> list[Project]:
    if table is None:
        return []
    rows: list[Project] = []
    for row in table.rows:
        values = row.values
        rows.append(
            Project(
                proj_id=_text(table, values, "proj_id", absent),
                proj_short_name=_text(table, values, "proj_short_name", absent),
                proj_name=_text(table, values, "proj_name", absent),
                clndr_id=_text(table, values, "clndr_id", absent),
                last_recalc_date=_date(table, values, "last_recalc_date", absent, notes),
                plan_end_date=_date(table, values, "plan_end_date", absent, notes),
                scd_end_date=_date(table, values, "scd_end_date", absent, notes),
            )
        )
    return rows


def _calendars(table: XerTable | None, absent: set[str], notes: list[str]) -> list[Calendar]:
    if table is None:
        return []
    rows: list[Calendar] = []
    for row in table.rows:
        values = row.values
        rows.append(
            Calendar(
                clndr_id=_text(table, values, "clndr_id", absent),
                clndr_name=_text(table, values, "clndr_name", absent),
                proj_id=_text(table, values, "proj_id", absent),
                day_hr_cnt=_number(table, values, "day_hr_cnt", absent, notes),
                base_clndr_id=_text(table, values, "base_clndr_id", absent),
                clndr_data=_text(table, values, "clndr_data", absent),
            )
        )
    return rows


def _wbs(table: XerTable | None, absent: set[str]) -> list[Wbs]:
    if table is None:
        return []
    rows: list[Wbs] = []
    for row in table.rows:
        values = row.values
        rows.append(
            Wbs(
                wbs_id=_text(table, values, "wbs_id", absent),
                proj_id=_text(table, values, "proj_id", absent),
                parent_wbs_id=_text(table, values, "parent_wbs_id", absent),
                wbs_short_name=_text(table, values, "wbs_short_name", absent),
                wbs_name=_text(table, values, "wbs_name", absent),
            )
        )
    return rows


def _activities(table: XerTable | None, absent: set[str], notes: list[str]) -> list[Activity]:
    if table is None:
        return []
    rows: list[Activity] = []
    for row in table.rows:
        values = row.values
        rows.append(
            Activity(
                task_id=_text(table, values, "task_id", absent),
                proj_id=_text(table, values, "proj_id", absent),
                wbs_id=_text(table, values, "wbs_id", absent),
                clndr_id=_text(table, values, "clndr_id", absent),
                task_code=_text(table, values, "task_code", absent),
                task_name=_text(table, values, "task_name", absent),
                task_type=_text(table, values, "task_type", absent),
                status_code=_text(table, values, "status_code", absent),
                complete_pct_type=_text(table, values, "complete_pct_type", absent),
                cstr_type=_text(table, values, "cstr_type", absent),
                cstr_type2=_text(table, values, "cstr_type2", absent),
                target_drtn_hr_cnt=_number(table, values, "target_drtn_hr_cnt", absent, notes),
                remain_drtn_hr_cnt=_number(table, values, "remain_drtn_hr_cnt", absent, notes),
                total_float_hr_cnt=_number(table, values, "total_float_hr_cnt", absent, notes),
                free_float_hr_cnt=_number(table, values, "free_float_hr_cnt", absent, notes),
                target_start_date=_date(table, values, "target_start_date", absent, notes),
                target_end_date=_date(table, values, "target_end_date", absent, notes),
                act_start_date=_date(table, values, "act_start_date", absent, notes),
                act_end_date=_date(table, values, "act_end_date", absent, notes),
                early_start_date=_date(table, values, "early_start_date", absent, notes),
                early_end_date=_date(table, values, "early_end_date", absent, notes),
                late_start_date=_date(table, values, "late_start_date", absent, notes),
                late_end_date=_date(table, values, "late_end_date", absent, notes),
                float_path=_text(table, values, "float_path", absent),
                float_path_order=_text(table, values, "float_path_order", absent),
                int_path=_text(table, values, "int_path", absent),
                int_path_order=_text(table, values, "int_path_order", absent),
                phys_complete_pct=_number(table, values, "phys_complete_pct", absent, notes),
            )
        )
    return rows


def _relationships(
    table: XerTable | None,
    absent: set[str],
    notes: list[str],
) -> list[Relationship]:
    if table is None:
        return []
    rows: list[Relationship] = []
    for row in table.rows:
        values = row.values
        rows.append(
            Relationship(
                task_pred_id=_text(table, values, "task_pred_id", absent),
                task_id=_text(table, values, "task_id", absent),
                pred_task_id=_text(table, values, "pred_task_id", absent),
                proj_id=_text(table, values, "proj_id", absent),
                pred_proj_id=_text(table, values, "pred_proj_id", absent),
                pred_type=_text(table, values, "pred_type", absent),
                lag_hr_cnt=_number(table, values, "lag_hr_cnt", absent, notes),
                line_index=row.line_index,
            )
        )
    return rows


def _assignments(
    table: XerTable | None,
    absent: set[str],
    notes: list[str],
) -> tuple[list[Assignment], bool]:
    if table is None:
        return [], False
    cost_present = table.has_field("target_cost")
    rows: list[Assignment] = []
    for row in table.rows:
        values = row.values
        rows.append(
            Assignment(
                taskrsrc_id=_text(table, values, "taskrsrc_id", absent),
                task_id=_text(table, values, "task_id", absent),
                rsrc_id=_text(table, values, "rsrc_id", absent),
                target_qty=_number(table, values, "target_qty", absent, notes),
                target_cost=_number(table, values, "target_cost", absent, notes),
                act_reg_cost=_number(table, values, "act_reg_cost", absent, notes),
                remain_cost=_number(table, values, "remain_cost", absent, notes),
            )
        )
    return rows, cost_present


def _codes(table: XerTable | None, absent: set[str]) -> list[ActivityCode]:
    if table is None:
        return []
    rows: list[ActivityCode] = []
    for row in table.rows:
        values = row.values
        rows.append(
            ActivityCode(
                task_id=_text(table, values, "task_id", absent),
                actv_code_id=_text(table, values, "actv_code_id", absent),
                actv_code_type_id=_text(table, values, "actv_code_type_id", absent),
            )
        )
    return rows
