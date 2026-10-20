"""In-memory schedule. Identifiers stay as text.

Field names are the ones recorded in docs/XER_SPEC.md. A missing column is
None plus an entry in `absent_columns`. An empty cell is None and is not
listed there.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Project:
    proj_id: str | None
    proj_short_name: str | None
    proj_name: str | None
    clndr_id: str | None
    last_recalc_date: datetime | None
    plan_end_date: datetime | None
    scd_end_date: datetime | None


@dataclass(frozen=True)
class Calendar:
    clndr_id: str | None
    clndr_name: str | None
    proj_id: str | None
    day_hr_cnt: float | None
    base_clndr_id: str | None
    clndr_data: str | None


@dataclass(frozen=True)
class Wbs:
    wbs_id: str | None
    proj_id: str | None
    parent_wbs_id: str | None
    wbs_short_name: str | None
    wbs_name: str | None


@dataclass(frozen=True)
class Activity:
    task_id: str | None
    proj_id: str | None
    wbs_id: str | None
    clndr_id: str | None
    task_code: str | None
    task_name: str | None
    task_type: str | None
    status_code: str | None
    complete_pct_type: str | None
    cstr_type: str | None
    cstr_type2: str | None
    target_drtn_hr_cnt: float | None
    remain_drtn_hr_cnt: float | None
    total_float_hr_cnt: float | None
    free_float_hr_cnt: float | None
    target_start_date: datetime | None
    target_end_date: datetime | None
    act_start_date: datetime | None
    act_end_date: datetime | None
    early_start_date: datetime | None
    early_end_date: datetime | None
    late_start_date: datetime | None
    late_end_date: datetime | None
    float_path: str | None
    float_path_order: str | None
    int_path: str | None
    int_path_order: str | None
    phys_complete_pct: float | None


@dataclass(frozen=True)
class Relationship:
    task_pred_id: str | None
    task_id: str | None
    pred_task_id: str | None
    proj_id: str | None
    pred_proj_id: str | None
    pred_type: str | None
    lag_hr_cnt: float | None
    line_index: int | None = None


@dataclass(frozen=True)
class Assignment:
    taskrsrc_id: str | None
    task_id: str | None
    rsrc_id: str | None
    target_qty: float | None
    target_cost: float | None
    act_reg_cost: float | None
    remain_cost: float | None


@dataclass(frozen=True)
class ActivityCode:
    task_id: str | None
    actv_code_id: str | None
    actv_code_type_id: str | None


@dataclass
class Schedule:
    """One loaded schedule. `proj_id` None means every project in the file."""

    projects: tuple[Project, ...]
    calendars: tuple[Calendar, ...]
    wbs: tuple[Wbs, ...]
    activities: tuple[Activity, ...]
    relationships: tuple[Relationship, ...]
    assignments: tuple[Assignment, ...]
    activity_codes: tuple[ActivityCode, ...]
    absent_columns: frozenset[str] = field(default_factory=frozenset)
    absent_tables: frozenset[str] = field(default_factory=frozenset)
    parse_notes: tuple[str, ...] = ()
    cost_column_present: bool = False

    def calendar_for(self, clndr_id: str | None) -> Calendar | None:
        if clndr_id is None:
            return None
        for calendar in self.calendars:
            if calendar.clndr_id == clndr_id:
                return calendar
        return None

    def select(self, proj_id: str | None) -> Schedule:
        """Narrow activities and relationships to one project id."""
        if proj_id is None:
            return self
        activities = tuple(item for item in self.activities if item.proj_id == proj_id)
        task_ids = {item.task_id for item in activities if item.task_id is not None}
        relationships = tuple(
            item
            for item in self.relationships
            if item.task_id in task_ids or item.pred_task_id in task_ids
        )
        assignments = tuple(item for item in self.assignments if item.task_id in task_ids)
        codes = tuple(item for item in self.activity_codes if item.task_id in task_ids)
        wbs = tuple(item for item in self.wbs if item.proj_id == proj_id)
        projects = tuple(item for item in self.projects if item.proj_id == proj_id)
        return Schedule(
            projects=projects,
            calendars=self.calendars,
            wbs=wbs,
            activities=activities,
            relationships=relationships,
            assignments=assignments,
            activity_codes=codes,
            absent_columns=self.absent_columns,
            absent_tables=self.absent_tables,
            parse_notes=self.parse_notes,
            cost_column_present=self.cost_column_present,
        )
