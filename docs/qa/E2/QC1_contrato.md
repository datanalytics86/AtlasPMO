# QC-1 — Contrato E2

Escrito antes del código de E2. Fecha 2026-10-21. Los resultados de esta etapa quedan condicionales a I-3 (E0 RECHAZADA-BLOQUEADA) y a los hallazgos abiertos de E1 (I-11, I-12, I-13, I-14 parcial) si E1 cierra como RECHAZADA-BLOQUEADA.

No se lee `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No hay contraste con P6. UDF no se lee: no hay columna verificada. La lista de códigos es el camino de hito contractual.

| Id | Qué debe quedar | Prueba | Estado al escribir este contrato |
|---|---|---|---|
| B-02 | Candidatos por un grafo, un orden topológico y un recorrido por origen, limitado al rango entre el origen y sus destinos. No se rearma el grafo por vínculo. | `tests/perf/test_redundancy.py` y el filtro en `redundant.py` | No implementado. El filtro actual es O(E·(V+E)). |
| R-020 | Redundancia con confirmación sobre 30k realista (`gen_scale`, `series=False`) bajo 3 min, o la cifra medida si no llega. | `tests/perf/test_redundancy.py` | No medido. |
| B-03 / R-021 | Dos vínculos iguales FS: uno solo queda `redundante_confirmado` y el conjunto da delta cero. | `tests/test_e2_joint.py` | Ya está. No se relaja. |
| B-03 / R-022 | Si el CPM del limpio no coincide, se devuelve el documento original y `removed == 0`. | `tests/test_e2_clean.py` | Ya está. No se relaja. |
| B-04 / R-023 | Hito no contractual no queda protegido. Con código en la lista, sí. Vínculo externo, sí. Extremos abiertos no se confirman. SS+FF queda intacto. | `tests/test_e2_guards.py` | Ya está. No se relaja. |
| R-024 | Invariantes b, c y d con perfil qa. | `tests/property/test_logic.py` | Ya está. G5 no se toca. |

La confirmación conjunta (`_confirm`, `_join`, `_unchanged`, `_events_stay_covered`) no se reemplaza. El cambio de B-02 es solo el filtro de candidatos. Un ciclo en el grafo completo no produce candidatos: el cálculo es sobre un DAG. Eso es más conservador que recalcular el orden sin el arco.

QC-2 de los casos nuevos de redundancia no está en este contrato. Los esperados de los tests ya verdes salen del CPM del propio caso, no de un segundo método en `tests/oracle/`. Queda anotado. No se inventa un oráculo de P6.