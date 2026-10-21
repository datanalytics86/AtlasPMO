RECHAZADA-BLOQUEADA

Ciclo 3. El revisor emitió RECHAZADO. Esta corrida, por ADR-013, no abre un cuarto ciclo. No es APROBADO.

Diagnóstico. El gate del ciclo 3 (`947cfcf`, código en `1e4c8bc`) sale 1. G4 sigue bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 87.3 y ramas 73.6. cobertura_total 88.8. test_count 173. Esas cifras subieron desde el ciclo 2 (calendars 81.6/63.9, engine 86.0/74.8, total 87.9, 167 tests) y no alcanzan. G13 no se reejecutó: kill_score 54.0, engine 60.2, calendars 45.5, logic 52.0, con 137 sobrevivientes en alcance completo. No se bajaron umbrales (ADR-014).

Qué se intentó. Ciclo 2: oráculo de un caso de CPLI (ADR-017) y las ramas del modelo, que quedaron en 100/100. Ciclo 3: notas del parser de calendario, minutos negativos, piso del epoch, calendario solo con excepción y desajustes de conformidad. I-11, I-12 e I-13 siguen abiertos. I-14 queda parcial: el oráculo no cubre el resto de los esperados. I-3, heredado de E0, sigue abierto. E2 a E6 quedan condicionales a esos hallazgos. No se reescribe historia.

Texto del revisor, que esta corrida no convierte en APROBADO:

Ciclo 3. Este es el rechazo 3 de 3. HEAD `947cfcf` (`test(qa): gate E1 ciclo 3, salida 1 (B-17)`). El código del ciclo está en `1e4c8bc`. El gate no está en verde: `docs/qa/E1/gate.json` trae exit_code 1, test_count 173 y cobertura_total 88.8. G4 y G13 están en fail. Hay hallazgos importantes abiertos. La etapa no se cierra.

No autorizo un cuarto ciclo ni bajar los umbrales de 8.1 ni los de G13 (ADR-014). ADR-013 no abre otro ciclo de esta etapa tras el tercer rechazo. El orquestador cambia el estado después. Esta revisión no lo cambia.

La excepción de línea base de la sección 10.2 vale solo para E0. En E1, G4 y G13 en fail impiden el cierre. No se marcan pass ni se dan por cerrados.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 es un test en 0.59 s: cubre la lectura, no el resto de la sección 11. G10 dice que 36 requisitos de E1 citan un archivo de test que existe; el verde de la suite lo mide G3. Eso no es conformidad con P6.

G4 incumple 8.1. Subieron respecto del ciclo 2 y no alcanzan. Ciclo 2, en el gate `07007ad` y en `docs/ESTADO.md`: calendars líneas 81.6 y ramas 63.9, engine líneas 86.0 y ramas 74.8, cobertura_total 87.9, tests 167. Ciclo 3: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, cobertura_total 88.8, tests 173. Logic no se movió: líneas 87.3 y ramas 73.6. El modelo no está en el texto de fail: líneas 100.0 y ramas 100.0. El resto, líneas 88.9, tampoco es el fail: 8.1 pide 80 % de líneas. Las ramas 74.7 del resto aparecen en el detalle y no están en el texto de fail. La cobertura_total 88.8 no compensa. El TOTAL 85 % de la tabla pegada (4003, 448, 1550, 329) no es el número de G4. No se marca pass.

G13 no se reejecutó. `docs/qa/E1/sabotaje.md` sigue en `2ed6b43`, con alcance completo. kill_score 54.0 < 70; engine 60.2 < 85; calendars 45.5 < 85; logic 52.0 < 85. io 71.4 no compensa. Un mutante que no termina en 20 s cuenta como killed y favorece el score.

La corrección del ciclo 3 es `tests/test_e1_cycle3_edges.py`, en `1e4c8bc`. Cubre notas del parser, minutos negativos, el piso del epoch, un calendario solo con excepción, conformidad vacía, tipo no programado, desajuste de fechas y holgura. No toca `src/`. No cierra G4 ni G13.

La lectura de 30k está medida: 0.197 s, bajo 15 s, en `docs/qa/E1/perf.md`. DCMA 30k, redundancia 30k, Monte Carlo 30k por 1 000 y conformidad con P6 no están medidos. No medido no es pass ni un crítico de tiempo superado. No hay críticos.

I-14 queda parcial y no se cierra. ADR-017 y `tests/oracle/span.py` cubren un solo caso de CPLI: 24 h de largo y 16 h de holgura. No cubre restricciones obligatorias, longest path, hito, redundancia ni BEI como segundo método.

Siguen abiertos I-3, I-11, I-12 e I-13. E0 sigue RECHAZADA-BLOQUEADA. Los resultados de E1 son condicionales a I-3. No se cierra I-3. QC-1 sigue siendo posterior a `366209b` y `3ddbddd`. No se reescribe esa historia. B-08, B-09 y B-21 siguen en [VALIDAR]: no son conformidad con P6.

Ciclos previos: ciclo 1 RECHAZADO en `797f559` (gate `b0c5039`). Ciclo 2 RECHAZADO en `1773c0d` (gate `07007ad`, código `734efc9`, ADR-017 un solo caso de CPLI). El detalle está en `docs/qa/E1/hallazgos.md`.
