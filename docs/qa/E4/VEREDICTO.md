RECHAZADA-BLOQUEADA

Diagnóstico de esta corrida, después del tercer rechazo. No es APROBADO. G4 sigue bajo 8.1: calendars 85.2/70.9, engine 89.4/79.5, logic 88.6/75.3. G13 no está medido y no se copia un kill score de otra etapa. Un CPM de 30 000 midió 9.401 s. Las 1 000 iteraciones no se corrieron; la proyección no cumple 5 minutos y no es una medición. El tornado no recorta al cono. `fact_timephased` queda en el balde corte, no en una curva por periodo. No hay cuarto ciclo. Las etapas siguientes quedan condicionales a este bloqueo y a I-3.

Texto del revisor, que esta corrida no convierte en APROBADO:

Ciclo 3 de E4. Este es el rechazo 3 de 3. Esta revisión no marca la etapa bloqueada. El orquestador cambia el estado después. No se autoriza un cuarto ciclo. Esta corrida no la cierra. HEAD `515ac6c42276afd32bfa988e9f108ac0c7571dbf` (`test(qa): gate E4 ciclo 3, salida 1 (B-07)`). El gate repite los ciclos 1 y 2 y no está en verde: `docs/qa/E4/gate.json` trae exit_code 1, test_count 205 y coverage_percent 89.5. Fallan G4 y G13, con las mismas cifras. Hay importantes abiertos. La etapa no se cierra.

No autorizo un cuarto ciclo ni bajar los umbrales de 8.1 ni los de G13 (ADR-014). ADR-013 no abre otro ciclo de esta etapa tras el tercer rechazo. Esta revisión no lo cambia y no marca la etapa bloqueada. No se copia un kill score.

El cierre no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser de cierre.

La excepción de línea base de la sección 10.2 vale solo para E0. En E4, G4 y G13 en fail impiden el cierre. No se marcan pass. No se bajan umbrales.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 registra 4 passed in 3.80 s. Ese verde no es el criterio de la sección 11. G10 dice que 13 requisitos de E4 citan un archivo de test que existe; el verde de la suite lo mide G3. No comprueba el cono, la curva por periodo ni la meta de 5 minutos.

`515ac6c` reescribe dos relojes de `docs/qa/E4/gate.json` y toca `docs/ESTADO.md`. Esta revisión no editó ese archivo. La suite de cobertura pasa de 19.00 s a 18.58 s, y G6 de 3.90 s a 3.80 s. En el ciclo 1 eran 19.64 s y 4.01 s. Las seis cifras de paquete no se mueven. Entre `bec5c9b21c7709caa4c8fba117ffbd66a207dc53` y este HEAD no hay diff en `src/`, `tests/` ni `scripts/`. `docs/qa/E4/gate.md` y `docs/qa/E4/perf.md` no cambian. `docs/qa/E4/ciclo3.md` no cambia código.

G4 incumple 8.1, igual que los ciclos 1 y 2 y que E3 en las seis cifras de paquete: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. El umbral de 8.1 es 90 % de líneas y 85 % de ramas. cobertura_total 89.5. El modelo está en 100.0 / 100.0 y no está en el texto de fail. El resto, líneas 89.8, está sobre el 80 % y no compensa. No se marca pass. El detalle está en I-25.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E4/sabotaje.md`. No se inventa un kill score y no se copia el de otra etapa. No medido no es un pase. El detalle está en I-26.

El tornado no se recorta al cono. `ciclo3.md` no agrega código. El ciclo 2 ya dejó escrito que no se integra. No haberlo integrado no cumple M5 ni B-07. El contraste del ciclo 1 queda vigente, porque el código no cambió. El detalle está en I-27.

`fact_timephased` sigue en el balde corte. No es una curva por periodo. El histograma y la sobreasignación siguen sin implementarse. El detalle está en I-28.

`docs/qa/E4/perf.md`, en este equipo el 2026-10-21, red de `gen_scale` de 30 000 actividades con `series=False`, sin XER real: un CPM midió 9.401 s. Monte Carlo de 30 000 por 1 000 no se corrió. La proyección 1 000 × 9.401 s son unas 2,6 h. No es una medición y no cumple 5 minutos. No hay crítico de un tiempo de 1 000 iteraciones medido por encima de la meta, porque no se midió. El test de perf solo corre 4 iteraciones de 2 actividades. No medido no es un pase. El detalle está en I-29. numba no está cargado. `ciclo3.md` no afirma una wheel que deje el resultado bajo 5 minutos.

El invariante e ya estaba. No hay diff de producto, así que la lectura del ciclo 1 sigue: no es doble firma. G5 en verde no cierra B-07 ni QC-2.

No hay críticos. Importantes abiertos de E4, y siguen abiertos: I-25 (G4), I-26 (G13 no medido), I-27 (el cono), I-28 (la curva por periodo) e I-29 (la meta de 5 minutos). Heredados que siguen abiertos y no se cierran ni se reabren: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17, I-18 parcial, y los de E3 (I-19 G4, I-20 G13, I-21 doble firma, I-22 driving parcial, I-23 float paths y continuidad, I-24 WBS). E0, E1, E2 y E3 siguen RECHAZADA-BLOQUEADA, cada una tras su tercer rechazo, sin cuarto ciclo. Los resultados de E4 quedan condicionales a I-3 y a esos bloqueos. Esta revisión no les cambia el estado y no marca E4 bloqueada.

No se leyeron datos reales. No se bajaron umbrales. No se reejecutó pytest, el gate ni la mutación. El ciclo 1 quedó RECHAZADO en `ab66a973a0e3057a4ee1af837842073a4f750a87`, sobre el gate `6163ea294f652edb4ad821fccba442125b665ab3`. El ciclo 2 quedó RECHAZADO en `b04ffa2`, sobre el gate `bec5c9b21c7709caa4c8fba117ffbd66a207dc53`. El detalle está en `docs/qa/E4/hallazgos.md`.
