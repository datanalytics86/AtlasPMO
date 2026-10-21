RECHAZADO

Ciclo 2. Este es el rechazo 2 de 3. HEAD `07007ad`. El código del ciclo está en `734efc9`. El gate no está en verde: `docs/qa/E1/gate.json` trae exit_code 1, test_count 167 y cobertura_total 87.9. G4 y G13 están en fail. Hay hallazgos importantes abiertos. No es APROBADO.

No autorizo un cuarto ciclo ni bajar los umbrales de 8.1 ni los de G13. Queda un ciclo de corrección. Si ese tercer ciclo también sale RECHAZADO, la etapa queda RECHAZADA-BLOQUEADA (ADR-013). Esta revisión no la marca bloqueada.

La excepción de línea base de la sección 10.2 vale solo para E0. En E1, G4 y G13 en fail impiden el cierre. No se marcan pass ni se dan por cerrados.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 es un test en 0.54 s: cubre la lectura, no el resto de la sección 11. G10 dice que 36 requisitos de E1 citan un archivo de test que existe; el verde de la suite lo mide G3. Eso no es conformidad con P6.

G4 incumple 8.1. Quedan bajo el umbral calendars líneas 81.6 y ramas 63.9, engine líneas 86.0 y ramas 74.8, logic líneas 87.3 y ramas 73.6. El modelo ya no está en el fail: líneas 100.0 y ramas 100.0. El resto, líneas 88.8, tampoco es el fail: 8.1 pide 80 % de líneas y 88.8 está sobre ese piso. Las ramas 74.5 del resto aparecen en el detalle y no están en el texto de fail. La cobertura_total 87.9 no compensa. El TOTAL 84 % de la tabla pegada (4003, 485, 1550, 352) no es el número de G4.

G13 no se reejecutó. `docs/qa/E1/sabotaje.md` sigue en `2ed6b43`. kill_score 54.0 < 70; engine 60.2 < 85; calendars 45.5 < 85; logic 52.0 < 85. io 71.4 no compensa. Alcance completo. Mutantes de `cpm.py`, `worktime.py`, `redundant.py`, `clean.py` y `validate.py`. Un mutante que no termina en 20 s cuenta como killed y favorece el score.

La lectura de 30k está medida: 0.197 s, bajo 15 s, en `docs/qa/E1/perf.md`. DCMA 30k, redundancia 30k, Monte Carlo 30k por 1 000 y conformidad con P6 no están medidos. No medido no es pass ni un crítico de tiempo superado. No hay críticos.

I-14 queda parcial y no se cierra. ADR-017 y `tests/oracle/span.py` cubren un solo caso de CPLI: 24 h de largo y 16 h de holgura, recorrido día a día de un calendario 08:00–16:00 de siete días, sin importar `atlaspmo`. QC-2 sigue incompleto fuera de ese caso. No cubre restricciones obligatorias, longest path, hito, redundancia ni BEI como segundo método.

Siguen abiertos I-3, I-11, I-12 e I-13. E0 sigue RECHAZADA-BLOQUEADA. Los resultados de E1 son condicionales a I-3. No se cierra I-3. QC-1 sigue siendo posterior a `366209b` y `3ddbddd`. No se reescribe esa historia. B-08, B-09 y B-21 siguen en [VALIDAR]: no son conformidad con P6. El detalle está en `docs/qa/E1/hallazgos.md`.
