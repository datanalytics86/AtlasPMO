"""Excel, PDF and run manifest. Spanish labels, es-CL numbers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import xlsxwriter
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from atlaspmo import __version__
from atlaspmo.analysis.contract import ModuleResult
from atlaspmo.ui.format_es import format_number


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def git_commit(root: Path) -> str | None:
    git = _git_executable()
    if git is None:
        return None
    try:
        done = subprocess.run(
            [git, "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    token = done.stdout.strip()
    return token or None


def write_excel(path: Path, results: list[ModuleResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = xlsxwriter.Workbook(str(path))
    summary = workbook.add_worksheet("Resumen")
    summary.write_row(0, 0, ["Módulo", "Métrica", "Valor", "Umbral", "Estado"])
    row_index = 1
    for result in results:
        for name, metric in result.metrics.items():
            summary.write_row(
                row_index,
                0,
                [
                    result.module_id,
                    name,
                    _num(metric.value),
                    _num(metric.threshold),
                    metric.status,
                ],
            )
            row_index += 1
        sheet = workbook.add_worksheet(_sheet_name(result.module_id))
        columns = list(result.findings.columns)
        sheet.write_row(0, 0, columns)
        for offset, record in enumerate(result.findings.itertuples(index=False), start=1):
            sheet.write_row(offset, 0, ["" if item is None else str(item) for item in record])
    workbook.close()


def write_pdf(path: Path, results: list[ModuleResult], title: str = "AtlasPMO") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]
    for result in results:
        story.append(Paragraph(result.module_id, styles["Heading2"]))
        index = result.metrics.get("quality_index")
        if index is not None and index.value is not None:
            story.append(Paragraph(f"Índice: {format_number(index.value, 1)}", styles["Normal"]))
        for name, metric in result.metrics.items():
            if name == "quality_index":
                continue
            value = "—" if metric.value is None else format_number(metric.value, 2)
            story.append(Paragraph(f"{name}: {value} ({metric.status})", styles["Normal"]))
        if result.approximations:
            notes = "; ".join(result.approximations)
            story.append(Paragraph(f"Aproximaciones: {notes}", styles["Normal"]))
        story.append(Spacer(1, 8))
    SimpleDocTemplate(str(path), pagesize=A4).build(story)


def write_manifest(
    path: Path,
    results: list[ModuleResult],
    source: Path | None,
    root: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "app_version": __version__,
        "git_commit": git_commit(root),
        "input_sha256": file_sha256(source) if source else None,
        "input_name": source.name if source else None,
        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "modules": [item.module_id for item in results],
        "approximations": [note for item in results for note in item.approximations],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _num(value: float | None) -> str:
    if value is None:
        return ""
    return format_number(value, 2)


def _sheet_name(module_id: str) -> str:
    cleaned = "".join(char if char.isalnum() else "_" for char in module_id)[:31]
    return cleaned or "modulo"


def _git_executable() -> str | None:
    candidates = (
        "git",
        r"C:\Users\nicolas.andrade\AppData\Local\Programs\Git\cmd\git.exe",
    )
    for candidate in candidates:
        try:
            subprocess.run([candidate, "--version"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            continue
        return candidate
    return None
