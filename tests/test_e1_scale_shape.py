"""B-14: a non-series scale network has the shape section 7 asks for."""

from __future__ import annotations

from scripts.gen_scale import build_tables


def test_realistic_scale_has_wbs_holiday_mixed_links_and_progress() -> None:
    tables = build_tables(24, series=False)
    by_name = {str(table["name"]): table["rows"] for table in tables}
    calendars = by_name["CALENDAR"]
    wbs = by_name["PROJWBS"]
    tasks = by_name["TASK"]
    preds = by_name["TASKPRED"]
    assert isinstance(calendars, list)
    assert len(calendars) >= 2
    assert isinstance(wbs, list)
    assert len(wbs) >= 2
    assert isinstance(tasks, list)
    assert isinstance(preds, list)
    assert {row[5] for row in preds} >= {"PR_FS", "PR_SS", "PR_FF", "PR_SF"}
    assert any(row[6] not in {"", "0"} for row in preds)
    assert any(row[7] == "TK_Active" and row[8] != row[9] for row in tasks)
    assert any(row[10] == "CS_MSO" for row in tasks)
    assert any("Exceptions" in row[4] for row in calendars)
    average = len(preds) / len(tasks)
    assert 2 <= average <= 3
