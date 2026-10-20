"""Minimal PBIP. Nicolás opens it in Power BI Desktop; this build does not.

Layout follows Microsoft Learn, 'Power BI Desktop project semantic model folder'
(reviewed 2026-10-20): definition.pbism version 4.0 or above stores TMDL in
definition/. The .pbip shortcut and definition.pbir byPath follow the Fabric
PBIP schema published with that project format. Visuals are left for Nicolás.
"""

from __future__ import annotations

import json
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

_TABLES = (
    ("dim_project", ("project_id", "proj_short_name")),
    ("dim_run", ("run_id", "seed", "quality_index", "input_name")),
    ("dim_activity", ("run_id", "task_code", "task_name")),
    ("dim_rule", ("rule_id", "rule_name_es", "source")),
    (
        "fact_finding",
        ("run_id", "rule_id", "task_code", "object_id", "passed", "value", "message_es"),
    ),
    ("fact_timephased", ("run_id", "task_code", "bucket", "hours")),
    ("fact_risk", ("run_id", "task_code", "criticality")),
)
_MEASURES = (
    ("fact_finding", "Hallazgos", "COUNTROWS(fact_finding)"),
    ("dim_run", "IndicePromedio", "AVERAGE(dim_run[quality_index])"),
)


def write_pbip(folder: Path, parquet_folder: Path) -> Path:
    """Write a report shortcut plus a TMDL model that reads the parquet folder."""
    folder.mkdir(parents=True, exist_ok=True)
    model = folder / "AtlasPMO.SemanticModel"
    report = folder / "AtlasPMO.Report"
    definition = model / "definition"
    (definition / "tables").mkdir(parents=True, exist_ok=True)
    report.mkdir(parents=True, exist_ok=True)
    _json(
        folder / "AtlasPMO.pbip",
        {
            "$schema": (
                "https://developer.microsoft.com/json-schemas/fabric/pbip/"
                "pbipProperties/1.0.0/schema.json"
            ),
            "version": "1.0",
            "artifacts": [{"report": {"path": "AtlasPMO.Report"}}],
            "settings": {"enableAutoRecovery": True},
        },
    )
    _json(
        model / "definition.pbism",
        {
            "$schema": (
                "https://developer.microsoft.com/json-schemas/fabric/item/"
                "semanticModel/definitionProperties/1.0.0/schema.json"
            ),
            "version": "4.2",
            "settings": {"qnaEnabled": False},
        },
    )
    _json(
        report / "definition.pbir",
        {
            "$schema": (
                "https://developer.microsoft.com/json-schemas/fabric/item/"
                "report/definitionProperties/2.0.0/schema.json"
            ),
            "version": "4.0",
            "datasetReference": {"byPath": {"path": "../AtlasPMO.SemanticModel"}},
        },
    )
    _platform(model / ".platform", "SemanticModel", "atlaspmo-semantic-model")
    _platform(report / ".platform", "Report", "atlaspmo-report")
    (definition / "database.tmdl").write_text(
        "database AtlasPMO\n\tcompatibilityLevel: 1567\n",
        encoding="utf-8",
    )
    refs = "\n".join(f"ref table {name}" for name, _columns in _TABLES)
    (definition / "model.tmdl").write_text(
        "model Model\n"
        "\tculture: es-CL\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: es-CL\n\n"
        f"{refs}\n",
        encoding="utf-8",
    )
    (definition / "expressions.tmdl").write_text(_expression(parquet_folder), encoding="utf-8")
    (definition / "relationships.tmdl").write_text(_relationships(), encoding="utf-8")
    for name, columns in _TABLES:
        (definition / "tables" / f"{name}.tmdl").write_text(
            _table(name, columns, parquet_folder),
            encoding="utf-8",
        )
    return folder / "AtlasPMO.pbip"


def _expression(parquet_folder: Path) -> str:
    literal = str(parquet_folder).replace("\\", "\\\\")
    meta = 'meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
    return f'expression ParquetFolder =\n\t\t"{literal}" {meta}\n'


def _table(name: str, columns: tuple[str, ...], parquet_folder: Path) -> str:
    del parquet_folder
    lines = [f"table {name}", f"\tlineageTag: {_tag(name)}", ""]
    for column in columns:
        numeric = column in {"seed", "quality_index", "hours", "criticality"}
        kind = "double" if numeric else "string"
        lines.extend(
            [
                f"\tcolumn {column}",
                f"\t\tdataType: {kind}",
                f"\t\tlineageTag: {_tag(name + '.' + column)}",
                f"\t\tsourceColumn: {column}",
                "\t\tsummarizeBy: none",
                "",
            ]
        )
    for table, measure, dax in _MEASURES:
        if table != name:
            continue
        lines.extend(
            [
                f"\tmeasure {measure} = {dax}",
                "\t\tformatString: #,0",
                "",
            ]
        )
    lines.extend(
        [
            f"\tpartition {name} = m",
            "\t\tmode: import",
            "\t\tsource =",
            "\t\t\t\tlet",
            "\t\t\t\t    Carpeta = ParquetFolder,",
            "\t\t\t\t    Datos = Parquet.Document(File.Contents("
            f'Carpeta & "\\\\" & "{name}.parquet"))',
            "\t\t\t\tin",
            "\t\t\t\t    Datos",
            "",
        ]
    )
    return "\n".join(lines)


def _relationships() -> str:
    pairs = (
        ("finding_run", "fact_finding.run_id", "dim_run.run_id"),
        ("finding_rule", "fact_finding.rule_id", "dim_rule.rule_id"),
        ("risk_run", "fact_risk.run_id", "dim_run.run_id"),
        ("time_run", "fact_timephased.run_id", "dim_run.run_id"),
    )
    blocks = []
    for name, origin, target in pairs:
        blocks.append(f"relationship {name}\n\tfromColumn: {origin}\n\ttoColumn: {target}\n")
    return "\n".join(blocks)


def _platform(path: Path, kind: str, key: str) -> None:
    _json(
        path,
        {
            "$schema": (
                "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/"
                "platformProperties/2.0.0/schema.json"
            ),
            "metadata": {"type": kind, "displayName": "AtlasPMO"},
            "config": {"version": "2.0", "logicalId": str(uuid5(NAMESPACE_URL, key))},
        },
    )


def _json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _tag(name: str) -> str:
    return str(uuid5(NAMESPACE_URL, "atlaspmo-tmdl-" + name))
