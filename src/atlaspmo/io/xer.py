"""XER reader and writer.

The writer replays the original lines. An unchanged document is byte
identical, including cp1252 bytes and the original newline style.
Column names are not interpreted here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class XerRow:
    """One %R line, cells in field order, plus the source line index."""

    line_index: int
    values: dict[str, str]


@dataclass(frozen=True)
class XerTable:
    """One %T block. `fields` is the %F header, in order."""

    name: str
    fields: tuple[str, ...]
    rows: tuple[XerRow, ...]

    def has_field(self, name: str) -> bool:
        return name in self.fields


@dataclass
class XerFile:
    """Parsed XER plus the lines required to write it back unchanged."""

    newline: str
    trailing_newline: bool
    lines: list[str]
    tables: tuple[XerTable, ...]

    def to_bytes(self) -> bytes:
        """Encode the current lines as cp1252."""
        text = self.newline.join(self.lines)
        if self.trailing_newline:
            text += self.newline
        return text.encode("cp1252")

    def table(self, name: str) -> XerTable | None:
        for item in self.tables:
            if item.name == name:
                return item
        return None

    def drop_rows(self, table_name: str, line_indexes: set[int]) -> XerFile:
        """Return a copy without the given source lines of one table.

        Every other line stays as it was read, so a TASKPRED deletion
        cannot rewrite the rest of the file.
        """
        if not line_indexes:
            return XerFile(self.newline, self.trailing_newline, list(self.lines), self.tables)
        owned = {
            row.line_index
            for table in self.tables
            if table.name == table_name
            for row in table.rows
        }
        unknown = line_indexes - owned
        if unknown:
            raise ValueError(f"line indexes outside {table_name}: {sorted(unknown)}")
        kept = [line for index, line in enumerate(self.lines) if index not in line_indexes]
        return read_xer_bytes(self._encode(kept))

    def _encode(self, lines: list[str]) -> bytes:
        text = self.newline.join(lines)
        if self.trailing_newline:
            text += self.newline
        return text.encode("cp1252")


def read_xer(path: Path) -> XerFile:
    """Read one XER file from disk."""
    return read_xer_bytes(path.read_bytes())


def read_xer_bytes(raw: bytes) -> XerFile:
    """Parse XER bytes. The line list round-trips through `to_bytes`."""
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("XER con BOM: se espera cp1252 sin marca")
    try:
        text = raw.decode("cp1252")
    except UnicodeDecodeError as exc:
        raise ValueError("el archivo no decodifica como cp1252") from exc
    newline, lines, trailing = _split_lines(text)
    if not lines or not lines[0].startswith("ERMHDR"):
        raise ValueError("la primera línea debe empezar por ERMHDR")
    tables = _parse_tables(lines)
    if not any(line.startswith("%E") for line in lines):
        raise ValueError("falta el marcador final %E")
    return XerFile(newline, trailing, lines, tables)


def _split_lines(text: str) -> tuple[str, list[str], bool]:
    newline = "\r\n" if "\r\n" in text else "\n" if "\n" in text else "\r\n"
    trailing = text.endswith(newline)
    body = text[: -len(newline)] if trailing else text
    return newline, body.split(newline), trailing


def _parse_tables(lines: list[str]) -> tuple[XerTable, ...]:
    tables: list[XerTable] = []
    name = ""
    fields: tuple[str, ...] = ()
    rows: list[XerRow] = []
    open_table = False

    def close() -> None:
        nonlocal open_table, rows, fields, name
        if not open_table:
            return
        tables.append(XerTable(name, fields, tuple(rows)))
        open_table = False
        rows = []
        fields = ()
        name = ""

    for index, line in enumerate(lines):
        if line.startswith("%T"):
            close()
            name = _cells(line)[0] if _cells(line) else ""
            open_table = True
            fields = ()
            rows = []
        elif line.startswith("%F") and open_table:
            fields = tuple(_cells(line))
        elif line.startswith("%R") and open_table:
            cells = _cells(line)
            values = {
                fields[pos]: cells[pos] if pos < len(cells) else "" for pos in range(len(fields))
            }
            rows.append(XerRow(index, values))
        elif line.startswith("%E"):
            close()
    close()
    return tuple(tables)


def _cells(line: str) -> list[str]:
    parts = line.split("\t")
    return parts[1:]
