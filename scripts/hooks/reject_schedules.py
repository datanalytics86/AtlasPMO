"""Reject schedule files committed outside tests/fixtures.

Blocks *.xer and *.mpp by extension. Blocks *.xml only when the bytes
contain a P6 export root or the MS Project XML namespace. Those two
markers are recognition signatures, not a schema.
"""

from __future__ import annotations

import sys
from pathlib import Path

FIXTURE_PREFIX = "tests/fixtures/"
SCHEDULE_EXTENSIONS = {".xer", ".mpp"}
XML_MARKERS = (
    b"APIBusinessObjects",
    b"http://schemas.microsoft.com/project",
)


def _normalize(path: str) -> str:
    parts: list[str] = []
    for part in path.replace("\\", "/").split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def is_under_fixtures(path: str) -> bool:
    """True when the path is inside the sanctioned fixture tree."""
    normalized = _normalize(path)
    return normalized == "tests/fixtures" or normalized.startswith(FIXTURE_PREFIX)


def forbidden_reason(path: str, content: bytes | None = None) -> str | None:
    """Return a rejection message, or None when the path may be committed."""
    if is_under_fixtures(path):
        return None
    suffix = Path(_normalize(path)).suffix.lower()
    if suffix in SCHEDULE_EXTENSIONS:
        return f"{path}: schedule file outside tests/fixtures/"
    xml_hit = content is not None and any(marker in content for marker in XML_MARKERS)
    if suffix == ".xml" and xml_hit:
        return f"{path}: schedule XML outside tests/fixtures/"
    return None


def main(argv: list[str] | None = None) -> int:
    paths = list(sys.argv[1:] if argv is None else argv)
    failures: list[str] = []
    for raw in paths:
        file_path = Path(raw)
        content = None
        if file_path.suffix.lower() == ".xml" and file_path.is_file():
            content = file_path.read_bytes()
        reason = forbidden_reason(raw, content)
        if reason is not None:
            failures.append(reason)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
