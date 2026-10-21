RECHAZADO

Ciclo 1 de E3. Este es el rechazo 1 de 3. HEAD `51d281f9e4aca9548be8a2e0bbb8eb736f26c3d5` (`test(qa): gate E3 ciclo 1, salida 1 (B-12)`). El gate no está en verde: `docs/qa/E3/gate.json` trae exit_code 1, test_count 200 y coverage_percent 89.4. Fallan G4 y G13. Hay importantes abiertos. La etapa no se cierra.

APROBADO no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser APROBADO. Esta revisión no marca la etapa como RECHAZADA-BLOQUEADA: eso lo hace el orquestador solo después del tercer RECHAZADO. El rechazo devuelve a QC-3 con la lista de hallazgos. No se bajan los umbrales de 8.1 ni los de G13.

La excepción de línea base de la sección 10.2 vale solo para E0. En E3, G4 y G13 en fail impiden el cierre. No se marcan pass.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 es `pytest -m perf` sobre `tests/perf`: 3 passed in 3.57 s. Ese verde no prueba la definición de CPLI. G10 dice que 42 requisitos de E3 citan un archivo de test que existe; el verde de la suite lo mide G3. No comprueba doble firma.

G4 incumple 8.1. Las seis cifras de calendarios, motor y lógica son las mismas que el gate de E2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.4. El modelo está en 100.0 / 100.0 y no está en el texto de fail. El resto, líneas 89.7, está sobre el 80 % y no compensa. No se marca pass. El detalle está en I-19.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E3/sabotaje.md`. No se inventa un kill score y no se copia el de E1. No medido no es pass. El detalle está en I-20.

`docs/qa/E3/perf.md`, en este equipo el 2026-10-21, red de `gen_scale` de 30 000 actividades con `series=False`, sin XER real: `evaluate` de calidad, sin baseline, 0.261 s. Está bajo 10 s. No es un crítico de rendimiento. El mismo documento dice que CPLI en esa red queda `no_evaluable` y que el tiempo no incluye el CPM ni prueba la definición de CPLI. Los otros criterios de la sección 11 no se miden ahí. La confirmación de redundancia de 30 000 sigue sin medirse (I-17).

Doble firma: no está, salvo el caso CPLI de ADR-017 (24 h + 16 h, `tests/oracle/span.py` y `tests/test_e3_cpli.py`). No hay caso SS solapado ni feriado. BEI (`tests/test_e3_bei.py`) cuenta una completada antes de tiempo y no es doble firma. `tests/test_e3_dcma.py`, `test_e3_gao.py`, `test_e3_extra.py` y `test_e3_profiles.py` afirman lo que el código hace en redes a mano. GAO 6 y GAO 8 quedan en estado «manual». Eso no es una revisión humana hecha. QC-2 sigue incompleto fuera de ese caso de CPLI. El criterio de E3 en 10.2 pide todas las métricas contra esperados con doble firma. No se cumple. I-21. La mitad de WBS de R-326 tampoco está implementada. I-24.

Modo A: las bandas son configurables y el corte por defecto en `PathsConfig` es (0, 10, 20, 44), con test en `tests/test_e3_paths.py`. El mismo test afirma que el modo A no marca la cadena driving. En `src/atlaspmo/analysis/paths/mode_a.py` la aproximación dice: «Los vínculos driving no se marcan en modo A: no hay un campo citado de holgura libre del vínculo.» Continuidad de la ruta y multiple float paths no están implementados. `docs/qa/E3/QC1_contrato.md` decía que las bandas seguían fijas: eso ya no es cierto y no cierra M2 ni el B-12 del megaprompt. I-22 e I-23.

No hay críticos. Importantes abiertos de este ciclo: I-19 (G4), I-20 (G13 no medido), I-21 (doble firma), I-22 (cadena driving), I-23 (continuidad y multiple float paths) e I-24 (WBS requerida). Heredados que siguen abiertos y no se cierran: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17 e I-18 parcial. E0, E1 y E2 siguen RECHAZADA-BLOQUEADA. Los resultados de E3 quedan condicionales a I-3 y a esos bloqueos.

No se leyeron datos reales. No se bajaron umbrales. No se reejecutó pytest, el gate ni la mutación. El detalle está en `docs/qa/E3/hallazgos.md`.
