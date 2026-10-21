RECHAZADO

Ciclo 1. HEAD `b0c5039`. El gate no está en verde: `docs/qa/E1/gate.json` trae exit_code 1 y test_count 165. G4 y G13 están en fail. Hay hallazgos importantes abiertos. No es APROBADO.

La excepción de línea base de la sección 10.2 vale solo para E0. En E1, G4 y G13 en fail impiden el cierre. No se marcan pass ni se dan por cerrados.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G5 es «invariantes a-e con perfil qa». G6 es un test en 0.64 s: cubre la lectura, no el resto de la sección 11. G10 dice que 36 requisitos de E1 citan un archivo de test que existe; el verde de la suite lo mide G3. Eso no es conformidad con P6.

G4 incumple 8.1. Quedan bajo el umbral calendars líneas 81.6 y ramas 63.9, engine líneas 86.0 y ramas 74.8, logic líneas 87.3 y ramas 73.6, y model ramas 62.5. La cobertura_total 87.8 no compensa. G13 queda bajo 70 y bajo 85 en engine, calendars y logic: kill_score 54.0, engine 60.2, calendars 45.5, logic 52.0. Alcance completo en `docs/qa/E1/sabotaje.md`. io 71.4 no es la causa del fail.

La lectura de 30k está medida: 0.197 s, bajo 15 s, en `docs/qa/E1/perf.md`. DCMA 30k, redundancia 30k, Monte Carlo 30k por 1 000 y conformidad con P6 no están medidos. No medido no es pass. Restricciones, longest path e hito de inicio siguen en [VALIDAR]: no hay `p6_verified` y no son conformidad con P6.

QC-1 se escribió después del código ya integrado en `366209b` y `3ddbddd`. La sección 8.4 pedía el contrato antes de implementar. Es desviación de proceso del ciclo 1. No se reescribe esa historia y no se toma el contrato tardío como si el control se hubiera cumplido a tiempo.

Sigue abierto I-3 de E0: R-198 no prueba que `run_conformance` no abra `ATLASPMO_GOLDEN_DIR`. E0 sigue RECHAZADA-BLOQUEADA. Esta revisión no leyó `data/real` ni esa carpeta, no reejecutó la suite y no cierra I-3. El detalle está en `docs/qa/E1/hallazgos.md`.
