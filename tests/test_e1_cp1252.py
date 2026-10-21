"""B-20: undefined cp1252 bytes stay in the round-trip and are noted."""

from __future__ import annotations

from pathlib import Path

from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer, read_xer_bytes

_UNDEFINED = bytes((0x81, 0x8D, 0x8F, 0x90, 0x9D))


def _xer_with_undefined_name() -> bytes:
    return (
        b"ERMHDR\t20.12\r\n"
        b"%T\tTASK\r\n"
        b"%F\ttask_id\ttask_name\r\n"
        b"%R\t1\tA" + _UNDEFINED + b"B\r\n"
        b"%E\r\n"
    )


def test_undefined_cp1252_bytes_round_trip(tmp_path: Path) -> None:
    raw = _xer_with_undefined_name()
    path = tmp_path / "indefinidos.xer"
    path.write_bytes(raw)
    document = read_xer(path)
    assert document.to_bytes() == raw
    assert read_xer_bytes(raw).to_bytes() == raw
    schedule = schedule_from_xer(document)
    notes = " ".join((*document.parse_notes, *schedule.parse_notes))
    for byte in _UNDEFINED:
        assert f"0x{byte:02X}" in notes
    assert "aproximaci" in notes.lower()
    name = schedule.activities[0].task_name
    assert name is not None
    assert name.encode("cp1252", errors="surrogateescape") == b"A" + _UNDEFINED + b"B"
