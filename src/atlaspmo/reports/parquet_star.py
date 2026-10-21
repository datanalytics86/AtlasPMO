"""Star-schema Parquet. Empty facts stay empty instead of inventing rows."""

from __future__ import annotations

import io
import tempfile
import zipfile
from pathlib import Path

import duckdb

from atlaspmo.analysis.contract import ModuleResult

_TABLES = (
    "dim_project",
    "dim_run",
    "dim_activity",
    "dim_rule",
    "fact_finding",
    "fact_timephased",
    "fact_risk",
)


def parquet_zip_bytes(
    results: list[ModuleResult],
    *,
    project_name: str,
    run_id: str,
) -> bytes:
    """Zip the seven star tables. The caller does not keep the temp folder."""
    with tempfile.TemporaryDirectory() as folder:
        written = write_star(
            Path(folder),
            results,
            project_name=project_name,
            run_id=run_id,
        )
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for path in written.values():
                archive.write(path, arcname=path.name)
        return buffer.getvalue()


def write_star(
    folder: Path,
    results: list[ModuleResult],
    *,
    project_name: str,
    run_id: str,
) -> dict[str, Path]:
    """Write the seven star tables.

    Time-phased rows, when the EVM table has ``spread_hours``, are the
    remaining duration in the single bucket ``corte``. They are not a
    period curve.
    """
    folder.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()
    try:
        _create(con)
        _fill(con, results, project_name, run_id)
        written: dict[str, Path] = {}
        for name in _TABLES:
            path = folder / f"{name}.parquet"
            destination = str(path).replace("\\", "/").replace("'", "''")
            con.execute(f"COPY {name} TO '{destination}' (FORMAT PARQUET)")
            written[name] = path
        return written
    finally:
        con.close()


def _create(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("CREATE TABLE dim_project (project_id VARCHAR, proj_short_name VARCHAR)")
    con.execute(
        """
        CREATE TABLE dim_run (
            run_id VARCHAR,
            seed INTEGER,
            quality_index DOUBLE,
            input_name VARCHAR
        )
        """
    )
    con.execute("CREATE TABLE dim_activity (run_id VARCHAR, task_code VARCHAR, task_name VARCHAR)")
    con.execute("CREATE TABLE dim_rule (rule_id VARCHAR, rule_name_es VARCHAR, source VARCHAR)")
    con.execute(
        """
        CREATE TABLE fact_finding (
            run_id VARCHAR,
            rule_id VARCHAR,
            task_code VARCHAR,
            object_id VARCHAR,
            passed BOOLEAN,
            value VARCHAR,
            message_es VARCHAR
        )
        """
    )
    con.execute(
        """
        CREATE TABLE fact_timephased (
            run_id VARCHAR,
            task_code VARCHAR,
            bucket VARCHAR,
            hours DOUBLE
        )
        """
    )
    con.execute(
        """
        CREATE TABLE fact_risk (
            run_id VARCHAR,
            task_code VARCHAR,
            criticality DOUBLE
        )
        """
    )


def _fill(
    con: duckdb.DuckDBPyConnection,
    results: list[ModuleResult],
    project_name: str,
    run_id: str,
) -> None:
    con.execute("INSERT INTO dim_project VALUES ('1', ?)", [project_name])
    seed = next((item.metadata.seed for item in results if item.metadata.seed is not None), None)
    quality = None
    for result in results:
        metric = result.metrics.get("quality_index")
        if metric is not None and metric.value is not None:
            quality = metric.value
    con.execute("INSERT INTO dim_run VALUES (?, ?, ?, ?)", [run_id, seed, quality, None])
    rules: set[tuple[str, str, str]] = set()
    for result in results:
        frame = result.findings
        if "rule_id" not in frame.columns:
            continue
        for row in frame.itertuples(index=False):
            rules.add((str(row.rule_id), str(row.rule_name_es), str(row.source)))
            con.execute(
                "INSERT INTO fact_finding VALUES (?, ?, ?, ?, ?, ?, ?)",
                [
                    run_id,
                    row.rule_id,
                    row.task_code,
                    row.object_id,
                    row.passed,
                    None if row.value is None else str(row.value),
                    row.message_es,
                ],
            )
        risk = result.tables.get("activities")
        if result.module_id == "risk" and risk is not None and "criticality" in risk.columns:
            for row in risk.itertuples(index=False):
                con.execute(
                    "INSERT INTO fact_risk VALUES (?, ?, ?)",
                    [run_id, row.task_code, row.criticality],
                )
        phased = result.tables.get("activities")
        if result.module_id == "evm" and phased is not None and "spread_hours" in phased.columns:
            for row in phased.itertuples(index=False):
                hours = row.spread_hours
                if not isinstance(hours, int | float):
                    continue
                con.execute(
                    "INSERT INTO fact_timephased VALUES (?, ?, ?, ?)",
                    [run_id, row.task_code, "corte", float(hours)],
                )
    for rule_id, name, source in sorted(rules):
        con.execute("INSERT INTO dim_rule VALUES (?, ?, ?)", [rule_id, name, source])
