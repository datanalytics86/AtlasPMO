"""Fast redundancy classes match the reference engine on generated nets."""

from __future__ import annotations

from hypothesis import assume, given, settings
from tests.property.test_e7_differential import _nets

from atlaspmo.analysis.logic.redundant import classify_links
from atlaspmo.engine.fast import LAST
from atlaspmo.engine.options import EngineOptions


def _classes(schedule, options: EngineOptions) -> dict[str, str]:
    found, _base = classify_links(schedule, options)
    return {item.task_pred_id: item.status for item in found}


@given(_nets())
@settings(max_examples=500, deadline=None, derandomize=True)
def test_fast_link_classes_match_the_reference(case) -> None:
    schedule, options = case
    fast = EngineOptions(
        options.progress,
        options.lag_calendar,
        options.float_kind,
        options.critical_hours,
        options.critical_rule,
        "fast",
    )
    fast_classes = _classes(schedule, fast)
    assume(LAST["path"] == "fast")
    reference = EngineOptions(
        options.progress,
        options.lag_calendar,
        options.float_kind,
        options.critical_hours,
        options.critical_rule,
        "reference",
    )
    assert fast_classes == _classes(schedule, reference)
