"""Streamlit entrypoint. Presentation only; no schedule calculations."""

from __future__ import annotations

import streamlit as st

from atlaspmo.analysis.contract import AnalysisContext
from atlaspmo.bootstrap import bootstrap
from atlaspmo.io.load import schedule_from_xer
from atlaspmo.io.xer import read_xer_bytes
from atlaspmo.model.schedule import Schedule
from atlaspmo.registry import registered_modules
from atlaspmo.reports.export import excel_bytes
from atlaspmo.runner import run_selected

bootstrap()

st.set_page_config(page_title="AtlasPMO", layout="wide")
st.title("AtlasPMO")
st.caption("Análisis local de cronogramas. Nada sale de este equipo.")
st.caption("El baseline no se asocia en esta pantalla.")

uploaded = st.file_uploader("Cronograma XER", type=["xer"])
if uploaded is not None:
    parsed = schedule_from_xer(read_xer_bytes(uploaded.getvalue()))
    st.session_state["schedule"] = parsed
    st.session_state["source_name"] = uploaded.name

held = st.session_state.get("schedule")
schedule = held if isinstance(held, Schedule) else None
raw_name = st.session_state.get("source_name")
source_name = raw_name if isinstance(raw_name, str) else None
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

if results:
    st.download_button(
        "Exportar Excel",
        data=excel_bytes(results),
        file_name="atlaspmo.xlsx",
    )
