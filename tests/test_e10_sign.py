"""Second signature: CPLI with an SS overlap and a holiday, and BEI 2/2."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from tests.oracle.bei import ratio as bei_ratio
from tests.oracle.span_holiday import cpli_ratio, work_minutes

from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from atlaspmo.engine.cpm import schedule_cpm
from atlaspmo.engine.options import EngineOptions
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer

CASES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "synthetic" / "cases"

MON_8 = datetime(2026, 1, 5, 8, 0)
MON_16 = datetime(2026, 1, 5, 16, 0)
WED_8 = datetime(2026, 1, 7, 8, 0)
WED_16 = datetime(2026, 1, 7, 16, 0)
THU_16 = datetime(2026, 1, 8, 16, 0)
FRI_16 = datetime(2026, 1, 9, 16, 0)
DATA = datetime(2026, 2, 1, 0, 0)
BEI_ROWS = (
    ("LATE", "TK_Complete", datetime(2026, 1, 12, 8, 0), datetime(2026, 1, 10, 8, 0)),
    ("OPEN", "TK_NotStart", None, datetime(2026, 1, 20, 8, 0)),
    ("EARLY", "TK_Complete", datetime(2026, 1, 5, 16, 0), datetime(2026, 3, 1, 8, 0)),
)


def test_holiday_span_returns_four_thirds() -> None:
    assert work_minutes(WED_8, WED_16) == 0
    length = work_minutes(MON_8, THU_16)
    slack = work_minutes(THU_16, FRI_16)
    assert length == 24 * 60
    assert slack == 8 * 60
    assert cpli_ratio(MON_8, THU_16, FRI_16) == (length + slack) / length
    assert cpli_ratio(MON_8, THU_16, FRI_16) == (24 + 8) / 24


def test_bei_rows_return_two_over_two() -> None:
    assert bei_ratio(BEI_ROWS, DATA) == 2 / 2


def test_evaluate_matches_the_oracles() -> None:
    profile, _note = load_profile("dcma_estricto")
    cpli = schedule_from_xer(read_xer(CASES / "cpli_ss.xer"))
    stored = {item.task_code: item for item in cpli.activities}
    assert stored["A"].early_end_date == THU_16
    assert stored["A"].float_path == "1"
    assert stored["B"].early_start_date == MON_8
    assert stored["B"].early_end_date == MON_16
    assert stored["B"].float_path != "1"
    metrics, _findings, _notes = evaluate(cpli, profile, None)
    assert metrics["cpli"].value == cpli_ratio(MON_8, THU_16, FRI_16)
    assert metrics["cpli"].status == "cumple"
    whole = schedule_from_xer(read_xer(CASES / "bei.xer"))
    metrics, _findings, _notes = evaluate(whole.select("1"), profile, whole.select("2"))
    assert metrics["bei"].value == bei_ratio(BEI_ROWS, DATA)
    assert metrics["bei"].status == "cumple"


def test_reference_cpm_finishes_thursday_and_monday() -> None:
    schedule = schedule_from_xer(read_xer(CASES / "cpli_ss.xer"))
    result = schedule_cpm(schedule, EngineOptions(engine="reference"))
    by_code = {item.task_code: item.task_id for item in schedule.activities}
    a_id = by_code["A"]
    b_id = by_code["B"]
    assert a_id is not None
    assert b_id is not None
    assert result.by_id[a_id].early_finish == THU_16
    assert result.by_id[b_id].early_finish == MON_16
