"""Structural XER writer for synthetic fixtures.

Tokens follow docs/MEGAPROMPT.md section 5: a header line that starts with
ERMHDR, table blocks marked %T / %F / %R, and a final %E line. Column names
are supplied by the caller. This module does not claim they are P6 fields.
"""

from __future__ import annotations

from pathlib import Path


def _cell(value: str) -> str:
    if "\t" in value or "\r" in value or "\n" in value:
        raise ValueError("XER cells cannot contain tabs or line breaks")
    return value


def encode_xer(header: str, tables: list[dict[str, object]]) -> bytes:
    """Encode one XER document as cp1252 with CRLF line endings."""
    if "\r" in header or "\n" in header:
        raise ValueError("header must be a single line")
    if not header.startswith("ERMHDR"):
        raise ValueError("header must start with ERMHDR")
    lines = [header]
    for table in tables:
        name = _cell(str(table["name"]))
        fields_obj = table["fields"]
        rows_obj = table["rows"]
        if not isinstance(fields_obj, list) or not isinstance(rows_obj, list):
            raise ValueError("fields and rows must be lists")
        fields = [_cell(str(item)) for item in fields_obj]
        lines.append("%T\t" + name)
        lines.append("%F\t" + "\t".join(fields))
        for row in rows_obj:
            if not isinstance(row, list) or len(row) != len(fields):
                raise ValueError("row width does not match fields")
            cells = [_cell(str(item)) for item in row]
            lines.append("%R\t" + "\t".join(cells))
    lines.append("%E")
    text = "\r\n".join(lines) + "\r\n"
    return text.encode("cp1252")


def write_xer(path: Path, header: str, tables: list[dict[str, object]]) -> None:
    """Write encode_xer output to path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encode_xer(header, tables))
