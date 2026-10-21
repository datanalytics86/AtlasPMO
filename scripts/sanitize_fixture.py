"""Anonymize a fixture XER. Do not point this at a real schedule.

ERMHDR has no verified field layout, so every field after the marker
becomes ANON. Columns whose names mention user, obs or db are cleared.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from atlaspmo.io.xer import read_xer_bytes

SENSITIVE = ("user", "obs", "db")


def sanitize(raw: bytes) -> bytes:
    document = read_xer_bytes_safe(raw)
    lines = list(document.lines)
    if lines and lines[0].startswith("ERMHDR"):
        parts = lines[0].split("\t")
        lines[0] = "\t".join(["ERMHDR"] + ["ANON"] * (len(parts) - 1))
    for table in document.tables:
        sensitive = [
            index
            for index, name in enumerate(table.fields)
            if any(token in name.lower() for token in SENSITIVE)
        ]
        if not sensitive:
            continue
        for row in table.rows:
            cells = lines[row.line_index].split("\t")
            for index in sensitive:
                cell_at = index + 1
                if cell_at < len(cells):
                    cells[cell_at] = "ANON"
            lines[row.line_index] = "\t".join(cells)
    text = document.newline.join(lines)
    if document.trailing_newline:
        text += document.newline
    return text.encode("cp1252")


def read_xer_bytes_safe(raw: bytes):
    return read_xer_bytes(raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Anonimiza un XER de fixture.")
    parser.add_argument("source", type=Path)
    parser.add_argument("dest", type=Path)
    args = parser.parse_args(argv)
    args.dest.write_bytes(sanitize(args.source.read_bytes()))
    print(args.dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
