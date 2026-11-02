"""E8: masked confirmation matches the reference and does not rebuild the model."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

import pytest
from scripts.gen_scale import write_scale
from tests.oracle.pathlen import alternate_is_long_enough

from atlaspmo.analysis.logic import redundant
from atlaspmo.analysis.logic.redundant import classify_links
from atlaspmo.engine import fast
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.engine.fast import LAST, cached_compiled, replay_masked
from atlaspmo.engine.options import EngineOptions
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.model.schedule import Activity, Calendar, Project, Relationship, Schedule
from atlaspmo.numeric.intervals import to_minute
from test_cpm import _link, _load, _task


def _status(schedule, options: EngineOptions | None = None) -> dict[str, str]:
    classes, _base = classify_links(schedule, options)
    return {item.task_pred_id: item.status for item in classes}


def _assert_same(schedule, options: EngineOptions | None = None) -> dict[str, str]:
    chosen = options or EngineOptions()
    fast = _status(schedule, replace(chosen, engine="fast"))
    assert LAST["path"] == "fast"
    reference = _status(schedule, replace(chosen, engine="reference"))
    assert fast == reference
    return fast


def test_pathlen_oracle_says_the_long_way_covers_a_zero_lag() -> None:
    assert alternate_is_long_enough((8, 8), 0)
    assert not alternate_is_long_enough((8,), 16)


def test_confirmation_masks_edges_and_keeps_the_calendar_tables(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "8")],
        [_link("12", "1", "2"), _link("23", "2", "3"), _link("13", "1", "3")],
    )
    LAST["mask_passes"] = 0
    tables: dict[str, int] = {}
    real_cpm = redundant.schedule_cpm
    real_fast = fast.schedule_cpm_fast
    real_compile = fast._compile
    real_tables = fast.build_tables

    def schedule_once(schedule, options=None):
        if int(LAST["mask_passes"]) > 0:
            raise AssertionError("schedule_cpm during confirmation")
        result = real_cpm(schedule, options)
        compiled = cached_compiled(schedule, options)
        if compiled is not None and compiled.tables is not None:
            tables["id"] = id(compiled.tables)
        return result

    def reject_fast(*args, **kwargs):
        if int(LAST["mask_passes"]) > 0:
            raise AssertionError("schedule_cpm_fast during confirmation")
        return real_fast(*args, **kwargs)

    def reject_compile(*args, **kwargs):
        if int(LAST["mask_passes"]) > 0:
            raise AssertionError("_compile during confirmation")
        return real_compile(*args, **kwargs)

    def reject_tables(*args, **kwargs):
        if int(LAST["mask_passes"]) > 0:
            raise AssertionError("build_tables during confirmation")
        return real_tables(*args, **kwargs)

    redundant.schedule_cpm = schedule_once
    fast.schedule_cpm_fast = reject_fast
    fast._compile = reject_compile
    fast.build_tables = reject_tables
    try:
        classes, _base = classify_links(schedule)
    finally:
        redundant.schedule_cpm = real_cpm
        fast.schedule_cpm_fast = real_fast
        fast._compile = real_compile
        fast.build_tables = real_tables
    assert int(LAST["mask_passes"]) > 0
    compiled = cached_compiled(schedule, EngineOptions())
    assert compiled is not None
    assert compiled.tables is not None
    assert id(compiled.tables) == tables["id"]
    assert any(item.status == "redundante_confirmado" for item in classes)


def test_hand_list_freezes_the_origin_filter(tmp_path: Path) -> None:
    """Six activities. Only the zero-lag shortcut 1→3 has another path at least as long.

    The chain links are the only way into their heads, so they are not candidates.
    The literal below is not read from ``_candidate_ids``.
    """
    schedule = _load(
        tmp_path,
        [_task(str(index), f"A{index}", "8") for index in range(1, 7)],
        [
            _link("12", "1", "2"),
            _link("23", "2", "3"),
            _link("34", "3", "4"),
            _link("45", "4", "5"),
            _link("56", "5", "6"),
            _link("13", "1", "3"),
        ],
    )
    # Hand list: shortcut is a candidate; the five chain links are not.
    expect_not_candidates = {"12", "23", "34", "45", "56"}
    statuses = _assert_same(schedule)
    assert statuses["13"] == "redundante_confirmado"
    no_candidato = {key for key, value in statuses.items() if value == "no_candidato"}
    assert no_candidato == expect_not_candidates


def test_ss_ff_pair_stays_protected_and_out_of_the_candidates(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("ss", "1", "2", "PR_SS"), _link("ff", "1", "2", "PR_FF")],
    )
    statuses = _assert_same(schedule)
    assert statuses == {"ss": "protegido", "ff": "protegido"}


def test_mutual_pair_matches_the_reference(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2"), _link("2", "1", "2")],
    )
    statuses = _assert_same(schedule)
    assert list(statuses.values()).count("redundante_confirmado") == 1


def test_open_end_is_not_confirmed_even_if_dates_could_match(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "8"),
            _task("2", "B", "8", cstr="CS_MSO", cstr_date="2026-01-06 08:00"),
        ],
        [_link("1", "1", "2")],
    )
    statuses = _assert_same(schedule)
    assert statuses["1"] != "redundante_confirmado"


def test_external_link_stays_protected(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2")],
    )
    link = schedule.relationships[0]
    schedule = replace(schedule, relationships=(replace(link, pred_proj_id="9"),))
    statuses = _assert_same(schedule)
    assert statuses["1"] == "protegido"


def test_cycle_has_no_candidates(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("12", "1", "2"), _link("21", "2", "1")],
    )
    statuses = _assert_same(schedule)
    assert set(statuses.values()) == {"no_candidato"}


def test_a_lag_longer_than_the_chain_is_not_a_candidate(tmp_path: Path) -> None:
    # 24 h is more than the 16 h chain, so the event filter does not offer it.
    loose = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "8")],
        [_link("12", "1", "2"), _link("23", "2", "3"), _link("13", "1", "3", "PR_FS", "24")],
    )
    loose_status = _assert_same(loose)
    assert loose_status["13"] == "no_candidato"


def test_masked_pass_matches_the_reference_minutes(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "8")],
        [_link("12", "1", "2"), _link("23", "2", "3"), _link("13", "1", "3")],
    )
    _assert_masked_equals_reference(schedule, frozenset({"13"}))


def test_masked_pass_matches_the_reference_on_scale_200(tmp_path: Path) -> None:
    path = tmp_path / "scale200.xer"
    write_scale(path, 200, series=False)
    schedule = schedule_from_xer(read_xer(path))
    statuses = _assert_same(schedule)
    drop = frozenset(
        key for key, value in list(statuses.items())[:8] if value == "redundante_confirmado"
    )
    if not drop:
        drop = frozenset({schedule.relationships[0].task_pred_id or ""})
    _assert_masked_equals_reference(schedule, drop)


def _assert_masked_equals_reference(schedule, drop: frozenset[str]) -> None:
    schedule_cpm(schedule, EngineOptions(engine="fast"))
    assert LAST["path"] == "fast"
    compiled = cached_compiled(schedule, EngineOptions())
    assert compiled is not None
    stacked = replay_masked(compiled, drop)
    assert stacked is not None
    reduced = replace(
        schedule,
        relationships=tuple(
            item for item in schedule.relationships if (item.task_pred_id or "") not in drop
        ),
    )
    reference = schedule_cpm(reduced, EngineOptions(engine="reference"))
    by_index = {task_id: index for index, task_id in enumerate(compiled.task_ids)}
    for task_id, item in reference.by_id.items():
        if task_id not in by_index:
            continue
        index = by_index[task_id]
        for row, moment in (
            (0, item.early_start),
            (1, item.early_finish),
            (2, item.late_start),
            (3, item.late_finish),
        ):
            assert abs(int(stacked[row, index]) - _minute(moment)) <= 1
        assert abs(int(stacked[4, index]) - round(item.total_float_hours * 60)) <= 1
        assert abs(int(stacked[5, index]) - round(item.free_float_hours * 60)) <= 1


def _minute(moment) -> int:
    return to_minute(moment)


_EXCEL = date(1899, 12, 30)
_DATA = datetime(2026, 1, 5, 8, 0)
_CONSTRAINTS = [
    "CS_MSO",
    "CS_MSOA",
    "CS_MSOB",
    "CS_MEO",
    "CS_MEOA",
    "CS_MEOB",
    "CS_MANDSTART",
    "CS_MANDFIN",
    "CS_ALAP",
]


def _clndr_data(kind: str, holiday: date | None = None) -> str:
    if kind == "half":
        working = {2, 3, 4, 5, 6}
        start, finish = "08:00", "12:00"
    elif kind == "full":
        working = set(range(1, 8))
        start, finish = "00:00", "00:00"
    else:
        working = set(range(1, 8))
        start, finish = "08:00", "16:00"
    chunks: list[str] = []
    for number in range(1, 8):
        if number in working:
            chunks.append(f"(0||{number}()((0||0(s|{start}|f|{finish})())))")
        else:
            chunks.append(f"(0||{number}()())")
    extra = ""
    if holiday is not None:
        serial = (holiday - _EXCEL).days
        extra = f"(0||Exceptions()((0||0(d|{serial})())))"
    body = "".join(chunks)
    return f"(0||CalendarData()((0||DaysOfWeek()({body})){extra}(0||VIEW(ShowTotal|N)())))"


def _plain(task_id: str, hours: float = 8) -> Activity:
    return Activity(
        task_id=task_id,
        proj_id="1",
        wbs_id="W1",
        clndr_id="C1",
        task_code=task_id,
        task_name=task_id,
        task_type="TT_Task",
        status_code="TK_NotStart",
        complete_pct_type=None,
        cstr_type=None,
        cstr_type2=None,
        target_drtn_hr_cnt=hours,
        remain_drtn_hr_cnt=hours,
        total_float_hr_cnt=None,
        free_float_hr_cnt=None,
        target_start_date=None,
        target_end_date=None,
        act_start_date=None,
        act_end_date=None,
        early_start_date=None,
        early_end_date=None,
        late_start_date=None,
        late_end_date=None,
        float_path=None,
        float_path_order=None,
        int_path=None,
        int_path_order=None,
        phys_complete_pct=None,
    )


def _on_calendar(kind: str, holiday: date | None = None) -> Schedule:
    return Schedule(
        projects=(Project("1", "P", "P", "C1", _DATA, None, None),),
        calendars=(Calendar("C1", "C1", "1", 8, None, _clndr_data(kind, holiday)),),
        wbs=(),
        activities=(_plain("1"), _plain("2"), _plain("3")),
        relationships=(
            Relationship("12", "2", "1", "1", "1", "PR_FS", 0),
            Relationship("23", "3", "2", "1", "1", "PR_FS", 0),
            Relationship("13", "3", "1", "1", "1", "PR_FS", 0),
        ),
        assignments=(),
        activity_codes=(),
    )


def test_s7_four_link_types_fs_ss_ff_sf(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A"), _task("2", "B"), _task("3", "C"), _task("4", "D")],
        [
            _link("fs", "1", "2", "PR_FS"),
            _link("ss", "1", "3", "PR_SS"),
            _link("ff", "2", "4", "PR_FF"),
            _link("sf", "3", "4", "PR_SF"),
        ],
    )
    _assert_same(schedule)


def test_s7_positive_and_negative_lag(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A"), _task("2", "B"), _task("3", "C")],
        [
            _link("pos", "1", "2", "PR_FS", "8"),
            _link("neg", "1", "3", "PR_FS", "-4"),
            _link("23", "2", "3"),
        ],
    )
    _assert_same(schedule)


def test_s7_holiday() -> None:
    _assert_same(_on_calendar("all", date(2026, 1, 7)))


def test_s7_half_day() -> None:
    _assert_same(_on_calendar("half"))


def test_s7_twenty_four_hour_day() -> None:
    _assert_same(_on_calendar("full"))


@pytest.mark.parametrize("cstr", _CONSTRAINTS)
def test_s7_supported_constraint(tmp_path: Path, cstr: str) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "A"),
            _task("2", "B", cstr=cstr, cstr_date="2026-01-06 08:00"),
            _task("3", "C"),
        ],
        [_link("12", "1", "2"), _link("23", "2", "3"), _link("13", "1", "3")],
    )
    _assert_same(schedule)


@pytest.mark.parametrize("progress", ["retained", "progress_override"])
def test_s7_out_of_sequence(tmp_path: Path, progress: str) -> None:
    # B started Monday; the 24 h predecessor would finish after that actual start.
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", "24"),
            _task("2", "B", status="TK_Active", act_start="2026-01-05 08:00"),
            _task("3", "C"),
        ],
        [_link("12", "1", "2"), _link("23", "2", "3"), _link("13", "1", "3")],
    )
    _assert_same(schedule, EngineOptions(progress=progress))


def test_s7_milestone(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "A"),
            _task("2", "M", "0", "TT_Mile"),
            _task("3", "F", "0", "TT_FinMile"),
            _task("4", "C"),
        ],
        [
            _link("12", "1", "2"),
            _link("23", "2", "3"),
            _link("34", "3", "4"),
            _link("14", "1", "4"),
        ],
    )
    _assert_same(schedule)


def test_s7_loe(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "A"),
            _task("2", "B"),
            _task("3", "L", "0", "TT_LOE"),
        ],
        [_link("12", "1", "2"), _link("13", "1", "3"), _link("32", "3", "2")],
    )
    _assert_same(schedule)


def test_s7_wbs(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [
            _task("1", "A", wbs="W1"),
            _task("2", "B", wbs="W1"),
            _task("3", "W", "0", "TT_WBS", wbs="W1"),
        ],
        [_link("12", "1", "2")],
    )
    _assert_same(schedule)


def test_s7_not_driver_and_not_redundant(tmp_path: Path) -> None:
    """SS lag 0 beside the FS that sets the early start. The SS is not confirmed."""
    schedule = _load(
        tmp_path,
        [_task("1", "A", "16"), _task("2", "B")],
        [_link("fs", "1", "2", "PR_FS", "0"), _link("ss", "1", "2", "PR_SS", "0")],
    )
    statuses = _assert_same(schedule)
    assert statuses["ss"] == "candidato_no_confirmado"
