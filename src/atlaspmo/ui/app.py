"""Streamlit entrypoint. Presentation only; no schedule calculations."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from pydantic import BaseModel

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.analysis.quality.module import QualityConfig
from atlaspmo.batch import BatchRow, ranking_bytes, run_folder
from atlaspmo.bootstrap import bootstrap
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer_bytes
from atlaspmo.library.store import Library
from atlaspmo.model.schedule import Schedule
from atlaspmo.registry import registered_modules
from atlaspmo.reports.export import excel_bytes, manifest_bytes, pdf_bytes
from atlaspmo.reports.gantt import gantt_figure
from atlaspmo.reports.parquet_star import parquet_zip_bytes
from atlaspmo.runner import run_selected

bootstrap()
ROOT = Path(__file__).resolve().parents[3]

st.set_page_config(page_title="AtlasPMO", layout="wide")
st.title("AtlasPMO")
st.caption("Análisis local de cronogramas. Nada sale de este equipo.")
st.caption("El baseline no se asocia en esta pantalla.")

uploaded = st.file_uploader("Cronograma XER", type=["xer"])
if uploaded is not None:
    raw = uploaded.getvalue()
    parsed = schedule_from_xer(read_xer_bytes(raw))
    st.session_state["schedule"] = parsed
    st.session_state["source_name"] = uploaded.name
    st.session_state["source_bytes"] = raw

held = st.session_state.get("schedule")
schedule = held if isinstance(held, Schedule) else None
raw_name = st.session_state.get("source_name")
source_name = raw_name if isinstance(raw_name, str) else None
raw_bytes = st.session_state.get("source_bytes")
source_bytes = raw_bytes if isinstance(raw_bytes, bytes) else None
if schedule is not None:
    st.write(f"{len(schedule.activities)} actividades")

modules = registered_modules()
labels = {module.name_es: module.id for module in modules}
picked: list[str] = []
if not modules:
    st.info(
        "El selector queda vacío hasta que haya módulos registrados.",
        title="Sin módulos",
    )
else:
    picked = st.multiselect("Módulos a ejecutar", list(labels))

profile_files = sorted((ROOT / "profiles").glob("*.yaml"))
profile_names = [path.stem for path in profile_files] or ["dcma_estricto"]
profile_name = st.selectbox("Perfil de calidad", profile_names)

if st.button("Ejecutar") and schedule is not None and picked:
    st.progress(0.0)
    chosen = [labels[name] for name in picked]
    configs: dict[str, BaseModel] = {}
    if "quality" in chosen:
        configs["quality"] = QualityConfig(profile=profile_name)
    st.session_state["results"] = run_selected(
        chosen,
        AnalysisContext(
            schedule=schedule,
            input_name=source_name,
        ),
        configs,
    )
    st.progress(1.0)
    st.caption("No hay avance parcial. La barra se llena al terminar.")

results = st.session_state.get("results") or []
if results:
    tab_results, tab_exports = st.tabs(["Resultados", "Exportaciones"])
    with tab_results:
        for result in results:
            st.subheader(result.module_id)
            if result.metadata.profile:
                st.caption(f"Perfil registrado: {result.metadata.profile}")
            for note in result.approximations:
                st.caption(note)
            rows = [
                {"métrica": key, "valor": metric.value, "estado": metric.status}
                for key, metric in result.metrics.items()
            ]
            if rows:
                st.dataframe(rows, hide_index=True)
            frame = result.tables.get("cpm")
            has_cpm = (
                frame is not None
                and not frame.empty
                and {"task_code", "early_start", "early_finish"} <= set(frame.columns)
            )
            if has_cpm:
                st.caption("El visor usa la tabla CPM del módulo. No recalcula fechas.")
                code_filter = st.text_input(
                    "Filtrar visor por código",
                    key=f"gantt_{result.module_id}",
                )
                shown = frame
                if code_filter:
                    mask = frame["task_code"].astype(str) == code_filter
                    shown = frame.loc[mask]
                st.plotly_chart(gantt_figure(shown))
                st.dataframe(shown, hide_index=True)
            else:
                st.caption("Esta corrida no trae tabla CPM, así que no hay Gantt.")
            chain = result.tables.get("driving_chain")
            if chain is not None and not chain.empty:
                st.caption("La cadena driving no es un float path de P6.")
                st.dataframe(chain, hide_index=True)
    with tab_exports:
        st.download_button(
            "Exportar Excel",
            data=excel_bytes(results),
            file_name="atlaspmo.xlsx",
        )
        st.download_button(
            "Exportar PDF",
            data=pdf_bytes(results),
            file_name="atlaspmo.pdf",
        )
        st.download_button(
            "Exportar Parquet",
            data=parquet_zip_bytes(
                results,
                project_name=source_name or "atlaspmo",
                run_id="ui",
            ),
            file_name="atlaspmo-star.zip",
        )
        st.download_button(
            "Exportar manifiesto",
            data=manifest_bytes(results, source_name, source_bytes, ROOT),
            file_name="run_manifest.json",
        )

st.caption("El lote corre cada XER de la carpeta. No asocia un baseline.")
folder_text = st.text_input("Carpeta de lote")
if st.button("Correr lote") and folder_text:
    folder = Path(folder_text)
    if folder.is_dir():
        chosen_ids = [labels[name] for name in picked] if picked else None
        ranked = run_folder(folder, chosen_ids)
        st.session_state["batch_rows"] = [(row.name, row.quality_index) for row in ranked]
    else:
        st.session_state["batch_rows"] = []
        st.warning("La carpeta de lote no existe.")
batch_rows = st.session_state.get("batch_rows")
restored: list[BatchRow] = []
if isinstance(batch_rows, list):
    for item in batch_rows:
        if not isinstance(item, tuple) or len(item) != 2 or not isinstance(item[0], str):
            continue
        index = item[1]
        value = index if isinstance(index, float) or index is None else None
        restored.append(BatchRow(item[0], value))
if restored:
    st.dataframe(
        [{"archivo": row.name, "indice": row.quality_index} for row in restored],
        hide_index=True,
    )
    st.download_button(
        "Exportar ranking",
        data=ranking_bytes(restored),
        file_name="ranking.xlsx",
    )

st.caption("La biblioteca guarda métricas. No guarda el cronograma.")
library_text = st.text_input("Biblioteca DuckDB")
if st.button("Guardar corrida") and results and library_text:
    library = Library(Path(library_text))
    try:
        library.save_run(results, input_name=source_name, store_schedule=False)
        st.session_state["library_points"] = len(library.trend("quality_index"))
    finally:
        library.close()
stored_points = st.session_state.get("library_points")
if isinstance(stored_points, int):
    st.caption(f"Puntos de quality_index: {stored_points}")
