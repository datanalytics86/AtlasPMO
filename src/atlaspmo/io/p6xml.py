"""Minimal P6 XML reader for the same schedule model.

Element names follow the fixture in tests/fixtures/synthetic/minimal.xml
and the public PMXML shape (APIBusinessObjects / Project / Activity /
Relationship). They are not confirmed against an export from Nicolás.
XER codes are not invented for XML values: status and type stay as text
and the mapping below is an explicit assumption.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from lxml import etree

from atlaspmo.model.schedule import Activity, Project, Relationship, Schedule

_STATUS = {
    "Not Started": "TK_NotStart",
    "In Progress": "TK_Active",
    "Completed": "TK_Complete",
}
_TYPE = {
    "Task Dependent": "TT_Task",
    "Resource Dependent": "TT_Rsrc",
    "Level of Effort": "TT_LOE",
    "Start Milestone": "TT_Mile",
    "Finish Milestone": "TT_FinMile",
    "WBS Summary": "TT_WBS",
}


def schedule_from_p6xml(path: Path) -> Schedule:
    """Read a small PMXML file. Unmapped elements are ignored."""
    tree = etree.parse(str(path))
    root = tree.getroot()
    projects: list[Project] = []
    activities: list[Activity] = []
    relationships: list[Relationship] = []
    notes = [
        "XML: estado y tipo se traducen con la tabla de docs/XER_SPEC.md; "
        "no es un código leído del XER."
    ]
    for project in root.findall("Project"):
        proj_id = _child(project, "ObjectId")
        projects.append(
            Project(
                proj_id=proj_id,
                proj_short_name=_child(project, "Id"),
                proj_name=_child(project, "Name"),
                clndr_id=None,
                last_recalc_date=_when(_child(project, "DataDate")),
                plan_end_date=None,
                scd_end_date=None,
            )
        )
        for activity in project.findall("Activity"):
            activities.append(_activity(activity, proj_id))
        for link in project.findall("Relationship"):
            relationships.append(_link(link, proj_id))
    return Schedule(
        projects=tuple(projects),
        calendars=(),
        wbs=(),
        activities=tuple(activities),
        relationships=tuple(relationships),
        assignments=(),
        activity_codes=(),
        absent_columns=frozenset(),
        absent_tables=frozenset(),
        parse_notes=tuple(notes),
        cost_column_present=False,
    )


def _activity(node: etree._Element, proj_id: str | None) -> Activity:
    status = _child(node, "Status")
    kind = _child(node, "Type")
    return Activity(
        task_id=_child(node, "ObjectId"),
        proj_id=proj_id,
        wbs_id=None,
        clndr_id=None,
        task_code=_child(node, "Id"),
        task_name=_child(node, "Name"),
        task_type=_TYPE.get(kind, kind) if kind else None,
        status_code=_STATUS.get(status, status) if status else None,
        complete_pct_type=None,
        cstr_type=None,
        cstr_type2=None,
        target_drtn_hr_cnt=_hours(_child(node, "PlannedDuration")),
        remain_drtn_hr_cnt=_hours(_child(node, "RemainingDuration")),
        total_float_hr_cnt=_hours(_child(node, "TotalFloat")),
        free_float_hr_cnt=None,
        target_start_date=_when(_child(node, "PlannedStartDate")),
        target_end_date=_when(_child(node, "PlannedFinishDate")),
        act_start_date=_when(_child(node, "ActualStartDate")),
        act_end_date=_when(_child(node, "ActualFinishDate")),
        early_start_date=_when(_child(node, "RemainingEarlyStartDate")),
        early_end_date=_when(_child(node, "RemainingEarlyFinishDate")),
        late_start_date=None,
        late_end_date=None,
        float_path=None,
        float_path_order=None,
        int_path=None,
        int_path_order=None,
        phys_complete_pct=None,
    )


def _link(node: etree._Element, proj_id: str | None) -> Relationship:
    return Relationship(
        task_pred_id=_child(node, "ObjectId"),
        task_id=_child(node, "SuccessorActivityObjectId"),
        pred_task_id=_child(node, "PredecessorActivityObjectId"),
        proj_id=proj_id,
        pred_proj_id=_child(node, "PredecessorProjectObjectId") or proj_id,
        pred_type=_child(node, "Type"),
        lag_hr_cnt=_hours(_child(node, "Lag")),
    )


def _child(node: etree._Element, name: str) -> str | None:
    child = node.find(name)
    if child is None:
        return None
    text = child.text
    if not isinstance(text, str) or text.strip() == "":
        return None
    return text.strip()


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


def _hours(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
