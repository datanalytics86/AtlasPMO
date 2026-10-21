RECHAZADO

Ciclo 2 de E3. Este es el rechazo 2 de 3. La etapa no queda bloqueada: no es el tercer rechazo. HEAD `436e1fcc2d2d834feb2fd060e25e152d5cbbf5f8` (`test(qa): gate E3 ciclo 2, salida 1 (B-12)`). El gate no está en verde: `docs/qa/E3/gate.json` trae exit_code 1, test_count 201 y coverage_percent 89.4. Fallan G4 y G13. Hay importantes abiertos. La etapa no se cierra.

APROBADO no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser APROBADO. El rechazo devuelve a QC-3 con la lista de hallazgos. No se bajan los umbrales de 8.1 ni los de G13.

La excepción de línea base de la sección 10.2 vale solo para E0. En E3, G4 y G13 en fail impiden el cierre. No se marcan pass.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 registra 3 passed in 3.80 s. Ese verde no prueba la definición de CPLI. G10 dice que 42 requisitos de E3 citan un archivo de test que existe; el verde de la suite lo mide G3. No comprueba doble firma.

G4 incumple 8.1. Las seis cifras son las mismas del ciclo 1 y del gate de E2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. El umbral de 8.1 es 90 % de líneas y 85 % de ramas. cobertura_total 89.4. El modelo está en 100.0 / 100.0 y no está en el texto de fail. El resto, líneas 89.7, está sobre el 80 % y no compensa. No se marca pass. El detalle está en I-19.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E3/sabotaje.md`. No se inventa un kill score y no se copia el de E1. No medido no es pass. El detalle está en I-20.

`docs/qa/E3/perf.md`, en este equipo el 2026-10-21, red de `gen_scale` de 30 000 actividades con `series=False`, sin XER real: `evaluate` de calidad, sin baseline, 0.261 s. Está bajo 10 s. No es un crítico de rendimiento. El mismo documento dice que CPLI en esa red queda `no_evaluable` y que el tiempo no incluye el CPM ni prueba la definición de CPLI. G6 no prueba CPLI. Los otros criterios de la sección 11 no se miden ahí. La confirmación de redundancia de 30 000 sigue sin medirse (I-17).

Doble firma: no está, salvo el caso CPLI de ADR-017 (24 h + 16 h, `tests/oracle/span.py` y `tests/test_e3_cpli.py`). No hay caso de SS solapado ni feriado. QC-2 sigue incompleto fuera de ese caso. El criterio de E3 en 10.2 pide todas las métricas contra esperados con doble firma. No se cumple. I-21. La mitad de WBS de R-326 tampoco está implementada. I-24.

Cadena driving: corrección parcial de este ciclo. El test `test_the_longer_predecessor_is_the_driving_one` falló primero con `KeyError: 'driving_codes'` (`docs/qa/E3/ciclo2.md`). Ahora el modo B publica `driving_codes` y `driving_chain`. En la red a mano, SHORT dura 8 h y LONG dura 16 h, ambas FS hacia JOIN. El test afirma que solo LONG es driving y que la cadena de JOIN es LONG y JOIN. `milestone_code="JOIN"` da el mismo conjunto. No es un float path de P6 ni doble firma. El modo A sigue sin marcar driving. No cierra B-12 ni la doble firma. Multiple float paths y la continuidad desde la fecha de corte hasta el término siguen sin implementarse. I-22 e I-23.

No hay críticos. Importantes abiertos de este ciclo: I-19 (G4), I-20 (G13 no medido), I-21 (doble firma), I-22 (cadena driving, corrección parcial que no cierra B-12), I-23 (continuidad y multiple float paths) e I-24 (WBS requerida). Heredados que siguen abiertos y no se cierran: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17 e I-18 parcial. E0, E1 y E2 siguen RECHAZADA-BLOQUEADA. Los resultados de E3 quedan condicionales a I-3 y a esos bloqueos.

No se leyeron datos reales. No se bajaron umbrales. No se reejecutó pytest, el gate ni la mutación. El detalle está en `docs/qa/E3/hallazgos.md`.
