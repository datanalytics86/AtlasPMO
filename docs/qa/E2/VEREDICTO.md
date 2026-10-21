RECHAZADA-BLOQUEADA

Ciclo 3. El revisor emitió RECHAZADO. Esta corrida, por ADR-013, no abre un cuarto ciclo. No es APROBADO.

Diagnóstico. El gate del ciclo 3 (`21cfe63`) sale 1. G4 sigue bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 88.9. test_count 175. G13 no está medido: falta el informe de E2, y el 54.0 de E1 no se copia porque `redundant.py` cambió. El filtro de 30 000 actividades tardó 0.345 s. La confirmación de 30 000 no se corrió. En 400 actividades tardó 58.1 s y la proyección queda en decenas de horas: no cumple los 3 minutos y no es una medición de 30 000. El atajo de holgura clasificó mal 41 vínculos en una red de 100 y no se integró. I-15, I-16, I-17 e I-18 parcial siguen abiertos, junto con I-3. E3 a E6 quedan condicionales. No se reescribe historia.

Texto del revisor, que esta corrida no convierte en APROBADO:

Ciclo 3 de E2. Este es el rechazo 3 de 3. HEAD `21cfe63` (`test(qa): gate E2 ciclo 3, salida 1 (B-02)`). El atajo que no se integró está en `fbfff7b`. El gate no está en verde: `docs/qa/E2/gate.json` trae exit_code 1, test_count 175 y cobertura_total 88.9. Fallan G4 y G13. Hay importantes abiertos. La etapa no se cierra.

No autorizo un cuarto ciclo ni bajar los umbrales de 8.1 ni los de G13 (ADR-014). ADR-013 no abre otro ciclo de esta etapa tras el tercer rechazo. El orquestador cambia el estado después. Esta revisión no lo cambia y no marca la etapa bloqueada.

La excepción de línea base de la sección 10.2 vale solo para E0. En E2, G4 y G13 en fail impiden el cierre. No se marcan pass.

Pass del gate, sin que alcancen: G1, G2, G3 y G5 a G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 es `pytest -m perf` sobre `tests/perf`: 2 passed in 1.84 s. Esos tests cronometran la lectura de 30 000 y el filtro de candidatos, no la confirmación. G10 dice que 12 requisitos de E2 citan un archivo de test que existe; el verde de la suite lo mide G3. No es la meta de 3 minutos ni conformidad con P6.

Contraste de las tres evidencias. Las cifras de cobertura no se movieron. El atajo no entró al árbol. El tiempo de 30 000 sigue sin medirse.

`docs/qa/E2/gate.md` sale 1. G4, igual que el ciclo 2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 88.9. En `gate.json` el TOTAL de la tabla sigue en 85 % (4055, 450, 1576, 333). Lo único que cambió de reloj es la suite de ese control, 18.18 s frente a 24.38 s, y G6, 1.84 s frente a 1.83 s. Ninguno de los dos es la confirmación de 30 000. El modelo no está en el texto de fail: líneas 100.0 y ramas 100.0.

`docs/qa/E2/ciclo3.md` no es un cambio de código. Fuera del repositorio, un atajo de holgura clasificó mal 41 vínculos en una red de 100 y no se integró. No acelera la confirmación de 30 000. No toca G4 ni G13. No baja umbrales. `21cfe63` solo reescribe el gate y el encabezado de estado.

`docs/qa/E2/perf.md` no cambió. El filtro de 30 000 está medido: 0.345 s. La confirmación de 30 000 no se corrió. La proyección no cumple los 3 minutos y no es una medición. No anoto un crítico de tiempo: no hay una cifra medida de 30 000 por encima de la meta. El criterio igual no está cumplido.

G13 sigue sin informe. No está medido. No se marca pass. No se copia el kill score de E1 como score de este gate.

ADR-018 sigue cubriendo un solo camino de 8 h + 8 h. I-18 queda parcial y no se cierra. El ciclo 3 no agregó otro caso.

No hay críticos. Importantes abiertos de E2: G4 (I-15), G13 no medido (I-16), la confirmación de 30 000 que no cumple por proyección (I-17) y QC-2 parcial (I-18). I-3 sigue abierto, heredado de E0. No se cierran I-11, I-12, I-13 ni I-14 parcial. E0 y E1 siguen bloqueadas, cada una tras su tercer rechazo, sin cuarto ciclo. Los resultados de E2 quedan condicionales a I-3, I-11, I-12, I-13 e I-14 parcial. B-08, B-09 y B-21 siguen en [VALIDAR].

Ciclos previos: ciclo 1 en `e41a452`, sobre el gate `c8281a9`. Ciclo 2 en `339cafd`, sobre el gate `d494694` y el oráculo `2182e71`. El detalle está en `docs/qa/E2/hallazgos.md`.
