"""Screen for a second XER, module requirements, the viewer and the library."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pytest
from streamlit.runtime.media_file_manager import MediaFileManager
from streamlit.testing.v1 import AppTest

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.paths.mode_b import PathsBConfig, PathsModeB
from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.profiles import load_profile
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.synthetic import write_xer
from atlaspmo.io.xer import read_xer, read_xer_bytes
from atlaspmo.model.schedule import Schedule
from test_cpm import _link, _load, _task

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "src" / "atlaspmo" / "ui" / "app.py"


def _app() -> AppTest:
    # The first script run imports the UI. Three seconds is tight on a cold cache.
    return AppTest.from_file(APP, default_timeout=30)


def _labeled(widgets, label: str):
    found = [item for item in widgets if item.label == label]
    assert len(found) == 1, label
    return found[0]


def _captions(app: AppTest) -> str:
    return " ".join(item.value for item in app.caption)


def _bei_value(app: AppTest) -> float:
    found = None
    for item in app.dataframe:
        frame = item.value
        if "métrica" not in frame.columns:
            continue
        rows = frame.loc[frame["métrica"] == "bei", "valor"]
        if not rows.empty:
            found = rows.iloc[0]
    assert found is not None
    return float(found)


def _within(schedule: Schedule, needle: str, levels: int) -> set[str]:
    """Predecessors and successors within N links. The UI is not called."""
    code_of = {
        activity.task_id: activity.task_code
        for activity in schedule.activities
        if activity.task_id and activity.task_code
    }
    seeds = {task_id for task_id, code in code_of.items() if needle in code}
    preds: dict[str, set[str]] = {}
    succs: dict[str, set[str]] = {}
    for link in schedule.relationships:
        if link.task_id and link.pred_task_id:
            preds.setdefault(link.task_id, set()).add(link.pred_task_id)
            succs.setdefault(link.pred_task_id, set()).add(link.task_id)
    seen = set(seeds)
    wave = set(seeds)
    for _step in range(levels):
        nxt: set[str] = set()
        for node in wave:
            nxt |= preds.get(node, set())
            nxt |= succs.get(node, set())
        nxt -= seen
        seen |= nxt
        wave = nxt
    return {code_of[task_id] for task_id in seen if task_id in code_of}


def _shown_codes(app: AppTest) -> set[str]:
    tables: list[set[str]] = []
    for item in app.dataframe:
        frame = item.value
        columns = set(frame.columns)
        if {"task_code", "early_start", "early_finish"} <= columns:
            tables.append(set(frame["task_code"].astype(str)))
    assert len(tables) == 1
    charts = app.get("plotly_chart")
    assert len(charts) == 1
    spec = json.loads(charts[0].spec)
    chart_codes = {str(trace["y"][0]) for trace in spec["data"]}
    assert chart_codes == tables[0]
    return tables[0]


def _color_groups(app: AppTest) -> list[set[str]]:
    spec = json.loads(app.get("plotly_chart")[0].spec)
    groups: dict[str, set[str]] = {}
    for trace in spec["data"]:
        marker = trace.get("marker") or {}
        color = marker.get("color")
        if isinstance(color, list):
            color = color[0]
        groups.setdefault(str(color), set()).add(str(trace["y"][0]))
    return list(groups.values())


def _library_cells(path: Path) -> list[object]:
    connection = duckdb.connect(str(path), read_only=True)
    try:
        names = [row[0] for row in connection.execute("SHOW TABLES").fetchall()]
        cells: list[object] = []
        for name in names:
            quoted = '"' + str(name).replace('"', '""') + '"'
            for row in connection.execute(f"SELECT * FROM {quoted}").fetchall():
                cells.extend(row)
        return cells
    finally:
        connection.close()


def _bei_bytes(folder: Path) -> tuple[bytes, bytes]:
    actual = folder / "actual.xer"
    baseline = folder / "base.xer"
    write_xer(
        actual,
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "last_recalc_date"],
                "rows": [["1", "2026-02-01 00:00"]],
            },
            {
                "name": "TASK",
                "fields": [
                    "task_id",
                    "proj_id",
                    "task_code",
                    "task_type",
                    "status_code",
                    "act_end_date",
                ],
                "rows": [
                    ["1", "1", "LATE", "TT_Task", "TK_Complete", "2026-01-12 08:00"],
                    ["2", "1", "OPEN", "TT_Task", "TK_NotStart", ""],
                    ["3", "1", "EARLY", "TT_Task", "TK_Complete", "2026-01-05 16:00"],
                ],
            },
        ],
    )
    write_xer(
        baseline,
        "ERMHDR",
        [
            {
                "name": "PROJECT",
                "fields": ["proj_id", "last_recalc_date"],
                "rows": [["1", "2026-02-01 00:00"]],
            },
            {
                "name": "TASK",
                "fields": [
                    "task_id",
                    "proj_id",
                    "task_code",
                    "task_type",
                    "status_code",
                    "target_end_date",
                ],
                "rows": [
                    ["1", "1", "LATE", "TT_Task", "TK_NotStart", "2026-01-10 08:00"],
                    ["2", "1", "OPEN", "TT_Task", "TK_NotStart", "2026-01-20 08:00"],
                    ["3", "1", "EARLY", "TT_Task", "TK_NotStart", "2026-03-01 08:00"],
                ],
            },
        ],
    )
    return actual.read_bytes(), baseline.read_bytes()


def test_baseline_requirements_progress_and_full_report(tmp_path: Path) -> None:
    actual_bytes, baseline_bytes = _bei_bytes(tmp_path)
    actual = schedule_from_xer(read_xer_bytes(actual_bytes))
    baseline = schedule_from_xer(read_xer_bytes(baseline_bytes))
    app = _app()
    app.run()
    assert "baseline no se asocia" not in _captions(app)
    captions = [item.value for item in app.caption]
    assert any(
        item.startswith("EVM y Earned Schedule:") and "requiere recursos" in item
        for item in captions
    )
    assert any(
        item.startswith("Comparación de updates:") and "requiere dos versiones" in item
        for item in captions
    )
    assert not any("Calidad (DCMA y GAO)" in item and "requiere" in item for item in captions)
    assert [item.label for item in app.file_uploader][:1] == ["Cronograma XER"]
    app.selectbox[0].set_value("dcma_estricto").run()
    app.file_uploader[0].upload("actual.xer", actual_bytes).run()
    app.file_uploader[1].upload("base.xer", baseline_bytes).run()
    chosen = ["Calidad (DCMA y GAO)", "EVM y Earned Schedule"]
    app.multiselect[0].set_value(chosen).run()
    app.button[0].click().run()
    assert app.exception == []
    profile, _note = load_profile(str(app.selectbox[0].value))
    expected = evaluate(actual, profile, baseline)[0]["bei"].value
    assert expected is not None
    assert _bei_value(app) == pytest.approx(expected)
    # AppTest stores st.progress(1.0) as 100.
    assert any(bar.value == 100 for bar in app.progress)
    labels = {item.label for item in app.tabs}
    assert "Resultados" in labels
    assert set(chosen) <= labels
    buttons = [item.label for item in app.button]
    assert buttons[:3] == ["Ejecutar", "Correr lote", "Guardar corrida"]
    informe = _labeled(app.button, "Informe completo")
    captured: dict[str, bytes] = {}
    original = MediaFileManager.add

    def spy(
        self, path_or_data, mimetype, coordinates, file_name=None, is_for_static_download=False
    ):
        if isinstance(path_or_data, bytes) and file_name in {"informe.xlsx", "informe.pdf"}:
            captured[file_name] = path_or_data
        return original(
            self,
            path_or_data,
            mimetype,
            coordinates,
            file_name=file_name,
            is_for_static_download=is_for_static_download,
        )

    MediaFileManager.add = spy  # type: ignore[method-assign]
    try:
        informe.click().run()
    finally:
        MediaFileManager.add = original  # type: ignore[method-assign]
    assert app.exception == []
    names = {item.label for item in app.download_button}
    assert {
        "Exportar Excel",
        "Exportar PDF",
        "Exportar Parquet",
        "Exportar manifiesto",
    } <= names
    assert "Informe Excel" in names
    assert "Informe PDF" in names
    assert captured["informe.xlsx"].startswith(b"PK")
    assert captured["informe.pdf"].startswith(b"%PDF")


def test_filter_walks_neighbors_and_driving_is_mode_b(tmp_path: Path) -> None:
    chain = _load(
        tmp_path / "chain",
        [_task("1", "A", "8"), _task("2", "B", "8"), _task("3", "C", "8")],
        [_link("1", "1", "2"), _link("2", "2", "3")],
    )
    assert _within(chain, "B", 0) == {"B"}
    assert _within(chain, "B", 1) == {"A", "B", "C"}
    app = _app()
    app.run()
    raw = (tmp_path / "chain" / "case.xer").read_bytes()
    app.file_uploader[0].upload("chain.xer", raw).run()
    app.multiselect[0].set_value(["Ruta crítica (modo B)"]).run()
    app.button[0].click().run()
    assert app.exception == []
    _labeled(app.text_input, "Filtrar visor por código").set_value("B")
    _labeled(app.number_input, "Niveles").set_value(0)
    app.run()
    assert app.exception == []
    assert _shown_codes(app) == _within(chain, "B", 0)
    _labeled(app.text_input, "Filtrar visor por código").set_value("B")
    _labeled(app.number_input, "Niveles").set_value(1)
    app.run()
    assert app.exception == []
    assert _shown_codes(app) == _within(chain, "B", 1)

    join = _load(
        tmp_path / "join",
        [_task("1", "SHORT", "8"), _task("2", "LONG", "16"), _task("3", "JOIN", "8")],
        [_link("1", "1", "3"), _link("2", "2", "3")],
    )
    driving = set(
        PathsModeB()
        .run(AnalysisContext(schedule=join), PathsBConfig())
        .tables["driving_chain"]["task_code"]
    )
    codes = {activity.task_code for activity in join.activities}
    assert driving
    assert driving < codes
    viewer = _app()
    viewer.run()
    viewer.file_uploader[0].upload("join.xer", (tmp_path / "join" / "case.xer").read_bytes()).run()
    viewer.multiselect[0].set_value(["Ruta crítica (modo B)"]).run()
    viewer.button[0].click().run()
    assert viewer.exception == []
    assert "No recalcula fechas" in _captions(viewer)
    assert driving in _color_groups(viewer)


def test_batch_orders_by_evaluate_and_library_skips_xer(tmp_path: Path) -> None:
    folder = tmp_path / "lote"
    folder.mkdir()
    _load(tmp_path / "open", [_task("1", "SOLO", "8")], [])
    _load(
        tmp_path / "cycle",
        [_task("1", "A", "8"), _task("2", "B", "8")],
        [_link("1", "1", "2"), _link("2", "2", "1")],
    )
    (folder / "a_open.xer").write_bytes((tmp_path / "open" / "case.xer").read_bytes())
    (folder / "z_cycle.xer").write_bytes((tmp_path / "cycle" / "case.xer").read_bytes())
    profile, _note = load_profile("dcma_estricto")
    indexes: dict[str, float] = {}
    for path in folder.glob("*.xer"):
        schedule = schedule_from_xer(read_xer(path))
        value = evaluate(schedule, profile, None)[0]["quality_index"].value
        assert value is not None
        indexes[path.name] = value
    expected = sorted(indexes, key=lambda name: (-indexes[name], name))
    assert expected == ["z_cycle.xer", "a_open.xer"]
    app = _app()
    app.run()
    app.text_input[0].set_value(str(folder)).run()
    app.button[1].click().run()
    assert app.exception == []
    frame = next(item.value for item in app.dataframe if "archivo" in item.value.columns)
    assert list(frame["archivo"]) == expected
    for name, shown in zip(frame["archivo"], frame["indice"], strict=True):
        assert shown == pytest.approx(indexes[name])

    xer_bytes = (folder / "a_open.xer").read_bytes()
    xer_text = xer_bytes.decode("cp1252")
    library = _app()
    library.run()
    library.file_uploader[0].upload("a_open.xer", xer_bytes).run()
    library.multiselect[0].set_value(["Calidad (DCMA y GAO)"]).run()
    library.button[0].click().run()
    off = tmp_path / "off.duckdb"
    library.text_input[1].set_value(str(off)).run()
    assert _labeled(library.checkbox, "Guardar el cronograma").value is False
    library.button[2].click().run()
    assert library.exception == []
    assert "Puntos de quality_index: 1" in _captions(library)
    off_cells = _library_cells(off)
    assert off_cells
    assert not any("ERMHDR" in str(cell) for cell in off_cells)

    kept = _app()
    kept.run()
    kept.file_uploader[0].upload("a_open.xer", xer_bytes).run()
    kept.multiselect[0].set_value(["Calidad (DCMA y GAO)"]).run()
    kept.button[0].click().run()
    on = tmp_path / "on.duckdb"
    _labeled(kept.checkbox, "Guardar el cronograma").set_value(True)
    kept.text_input[1].set_value(str(on))
    kept.button[2].click().run()
    assert kept.exception == []
    on_cells = _library_cells(on)
    assert any(cell == xer_text for cell in on_cells)
    assert any("ERMHDR" in str(cell) for cell in on_cells)
