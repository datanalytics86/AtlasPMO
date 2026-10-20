"""Rank every XER in a folder. The schedule math stays out of the UI."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import xlsxwriter

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.bootstrap import bootstrap
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer
from atlaspmo.runner import run_selected


@dataclass(frozen=True)
class BatchRow:
    name: str
    quality_index: float | None


def run_folder(folder: Path, module_ids: list[str] | None = None) -> list[BatchRow]:
    """Run the chosen modules on each XER and rank by quality index."""
    bootstrap()
    chosen = module_ids or ["quality"]
    rows: list[BatchRow] = []
    for path in sorted(folder.glob("*.xer")):
        schedule = schedule_from_xer(read_xer(path))
        results = run_selected(
            chosen,
            AnalysisContext(schedule=schedule, input_name=path.name),
        )
        index = None
        for result in results:
            metric = result.metrics.get("quality_index")
            if metric is not None and metric.value is not None:
                index = metric.value
        rows.append(BatchRow(path.name, index))
    return rank_rows(rows)


def rank_rows(rows: list[BatchRow]) -> list[BatchRow]:
    """Higher index first. A missing index sorts last, then the file name."""
    return sorted(
        rows,
        key=lambda row: (row.quality_index is None, -(row.quality_index or 0.0), row.name),
    )


def write_ranking(path: Path, rows: list[BatchRow]) -> None:
    """Write the ranked rows to one Excel sheet."""
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(str(path))
    sheet = workbook.add_worksheet("ranking")
    sheet.write_row(0, 0, ["archivo", "indice"])
    for offset, row in enumerate(rows, start=1):
        sheet.write(offset, 0, row.name)
        if row.quality_index is None:
            sheet.write(offset, 1, "")
        else:
            sheet.write_number(offset, 1, row.quality_index)
    workbook.close()
