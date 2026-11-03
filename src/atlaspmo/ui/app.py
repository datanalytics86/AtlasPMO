"""Streamlit entrypoint. Presentation only; no schedule calculations."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from pydantic import BaseModel

from atlaspmo.analysis.contract import AnalysisContext, Metric, Requirement
from atlaspmo.analysis.quality.check import evaluate
from atlaspmo.analysis.quality.module import QualityConfig
from atlaspmo.analysis.quality.profiles import load_profile
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

_REQUIREMENT_ES = {
    Requirement.RESOURCES: "requiere recursos",
    Requirement.TWO_VERSIONS: "requiere dos versiones",
    Requirement.BASELINE: "requiere baseline",
    Requirement.CPM_ENGINE: "requiere el motor CPM",
}


def _codes_within(schedule: Schedule, needle: str, levels: int) -> set[str]:
    """Activity codes within N predecessor and successor links of the needle."""
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


def _viewer_frame(
    frame: pd.DataFrame, schedule: Schedule | None, needle: str, levels: int
) -> pd.DataFrame:
    """Keep rows whose code contains the text, plus N links around them."""
    text = needle.strip()
    if not text:
        return frame
    allowed = _codes_within(schedule, text, levels) if schedule is not None else set()
    return frame.loc[frame["task_code"].astype(str).isin(allowed)]


def _marked(chain: pd.DataFrame | None) -> set[str]:
    """Task codes already listed on the module driving chain."""
    if chain is None or chain.empty or "task_code" not in chain.columns:
        return set()
    return {str(code) for code in chain["task_code"] if code is not None and str(code) != "nan"}


st.set_page_config(page_title="AtlasPMO", layout="wide")
st.title("AtlasPMO")
st.caption("Análisis local de cronogramas. Nada sale de este equipo.")
st.caption("El segundo XER es el baseline.")

uploaded = st.file_uploader("Cronograma XER", type=["xer"])
baseline_file = st.file_uploader("XER baseline", type=["xer"])
if uploaded is not None:
    raw = uploaded.getvalue()
    parsed = schedule_from_xer(read_xer_bytes(raw))
    st.session_state["schedule"] = parsed
    st.session_state["source_name"] = uploaded.name
    st.session_state["source_bytes"] = raw
if baseline_file is not None:
    st.session_state["baseline"] = schedule_from_xer(read_xer_bytes(baseline_file.getvalue()))

held = st.session_state.get("schedule")
schedule = held if isinstance(held, Schedule) else None
held_baseline = st.session_state.get("baseline")
baseline = held_baseline if isinstance(held_baseline, Schedule) else None
raw_name = st.session_state.get("source_name")
source_name = raw_name if isinstance(raw_name, str) else None
raw_bytes = st.session_state.get("source_bytes")
source_bytes = raw_bytes if isinstance(raw_bytes, bytes) else None
if schedule is not None:
    st.write(f"{len(schedule.activities)} actividades")

modules = registered_modules()
labels = {module.name_es: module.id for module in modules}
names = {module.id: module.name_es for module in modules}
picked: list[str] = []
if not modules:
    st.info(
        "El selector queda vacío hasta que haya módulos registrados.",
        title="Sin módulos",
    )
else:
    picked = st.multiselect("Módulos a ejecutar", list(labels))
for module in modules:
    if not module.requires:
        continue
    phrases = [_REQUIREMENT_ES[item] for item in sorted(module.requires)]
    st.caption(f"{module.name_es}: {', '.join(phrases)}")

profile_files = sorted((ROOT / "profiles").glob("*.yaml"))
profile_names = [path.stem for path in profile_files] or ["dcma_estricto"]
profile_name = st.selectbox("Perfil de calidad", profile_names)

baseline_bei: Metric | None = None
if schedule is not None and baseline is not None:
    chosen_profile, _profile_note = load_profile(str(profile_name))
    baseline_bei = evaluate(schedule, chosen_profile, baseline)[0]["bei"]

if st.button("Ejecutar") and schedule is not None and picked:
    chosen = [labels[name] for name in picked]
    configs: dict[str, BaseModel] = {}
    if "quality" in chosen:
        configs["quality"] = QualityConfig(profile=profile_name)
    st.session_state["results"] = run_selected(
        chosen,
        AnalysisContext(
            schedule=schedule,
            other=baseline,
            input_name=source_name,
        ),
        configs,
    )
    st.session_state["done"] = True
if st.session_state.get("done"):
    st.progress(1.0)
    st.caption("No hay avance parcial. La barra se llena al terminar.")

results = st.session_state.get("results") or []
if results:
    tab_names = ["Resultados", "Exportaciones"]
    tab_names.extend(names.get(result.module_id, result.module_id) for result in results)
    opened = st.tabs(tab_names)
    with opened[0]:
        for result in results:
            st.subheader(result.module_id)
            if result.metadata.profile:
                st.caption(f"Perfil registrado: {result.metadata.profile}")
            for note in result.approximations:
                st.caption(note)
            shown_metrics = result.metrics
            if result.module_id == "quality" and baseline_bei is not None:
                shown_metrics = dict(result.metrics)
                shown_metrics["bei"] = baseline_bei
            rows = [
                {"métrica": key, "valor": metric.value, "estado": metric.status}
                for key, metric in shown_metrics.items()
            ]
            if rows:
                st.dataframe(rows, hide_index=True)
            frame = result.tables.get("cpm")
            has_cpm = (
                frame is not None
                and not frame.empty
                and {"task_code", "early_start", "early_finish"} <= set(frame.columns)
            )
            chain = result.tables.get("driving_chain")
            if has_cpm:
                st.caption("El visor usa la tabla CPM del módulo. No recalcula fechas.")
                code_filter = st.text_input(
                    "Filtrar visor por código",
                    key=f"gantt_{result.module_id}",
                )
                levels = st.number_input(
                    "Niveles",
                    min_value=0,
                    max_value=99,
                    value=0,
                    step=1,
                    key=f"niveles_{result.module_id}",
                )
                shown = _viewer_frame(frame, schedule, code_filter, int(levels))
                st.plotly_chart(gantt_figure(shown, _marked(chain)))
                st.dataframe(shown, hide_index=True)
            else:
                st.caption("Esta corrida no trae tabla CPM, así que no hay Gantt.")
            if chain is not None and not chain.empty:
                st.caption("La cadena driving no es un float path de P6.")
                st.dataframe(chain, hide_index=True)
    with opened[1]:
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
    for tab, result in zip(opened[2:], results, strict=True):
        with tab:
            st.caption(names.get(result.module_id, result.module_id))

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

st.caption(
    "La biblioteca guarda métricas. El cronograma se guarda solo si la opción está prendida."
)
library_text = st.text_input("Biblioteca DuckDB")
keep_schedule = st.checkbox("Guardar el cronograma", value=False)
if st.button("Guardar corrida") and results and library_text:
    library = Library(Path(library_text))
    try:
        schedule_text = None
        if keep_schedule and isinstance(source_bytes, bytes):
            schedule_text = source_bytes.decode("cp1252", errors="surrogateescape")
        library.save_run(
            results,
            schedule=schedule if keep_schedule else None,
            store_schedule=keep_schedule,
            input_name=source_name,
            schedule_text=schedule_text,
        )
        st.session_state["library_points"] = len(library.trend("quality_index"))
    finally:
        library.close()
stored_points = st.session_state.get("library_points")
if isinstance(stored_points, int):
    st.caption(f"Puntos de quality_index: {stored_points}")

if st.button("Informe completo") and results:
    st.session_state["full_report"] = True
if st.session_state.get("full_report") and results:
    st.download_button(
        "Informe Excel",
        data=excel_bytes(results),
        file_name="informe.xlsx",
    )
    st.download_button(
        "Informe PDF",
        data=pdf_bytes(results),
        file_name="informe.pdf",
    )
