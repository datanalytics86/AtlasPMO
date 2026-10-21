# QC-1 — Contrato E4

Escrito antes del código nuevo de E4. Fecha 2026-10-21. Los resultados quedan condicionales a I-3 y a E0, E1, E2 y E3 RECHAZADA-BLOQUEADA.

No se lee `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No hay contraste con P6.

| Id | Qué debe quedar | Prueba | Al escribir este contrato |
|---|---|---|---|
| B-07 / R-040 / R-303 | Monte Carlo de 30 000 por 1 000 iteraciones bajo 5 minutos, o la cifra medida. | `tests/perf/test_montecarlo.py` | No medido. El motor sigue recalculando el CPM completo. numba no está cargado. |
| R-041 / R-168 | Tornado solo sobre el cono de sucesoras, con conteo de recalculadas. | `tests/test_e4_tornado.py` | No implementado. Hoy hay un CPM completo por actividad. |
| R-042 | Invariante e: varianza cero igual al CPM. | `tests/property/test_invariant_e.py` | El archivo existe. La trazabilidad cita `tests/property/test_risk.py`, que no existe. Hay que corregir la cita, no inventar el módulo. |
| B-13 / R-043 / R-169 | Curvas por periodo, histogramas y `fact_timephased` poblado. | `tests/test_e4_spreads.py` | `fact_timephased` se crea vacío. La curva S tiene un solo punto en la fecha de corte y el PV es lineal. |
| R-103 | Metadatos con versión, semilla y parámetros. | `tests/test_e4_metadata.py` | El módulo de riesgo ya guarda la semilla. Falta el archivo de prueba citado. |
| R-343 / R-344 | P50, P80, P90 y convergencia contra el término determinístico. | `tests/test_e4_outputs.py` | Hay casos en `tests/test_risk.py`. Falta el archivo citado. No es doble firma. |

QC-2 sigue incompleto. No se inventa un oráculo de P6 ni un tiempo de 30 000 por 1 000.
