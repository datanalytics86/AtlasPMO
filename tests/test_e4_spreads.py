"""fact_timephased stores remaining hours in one bucket. It is not a period curve."""

from __future__ import annotations

from pathlib import Path

import duckdb

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.resources.module import EvmConfig, EvmModule
from atlaspmo.reports.parquet_star import write_star
from test_cpm import _link, _load, _task


def test_remaining_hours_land_in_the_data_date_bucket(tmp_path: Path) -> None:
    schedule = _load(
        tmp_path,
        [_task("1", "A", "8"), _task("2", "B", "16")],
        [_link("1", "1", "2")],
    )
    result = EvmModule().run(AnalysisContext(schedule=schedule), EvmConfig())
    text = " ".join(result.approximations)
    assert "balde corte" in text
    assert "No es una curva por periodo" in text
    written = write_star(tmp_path / "star", [result], project_name="Cadena", run_id="r1")
    target = str(written["fact_timephased"]).replace("\\", "/")
    con = duckdb.connect()
    try:
        rows = con.execute(
            f"SELECT task_code, bucket, hours FROM read_parquet('{target}') ORDER BY task_code"
        ).fetchall()
    finally:
        con.close()
    assert rows == [("A", "corte", 8.0), ("B", "corte", 16.0)]
