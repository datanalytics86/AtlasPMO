# QC-1 — Contrato E5

Escrito antes del código nuevo de E5. Fecha 2026-10-21. Los resultados quedan condicionales a I-3 y a E0, E1, E2, E3 y E4 RECHAZADA-BLOQUEADA.

No se lee `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

| Id | Qué debe quedar | Prueba | Al escribir este contrato |
|---|---|---|---|
| B-01 / R-050 | AppTest: cargar un sintético, ejecutar un módulo y exportar. | `tests/test_e5_ui.py` | La UI es un multiselect de 25 líneas. No carga, no ejecuta y no exporta. |
| R-051 | Localhost y sin estadísticas de uso. | `tests/test_e5_ui.py` | `.streamlit/config.toml` ya dice `address = "localhost"` y `gatherUsageStats = false`. El test tiene que leer ese archivo. No abre un socket. |
| R-102 | La entrada no se reescribe y hay manifiesto. | `tests/test_e5_manifest.py` | `write_manifest` existe. Falta la prueba citada. |
| R-104 | Las aproximaciones se muestran. | `tests/test_e5_ui.py` | No se muestran: la pantalla no ejecuta módulos. |
| R-120 | El usuario asocia el baseline. | `tests/test_e5_ui.py` | No implementado. No se va a marcar en verde. |

El visor Gantt, el lote desde la pantalla, PDF y Parquet en la UI siguen fuera de este contrato hasta que haya una prueba que los ejercite. No se inventa un e2e que no corre.
