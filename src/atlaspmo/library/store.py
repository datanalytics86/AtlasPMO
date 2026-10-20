"""Local DuckDB library. The full schedule is stored only when asked."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import duckdb

from atlaspmo.analysis.contract import ModuleResult
from atlaspmo.model.schedule import Schedule


class Library:
    """Manifests, metrics and findings. Not the schedule, unless requested."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._con = duckdb.connect(str(path))
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id VARCHAR PRIMARY KEY,
                seq INTEGER,
                input_name VARCHAR,
                seed INTEGER
            )
            """
        )
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                run_id VARCHAR,
                metric_name VARCHAR,
                value DOUBLE,
                status VARCHAR
            )
            """
        )
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS findings (
                run_id VARCHAR,
                rule_id VARCHAR,
                task_code VARCHAR,
                message_es VARCHAR
            )
            """
        )
        self._con.execute(
            """
            CREATE TABLE IF NOT EXISTS activities (
                run_id VARCHAR,
                task_code VARCHAR,
                task_name VARCHAR
            )
            """
        )

    def close(self) -> None:
        self._con.close()

    def save_run(
        self,
        results: list[ModuleResult],
        *,
        schedule: Schedule | None = None,
        store_schedule: bool = False,
        input_name: str | None = None,
    ) -> str:
        """Store metrics and findings. Activities stay out unless store_schedule is true."""
        run_id = uuid4().hex
        seed = next(
            (item.metadata.seed for item in results if item.metadata.seed is not None),
            None,
        )
        current = self._con.execute("SELECT COALESCE(MAX(seq), 0) + 1 FROM runs").fetchone()
        seq = int(current[0]) if current else 1
        self._con.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?)",
            [run_id, seq, input_name, seed],
        )
        for result in results:
            for name, metric in result.metrics.items():
                self._con.execute(
                    "INSERT INTO metrics VALUES (?, ?, ?, ?)",
                    [run_id, name, metric.value, metric.status],
                )
            if "rule_id" not in result.findings.columns:
                continue
            for row in result.findings.itertuples(index=False):
                self._con.execute(
                    "INSERT INTO findings VALUES (?, ?, ?, ?)",
                    [run_id, row.rule_id, row.task_code, row.message_es],
                )
        if store_schedule and schedule is not None:
            for activity in schedule.activities:
                self._con.execute(
                    "INSERT INTO activities VALUES (?, ?, ?)",
                    [run_id, activity.task_code, activity.task_name],
                )
        return run_id

    def trend(self, metric_name: str) -> list[tuple[str, float]]:
        """Return (run_id, value) for one metric, in insertion order."""
        rows = self._con.execute(
            """
            SELECT metrics.run_id, metrics.value
            FROM metrics
            JOIN runs ON runs.run_id = metrics.run_id
            WHERE metrics.metric_name = ? AND metrics.value IS NOT NULL
            ORDER BY runs.seq
            """,
            [metric_name],
        ).fetchall()
        return [(str(run_id), float(value)) for run_id, value in rows]

    def activity_count(self) -> int:
        row = self._con.execute("SELECT COUNT(*) FROM activities").fetchone()
        return int(row[0]) if row else 0
