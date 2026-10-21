RECHAZADO

Ciclo 1 de E2. HEAD `c8281a9` (`test(qa): gate E2 ciclo 1, salida 1 (B-02)`). El filtro está en `8bcd892`, integrado por `440b23b`. El gate no está en verde: `docs/qa/E2/gate.json` trae exit_code 1, test_count 174 y cobertura_total 88.9. G4 y G13 están en fail. Hay hallazgos importantes abiertos. APROBADO es imposible. La etapa no se cierra.

Este es el rechazo 1 de 3. Quedan dos ciclos. No se marca la etapa bloqueada: el orquestador lo hace solo tras el tercer rechazo (ADR-013). No se autoriza bajar los umbrales de 8.1 ni los de G13 (ADR-014). Esta revisión no cambia el estado de la etapa.

La excepción de línea base de la sección 10.2 vale solo para E0. En E2, G4 y G13 en fail impiden el cierre. No se marcan pass.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 es `pytest -m perf` sobre `tests/perf`: 2 passed in 1.93 s. Esos tests cronometran la lectura de 30 000 y el filtro de candidatos, no la confirmación. Eso no convierte la confirmación de 30 000 en pass. G10 dice que 12 requisitos de E2 citan un archivo de test que existe; el verde de la suite lo mide G3. No es la meta de 3 minutos ni conformidad con P6.

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta. La proyección de `docs/qa/E2/perf.md` no es una medición de 30 000. No se anota un crítico de tiempo superado.

Importantes de este ciclo, abiertos: G4 (I-15), G13 no medido (I-16), la confirmación de 30 000 que no cumple por proyección (I-17) y QC-2 de redundancia ausente (I-18). I-3 sigue abierto, heredado de E0. No se cierran I-11, I-12, I-13 ni I-14 parcial. E0 y E1 siguen RECHAZADA-BLOQUEADA. Los resultados de E2 quedan condicionales a I-3, I-11, I-12, I-13 e I-14 parcial. B-08, B-09 y B-21 siguen en [VALIDAR].

B-03 y B-04 ya tenían tests en `tests/test_e2_joint.py`, `tests/test_e2_clean.py` y `tests/test_e2_guards.py`. Esos tres archivos no cambiaron desde `3ecec3c`. El filtro nuevo está en `redundant.py`. Si el grafo tiene ciclo, no hay candidatos. Eso es más conservador. No es una relajación.

El detalle está en `docs/qa/E2/hallazgos.md`.
