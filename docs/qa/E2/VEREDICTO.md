RECHAZADO

Ciclo 2 de E2. HEAD `d494694` (`test(qa): gate E2 ciclo 2, salida 1 (B-02)`). El oráculo del ciclo está en `2182e71`. El veredicto del ciclo 1 queda en `e41a452`, sobre el gate `c8281a9`. El filtro sigue en `8bcd892`, integrado por `440b23b`. El gate no está en verde: `docs/qa/E2/gate.json` trae exit_code 1, test_count 175 y cobertura_total 88.9. G4 y G13 están en fail. Hay hallazgos importantes abiertos. La etapa no se cierra.

Este es el rechazo 2 de 3. Queda un ciclo. No se marca la etapa bloqueada: el orquestador lo hace solo tras el tercer rechazo (ADR-013). No se autoriza bajar los umbrales de 8.1 ni los de G13 (ADR-014). Esta revisión no cambia el estado de la etapa.

La excepción de línea base de la sección 10.2 vale solo para E0. En E2, G4 y G13 en fail impiden el cierre. No se marcan pass.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 es `pytest -m perf` sobre `tests/perf`: 2 passed in 1.83 s. Esos tests cronometran la lectura de 30 000 y el filtro de candidatos, no la confirmación. Eso no convierte la confirmación de 30 000 en pass. G10 dice que 12 requisitos de E2 citan un archivo de test que existe; el verde de la suite lo mide G3. No es la meta de 3 minutos ni conformidad con P6.

G4 no se movió respecto del ciclo 1. Siguen bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 88.9. El modelo no está en el texto de fail: líneas 100.0 y ramas 100.0. El oráculo no entra en esos paquetes.

G13 sigue sin informe. No está medido. No se usa el 54.0 de E1 como score de este gate.

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta. La proyección de `docs/qa/E2/perf.md` no es una medición de 30 000. No se anota un crítico de tiempo superado. El criterio de 3 minutos igual no está cumplido.

Importantes de este ciclo, abiertos: G4 (I-15), G13 no medido (I-16), la confirmación de 30 000 que no cumple por proyección (I-17) y QC-2 de redundancia parcial (I-18). I-18 no se cierra. I-3 sigue abierto, heredado de E0. No se cierran I-11, I-12, I-13 ni I-14 parcial. E0 y E1 siguen sin cuarto ciclo, tras su tercer rechazo. Los resultados de E2 quedan condicionales a I-3, I-11, I-12, I-13 e I-14 parcial. B-08, B-09 y B-21 siguen en [VALIDAR].

La corrección del ciclo es ADR-018, `tests/oracle/pathlen.py` y `tests/test_e2_oracle.py`. Suma 8 y 8 y compara el total con un lag. No importa `atlaspmo`. Es un solo caso. No cierra QC-2. No mueve G4, ni G13, ni la confirmación de 30 000.

B-03 y B-04 no se tocaron en este ciclo. El diff desde `e41a452` no incluye `redundant.py` ni `tests/test_e2_joint.py`, `tests/test_e2_clean.py` ni `tests/test_e2_guards.py`. No es una relajación.

El detalle está en `docs/qa/E2/hallazgos.md`.
