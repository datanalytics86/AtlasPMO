"""MSPDI reader. Element names follow the Project 2007 XML schema on Microsoft Learn.

They are not confirmed against a file exported by Nicolás. Duration values use
the XML Schema duration (clock time). LinkLag is tenths of a minute.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from lxml import etree

from atlaspmo.model.schedule import Activity, Project, Relationship, Schedule

_NS = "http://schemas.microsoft.com/project"
_DURATION = re.compile(
    r"^P(?:(?P<days>\d+)D)?(?:T(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?)?$"
)
_LINK = {"0": "PR_FF", "1": "PR_FS", "2": "PR_SF", "3": "PR_SS"}
_NOTE_CODE = "MSPDI no tiene task_code. Se usa WBS y, si falta, el UID."
_NOTE_DAY = "Una duración ISO con días (P1D) vale 24 horas de reloj, no un día laboral."
_NOTE_LAG = "LinkLag se divide por 600 para pasar de décimas de minuto a horas."
_NOTE_STATUS = "El estado sale de PercentComplete: 0 no iniciada, 100 completa, el resto activa."
_NOTE_MILE = "Milestone se guarda como TT_Mile. El MSPDI no distingue hito de inicio y de fin."
_NOTE_CAL = "Los calendarios MSPDI no se leen en esta fase."
_NOTE_SLACK = "TotalSlack no se carga: no se contrastó la unidad con un archivo de Nicolás."
_NOTE_BASE = "Sin BaselineStart: Start se usó también como fecha baseline."


def schedule_from_mspdi(path: Path) -> Schedule:
    """Read one MSPDI project. UID 0, the project summary task, is skipped."""
    root = etree.parse(str(path)).getroot()
    notes = [_NOTE_CODE, _NOTE_LAG, _NOTE_STATUS, _NOTE_MILE, _NOTE_CAL, _NOTE_SLACK]
    name = _text(root, "Name")
    data_date = _when(_text(root, "StatusDate"))
    if data_date is None:
        notes.append("No hay StatusDate. La fecha de corte queda vacía.")
    projects = (
        Project(
            proj_id="1",
            proj_short_name=name,
            proj_name=_text(root, "Title") or name,
            clndr_id=None,
            last_recalc_date=data_date,
            plan_end_date=_when(_text(root, "FinishDate")),
            scd_end_date=None,
        ),
    )
    activities: list[Activity] = []
    relationships: list[Relationship] = []
    tasks = root.find(_tag("Tasks"))
    link_seq = 0
    saw_day = False
    saw_baseline_gap = False
    for node in [] if tasks is None else tasks.findall(_tag("Task")):
        uid = _text(node, "UID")
        if uid is None or uid == "0":
            continue
        duration = _iso_hours(_text(node, "Duration"))
        remain = _iso_hours(_text(node, "RemainingDuration"))
        if _has_days(_text(node, "Duration")) or _has_days(_text(node, "RemainingDuration")):
            saw_day = True
        target_start = _when(_text(node, "BaselineStart")) or _when(_text(node, "Start"))
        target_end = _when(_text(node, "BaselineFinish")) or _when(_text(node, "Finish"))
        if _text(node, "BaselineStart") is None and _text(node, "Start") is not None:
            saw_baseline_gap = True
        activities.append(
            Activity(
                task_id=uid,
                proj_id="1",
                wbs_id=_text(node, "OutlineNumber"),
                clndr_id=None,
                task_code=_text(node, "WBS") or uid,
                task_name=_text(node, "Name"),
                task_type=_kind(node),
                status_code=_status(_text(node, "PercentComplete")),
                complete_pct_type=None,
                cstr_type=None,
                cstr_type2=None,
                target_drtn_hr_cnt=duration,
                remain_drtn_hr_cnt=remain,
                total_float_hr_cnt=None,
                free_float_hr_cnt=None,
                target_start_date=target_start,
                target_end_date=target_end,
                act_start_date=_when(_text(node, "ActualStart")),
                act_end_date=_when(_text(node, "ActualFinish")),
                early_start_date=_when(_text(node, "EarlyStart")) or _when(_text(node, "Start")),
                early_end_date=_when(_text(node, "EarlyFinish")) or _when(_text(node, "Finish")),
                late_start_date=_when(_text(node, "LateStart")),
                late_end_date=_when(_text(node, "LateFinish")),
                float_path=None,
                float_path_order=None,
                int_path=None,
                int_path_order=None,
                phys_complete_pct=None,
            )
        )
        for link in node.findall(_tag("PredecessorLink")):
            link_seq += 1
            relationships.append(_relationship(link, uid, link_seq, notes))
    if saw_day:
        notes.append(_NOTE_DAY)
    if saw_baseline_gap:
        notes.append(_NOTE_BASE)
    notes.append("proj_id queda en 1. El MSPDI no trae el id de P6.")
    notes.append("ConstraintType no se traduce a códigos CS_*.")
    return Schedule(
        projects=projects,
        calendars=(),
        wbs=(),
        activities=tuple(activities),
        relationships=tuple(relationships),
        assignments=(),
        activity_codes=(),
        parse_notes=tuple(dict.fromkeys(notes)),
    )


def _relationship(
    node: etree._Element,
    successor: str,
    seq: int,
    notes: list[str],
) -> Relationship:
    raw = _text(node, "Type")
    kind = _LINK.get(raw or "")
    if raw is not None and kind is None:
        notes.append(f"Tipo de vínculo MSPDI no reconocido: {raw}.")
    lag = _text(node, "LinkLag")
    hours = None if lag is None else int(lag) / 600
    return Relationship(
        task_pred_id=str(seq),
        task_id=successor,
        pred_task_id=_text(node, "PredecessorUID"),
        proj_id="1",
        pred_proj_id="1",
        pred_type=kind,
        lag_hr_cnt=hours,
    )


def _kind(node: etree._Element) -> str:
    if _text(node, "Summary") == "1":
        return "TT_WBS"
    if _text(node, "Milestone") == "1":
        return "TT_Mile"
    return "TT_Task"


def _status(percent: str | None) -> str | None:
    if percent is None:
        return None
    value = float(percent)
    if value >= 100:
        return "TK_Complete"
    if value > 0:
        return "TK_Active"
    return "TK_NotStart"


def _iso_hours(value: str | None) -> float | None:
    if value is None:
        return None
    match = _DURATION.fullmatch(value)
    if match is None:
        return None
    days = int(match.group("days") or 0)
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes") or 0)
    seconds = int(match.group("seconds") or 0)
    return days * 24 + hours + minutes / 60 + seconds / 3600


def _has_days(value: str | None) -> bool:
    if value is None:
        return False
    match = _DURATION.fullmatch(value)
    return match is not None and match.group("days") not in (None, "0")


def _tag(name: str) -> str:
    return f"{{{_NS}}}{name}"


def _text(node: etree._Element, name: str) -> str | None:
    child = node.find(_tag(name))
    if child is None or not isinstance(child.text, str) or child.text.strip() == "":
        return None
    return child.text.strip()


def _when(value: str | None) -> datetime | None:
    if value is None:
        return None
    token = value.replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(token, fmt)
        except ValueError:
            continue
    return None
