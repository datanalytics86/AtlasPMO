RECHAZADO

Ciclo 1 de E6. Este es el rechazo 1 de 3. La etapa no queda bloqueada. No es el tercer rechazo y esta revisión no la marca bloqueada. Cabe un ciclo de corrección. No se autoriza saltar el tope de tres. HEAD `d75593cdd1c58b02a4c7fb08028d33a0fcfb322a` (`test(qa): gate E6 ciclo 1, salida 1 (B-16)`). El gate no está en verde: `docs/qa/E6/gate.json` trae exit_code 1, test_count 216 y coverage_percent 89.8. Pasan G1, G2, G3 y G5 a G12. Fallan G4 y G13. Hay importantes abiertos. La etapa no se cierra.

El cierre no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser de cierre.

La excepción de línea base de la sección 10.2 vale solo para E0. En E6, G4 y G13 en fail impiden el cierre. No se marcan pass. No se bajan umbrales.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 registra 4 passed in 3.66 s. Ese verde no es la sección 11 completa. G10 dice que 5 requisitos de E6 citan un archivo de test que existe. El verde de la suite lo mide G3. No mide el 99,5 % ni el 100 %, ni una tendencia de cronogramas reales.

`d75593c` agrega `docs/qa/E6/gate.json` y `docs/qa/E6/gate.md`, y toca `docs/ESTADO.md`. Esta revisión no editó ese archivo. Las pruebas y el manual están en `e47f8c1` (`test(e6): tendencia, omision y conformidad no medida (B-16)`). El contrato es `0327903`, anterior al código. Esta revisión no reejecutó pytest, el gate ni la mutación. No se abrió un navegador. No se leyó `data/real/` ni un `ATLASPMO_GOLDEN_DIR` real.

G4 incumple 8.1. El umbral es 90 % de líneas y 85 % de ramas. Este gate: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.8. El modelo en 100.0 / 100.0 y el resto en líneas 90.2 no compensan. No se marca pass. La línea base no se aplica a E6. El detalle está en I-35.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E6/sabotaje.md`. No se inventa un kill score y no se copia el de otra etapa. No medido no es un pase. La fila E6 de 10.2 pide G13 sobre todo `src/`. Sin informe, eso no está evidenciado. El detalle está en I-36.

La sección 11 no está medida como conjunto. G6 en verde no la completa. La lectura de 30 000 midió 0.197 s en `docs/qa/E1/perf.md`; está bajo 15 s y no se reejecutó aquí. DCMA `evaluate` midió 0.261 s en `docs/qa/E3/perf.md` y en esa red CPLI queda `no_evaluable`. El filtro de 30 000 midió 0.345 s y la confirmación no se corrió (`docs/qa/E2/perf.md`). Un CPM de 30 000 midió 9.401 s. Monte Carlo de 30 000 por 1 000 no se corrió; la proyección de unas 2,6 h no es una medición y no cumple 5 minutos (`docs/qa/E4/perf.md`). La conformidad contra P6 no se puede correr aquí. El detalle está en I-37.

R-181: `Library.trend` ordena dos puntos sintéticos de `quality_index`. No es una tendencia de cronogramas reales. No se marca como tal.

R-196: la prueba renombra un momento la carpeta `tests/fixtures/p6_verified`, que solo tiene `.gitkeep`, ve `p6_verified: omitido` y la restaura. No edita `docs/qa/skips.toml`. No agrega un `skip`.

R-304: con la variable ausente el script imprime `golden: omitido`. Con una carpeta temporal no imprime el nombre y no cambia los bytes. El 99,5 % y el 100 % no están medidos. No es un pase de la sección 11.

R-180 sigue en `tests/test_phase4.py`. No es una comparación contra P6.

El manual, en `e47f8c1`, describe límites: el baseline no se asocia, no hay avance parcial, el visor solo aparece con tabla CPM, y la conformidad con P6 no está medida. No cierra B-01. No afirma un gate en verde.

E6 queda condicional a I-3 y a E0, E1, E2, E3, E4 y E5, cada una en el estado de su tercer rechazo, sin cuarto ciclo. Esta revisión no les cambia el estado y no las reabre. No se leyeron datos reales. No se bajaron umbrales. No se copió un kill score. El detalle está en `docs/qa/E6/hallazgos.md`.

No hay críticos. Importantes abiertos de este ciclo, y bloquean el cierre: I-35 (G4), I-36 (G13 no medido) e I-37 (la sección 11 no está medida). Ninguno se cierra. Heredados que siguen abiertos y no se cierran ni se reabren: I-3 y los de E1 a E5, I-11 a I-34.
