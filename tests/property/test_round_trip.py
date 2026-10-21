"""Invariant a: an unchanged XER round-trips to the same bytes."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from atlaspmo.io.synthetic import encode_xer
from atlaspmo.io.xer import read_xer_bytes

settings.register_profile("qa", max_examples=500, deadline=None, derandomize=True)
settings.load_profile("qa")

_HOURS = st.sampled_from(("8", "16", "24"))


@given(hours=_HOURS, undefined=st.booleans())
def test_round_trip(hours: str, undefined: bool) -> None:
    raw = encode_xer(
        "ERMHDR\t20.12",
        [
            {
                "name": "TASK",
                "fields": ["task_id", "task_code", "remain_drtn_hr_cnt"],
                "rows": [["1", "A1", hours]],
            }
        ],
    )
    if undefined:
        raw = raw.replace(b"A1", b"A\x81", 1)
    assert read_xer_bytes(raw).to_bytes() == raw
