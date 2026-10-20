"""Streamlit entrypoint. Presentation only; no schedule calculations."""

from __future__ import annotations

import streamlit as st

from atlaspmo.bootstrap import bootstrap
from atlaspmo.registry import registered_modules

bootstrap()

st.set_page_config(page_title="AtlasPMO", layout="wide")
st.title("AtlasPMO")
st.caption("Análisis local de cronogramas. Nada sale de este equipo.")

modules = registered_modules()
if not modules:
    st.info(
        "El selector queda vacío hasta que haya módulos registrados.",
        title="Sin módulos",
    )
else:
    st.multiselect(
        "Módulos a ejecutar",
        [module.name_es for module in modules],
    )
