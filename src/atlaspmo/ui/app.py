"""Streamlit entrypoint. Presentation only; no schedule calculations."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.batch import run_folder
from atlaspmo.bootstrap import bootstrap
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer_bytes
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

if st.button("Ejecutar") and schedule is not None and picked:
    st.session_state["results"] = run_selected(
        [labels[name] for name in picked],
        AnalysisContext(
            schedule=schedule,
            input_name=source_name,
        ),
    )

results = st.session_state.get("results") or []
for result in results:
    st.subheader(result.module_id)
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
        st.plotly_chart(gantt_figure(frame))
    else:
        st.caption("Esta corrida no trae tabla CPM, así que no hay Gantt.")

if results:
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
        data=parquet_zip_bytes(results, project_name=source_name or "atlaspmo", run_id="ui"),
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
        ranked = run_folder(folder)
        st.session_state["batch_rows"] = [(row.name, row.quality_index) for row in ranked]
    else:
        st.session_state["batch_rows"] = []
        st.warning("La carpeta de lote no existe.")
batch_rows = st.session_state.get("batch_rows")
if isinstance(batch_rows, list) and batch_rows:
    st.dataframe(
        [{"archivo": name, "indice": index} for name, index in batch_rows],
        hide_index=True,
    )
