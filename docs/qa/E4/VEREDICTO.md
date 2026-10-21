RECHAZADO

Ciclo 1 de E4. Este es el rechazo 1 de 3. La etapa no queda bloqueada. Esta corrida no la cierra. HEAD `6163ea294f652edb4ad821fccba442125b665ab3` (`test(qa): gate E4 ciclo 1, salida 1 (B-07)`). El gate no está en verde: `docs/qa/E4/gate.json` trae exit_code 1, test_count 205 y coverage_percent 89.5. Fallan G4 y G13. Hay importantes abiertos. La etapa no se cierra.

El cierre no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser de cierre.

La excepción de línea base de la sección 10.2 vale solo para E0. En E4, G4 y G13 en fail impiden el cierre. No se marcan pass. No se bajan umbrales.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 registra 4 passed in 4.01 s. Ese verde no es el criterio de la sección 11. G10 dice que 13 requisitos de E4 citan un archivo de test que existe; el verde de la suite lo mide G3. No comprueba el cono, la curva por periodo ni la meta de 5 minutos.

G4 incumple 8.1, igual que E3 en las seis cifras de paquete: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. El umbral de 8.1 es 90 % de líneas y 85 % de ramas. cobertura_total 89.5. El modelo está en 100.0 / 100.0 y no está en el texto de fail. El resto, líneas 89.8, está sobre el 80 % y no compensa. No se marca pass. El detalle está en I-25.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E4/sabotaje.md`. No se inventa un kill score y no se copia el de E1. No medido no es un pase. El detalle está en I-26.

El tornado sigue reprogramando el cronograma completo por actividad. La frase de `src/atlaspmo/analysis/risk/montecarlo.py` dice que no recorta al cono de sucesoras. `tests/test_e4_tornado.py` afirma esa frase. No es el recorte de M5 ni de B-07. El detalle está en I-27.

`fact_timephased` guarda la duración remanente en el balde «corte». No es una curva por periodo, ni un histograma, ni sobreasignación. El PV sigue siendo lineal. La curva S tiene un solo punto, en la fecha de corte. El detalle está en I-28.

`docs/qa/E4/perf.md`, en este equipo el 2026-10-21, red de `gen_scale` de 30 000 actividades con `series=False`, sin XER real: un CPM midió 9.401 s. Monte Carlo de 30 000 por 1 000 no se corrió. La proyección 1 000 × 9.401 s son unas 2,6 h. No es una medición y no cumple 5 minutos. No hay crítico de un tiempo medido por encima de 5 minutos, porque las 1 000 iteraciones no se corrieron. El test de perf solo corre 4 iteraciones de 2 actividades. No medido no es un pase. El detalle está en I-29. numba no está cargado.

El invariante e ya estaba en `tests/property/test_invariant_e.py`. La cita vieja `tests/property/test_risk.py` se corrigió: R-042 apunta a ese archivo. No es doble firma. G5 en verde no cierra B-07 ni QC-2.

No hay críticos. Importantes abiertos de E4: I-25 (G4), I-26 (G13 no medido), I-27 (el cono), I-28 (la curva por periodo) e I-29 (la meta de 5 minutos). Heredados que siguen abiertos y no se cierran ni se reabren: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17, I-18 parcial, y los de E3 (I-19 G4, I-20 G13, I-21 doble firma, I-22 driving parcial, I-23 float paths y continuidad, I-24 WBS). E0, E1, E2 y E3 siguen bloqueadas, cada una tras su tercer rechazo, sin cuarto ciclo. Los resultados de E4 quedan condicionales a I-3 y a esos bloqueos. Esta revisión no les cambia el estado.

No se leyeron datos reales. No se bajaron umbrales. No se reejecutó pytest, el gate ni la mutación. El detalle está en `docs/qa/E4/hallazgos.md`.
