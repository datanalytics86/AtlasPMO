"""Structural synthetic XER. Column names are not P6 fields."""

from __future__ import annotations

from pathlib import Path

import pytest

from atlaspmo.io.synthetic import encode_xer, write_xer

TABLES = [
    {
        "name": "SYNTH",
        "fields": ["col_a", "col_b"],
        "rows": [["1", "ni\u00f1o"]],
    }
]


def test_minimal_xer_is_cp1252_crlf():
    payload = encode_xer("ERMHDR", TABLES)
    assert payload.startswith(b"ERMHDR\r\n")
    assert payload.endswith(b"%E\r\n")
    assert b"\n" not in payload.replace(b"\r\n", b"")
    assert "ni\u00f1o".encode("cp1252") in payload
    assert b"%T\tSYNTH\r\n" in payload
    assert b"%F\tcol_a\tcol_b\r\n" in payload


def test_header_must_start_with_ermhdr():
    with pytest.raises(ValueError):
        encode_xer("NOPE", TABLES)


def test_row_width_is_checked():
    bad = [{"name": "SYNTH", "fields": ["col_a"], "rows": [["1", "2"]]}]
    with pytest.raises(ValueError):
        encode_xer("ERMHDR", bad)


def test_write_round_trip_bytes(tmp_path: Path):
    target = tmp_path / "minimal.xer"
    write_xer(target, "ERMHDR", TABLES)
    assert target.read_bytes() == encode_xer("ERMHDR", TABLES)
