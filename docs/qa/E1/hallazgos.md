# Hallazgos E1 — ciclo 3

Revisión de QC-6 sobre `docs/qa/E1/gate.md`, `docs/qa/E1/gate.json` (exit_code 1, test_count 173, coverage_percent 88.8), `docs/qa/E1/sabotaje.md`, `docs/qa/E1/QC1_contrato.md`, `docs/qa/E1/perf.md`, el encabezado «v2 — en curso» de `docs/ESTADO.md`, ADR-013, ADR-014 y ADR-017 en `docs/DECISIONES.md`, las secciones 7 (punto 3), 8.1, 8.3, 8.4, 8.5, 10.2 y 11 de `docs/MEGAPROMPT_v2.md`, los puntos 1 a 3 de `docs/VALIDACIONES_PENDIENTES.md`, `tests/oracle/span.py`, `tests/test_e3_oracle.py`, `tests/test_e3_cpli.py`, `tests/test_e1_cycle3_edges.py`, `tests/fixtures/synthetic/cases/cpli.yaml` y el contenido de `tests/fixtures/p6_verified/`. HEAD `947cfcf` (`test(qa): gate E1 ciclo 3, salida 1 (B-17)`). El código del ciclo está en `1e4c8bc`. No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó `docs/ESTADO.md`.

Este es el rechazo 3 de 3. No se autoriza un cuarto ciclo ni bajar umbrales (ADR-014). La regla de cierre exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. ADR-013 no abre otro ciclo de esta etapa. El orquestador cambia el estado después de este rechazo. Esta revisión no lo cambia.

Ciclos previos: ciclo 1 RECHAZADO en `797f559` (gate `b0c5039`). Ciclo 2 RECHAZADO en `1773c0d` (gate `07007ad`, código `734efc9`, ADR-017 un solo caso de CPLI).

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta. La única cifra medida de esa sección es la lectura de 30k: 0.197 s, bajo 15 s. Lo que `perf.md` deja sin medir no se anota como crítico de tiempo superado: no hay cifra. Tampoco es un pass. Va en «No medido».

## Importante

Abiertos. Bloquean el cierre. No se cierran en este ciclo: I-3, I-11, I-12, I-13 y lo que queda de I-14.

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. E0 está RECHAZADA-BLOQUEADA. `docs/qa/E1/QC1_contrato.md` condiciona los resultados de E1 a ese hallazgo y dice que el script actual no abre la carpeta y que esta etapa no la abre. No se releyó el script ni la carpeta. No se cierra I-3.

### I-11 — G4 incumple 8.1

Estado: abierto. El gate lo deja en fail. No se marca pass. Las cifras subieron y no alcanzan.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. G4 falla si eso no se cumple. ADR-014 precisa lo mismo.

El modelo no está en el texto de fail. El detalle del ciclo 3 dice model líneas 100.0 y ramas 100.0. Eso no cierra el hallazgo.

`docs/qa/E1/gate.md` y el texto de fail de `gate.json` nombran solo esto:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 87.3 < 90; ramas 73.6 < 85

Respecto del ciclo 2 (`07007ad`, y el mismo recuento en `docs/ESTADO.md`): calendars 81.6 / 63.9, engine 86.0 / 74.8, cobertura_total 87.9, tests 167. Calendars y engine subieron. Logic no se movió: sigue en 87.3 y 73.6. Ninguna de las seis cifras llega al umbral.

El mismo detalle añade resto líneas 88.9 % y ramas 74.7 %. Las líneas del resto no son el fail: 88.9 está sobre el 80 % de 8.1. Las ramas 74.7 del resto están en el detalle y no están en el texto de fail. ADR-014 no fija umbral de ramas para el resto. No se abre un hallazgo por esa cifra y no se usa para compensar. En el ciclo 2 el resto era líneas 88.8 y ramas 74.5; el alza no cambia la lectura.

La cobertura_total que cita el control es 88.8. La tabla pegada en el detalle cierra con TOTAL 85 % (4003, 448, 1550, 329). En el ciclo 2 esa tabla cerraba en 84 % (4003, 485, 1550, 352). Ni 88.8 ni 85 dejan el control en pass. 85 no es el número de G4.

La corrección `tests/test_e1_cycle3_edges.py` no declara G4. El alza de calendars y engine no lo cierra.

### I-12 — G13 bajo 70 y bajo 85 en engine, calendars y logic

Estado: abierto. El gate lo deja en fail. No se marca pass. El sabotaje no cambió.

`docs/qa/E1/sabotaje.md` no se reejecutó en el ciclo 3. El último commit de ese archivo es `2ed6b43`, ancestro de `947cfcf`, anterior a `1e4c8bc`. El informe que lee el gate es el mismo del ciclo 1 y del ciclo 2.

8.3: en los módulos de la etapa el kill score falla si es menor que 85 % en `engine`, `calendars` y `analysis/logic`, o menor que 70 % en el resto. G13 en `gate.md`: kill_score 54.0 < 70; engine 60.2 < 85; calendars 45.5 < 85; logic 52.0 < 85.

Alcance completo, las mismas cuentas:

- kill_score 54.0; killed 161; survived 137; invalid 4
- engine 60.2 (killed 62, survived 41, invalid 1)
- calendars 45.5 (killed 45, survived 54, invalid 1)
- logic 52.0 (killed 39, survived 36, invalid 2)
- io 71.4 (killed 15, survived 6, invalid 0)

io 71.4 no está en el texto de fail. No se abre un hallazgo contra io y no se usa para compensar el 54.0 ni los tres módulos bajo 85. La corrida es la de los mutantes de `cpm.py`, `worktime.py`, `redundant.py`, `clean.py` y `validate.py`. Cada mutante corrió el subconjunto de tests de su módulo, no la suite entera. Un mutante que no termina en 20 s cuenta como killed. Esa regla favorece el score. El informe no separa cuántos murieron por tiempo. Con esa regla a favor, el resultado igual está bajo el umbral.

Los tests nuevos de `1e4c8bc` no entraron en esa corrida. No cierran G13.

### I-13 — QC-1 tardío

Estado: abierto como desviación de proceso. No se convierte en cumplimiento. No se cierra.

La sección 8.4 exige el contrato antes de escribir código. `docs/qa/E1/QC1_contrato.md` dice que se escribió después del código de xer-io y motor-cpm, ya integrados en `366209b` y `3ddbddd`, y que queda registrado como desviación del ciclo 1. El archivo no se reescribió en el ciclo 3: su último commit es `496b8cc`. `docs/ESTADO.md` dice lo mismo. No se reescribe esa historia. Tener el archivo ahora no hace que 8.4 se haya cumplido a tiempo.

8.5: desviación de la spec. Bloquea el cierre de este ciclo.

### I-14 — QC-2 parcial

Estado: parcial. Sigue abierto como importante. No se cierra.

El ciclo 2, en `734efc9` y ADR-017, agregó un solo caso. El ciclo 3 no tocó `tests/oracle/` ni el YAML. El último commit de `tests/oracle/span.py` sigue siendo `734efc9`.

Lo que sí está:

- `tests/oracle/span.py` recorre la jornada 08:00–16:00 día a día. Solo usa `datetime`. No importa `atlaspmo`. Es el único módulo de `tests/oracle/`.
- `tests/test_e3_oracle.py` llama `work_minutes` de lunes 08:00 a miércoles 16:00 y de miércoles 16:00 a viernes 16:00. Afirma 24 h de largo, 16 h de holgura y el cociente (24 + 16) / 24. No importa `atlaspmo`.
- `tests/fixtures/synthetic/cases/cpli.yaml` es el único YAML del árbol con `calculado_por`, `verificado_por` y `metodo`. El esperado de CPLI es 1.6666666666666667.

Eso no cumple QC-2. La sección 7, punto 3, pide que los esperados de cada caso se recalculen por otro método y que la doble firma quede en el YAML. La sección 8.4 no permite saltar el control: esperados con doble firma, recalculados por otro método.

Lo que falta, y por eso el hallazgo no se cierra:

- El test del oráculo no llama al motor. `tests/test_e3_cpli.py` afirma el mismo cociente, importa `atlaspmo` y no llama a `work_minutes`. Las dos cuentas no están en la misma aserción.
- Fuera de ese caso, QC-2 sigue incompleto. No hay segundo método para restricciones obligatorias, longest path, hito de inicio, redundancia ni BEI. No hay otro YAML con `verificado_por`.
- El contrato, que no se actualizó, sigue diciendo que no declara QC-2 y que los esperados de los casos nuevos salen del calendario y del CPM, no de un segundo cálculo en `tests/oracle/`.

## Corrección del ciclo 3 — no cierra G4 ni G13

`1e4c8bc` agrega solo `tests/test_e1_cycle3_edges.py` (y una nota en `docs/ESTADO.md`, que esta revisión no edita). No cambia `src/`. El archivo dice que esos casos no reclaman G4 ni G13. Son seis tests. El conteo del gate pasa de 167 a 173.

Lo que cubren, leído del archivo:

- Notas del parser de `clndr_data`: semana ausente, marca sin cerrar, turno invertido, turno que no va de `s|` a `f|`, y seriales de excepción rotos que no inventan un turno.
- Minutos negativos: `add_work` y `subtract_work` con −8 h delegan al sentido contrario.
- Piso del epoch: restar trabajo sobre un calendario de 24 h desde el año 1 levanta `CalendarLimitError`.
- `elapsed_calendar`: 60 minutos avanzan una hora, y el trabajo entre un instante y sí mismo es 0.
- Calendario solo con excepción: la semana vacía y un feriado con turno de 08:00 a 12:00. El día siguiente no tiene turno.
- Conformidad vacía: un `Schedule` vacío deja `ratio` en None. Desajuste de fechas y holgura: `early_start`, holgura total y holgura libre quedan en `unexplained` y el ratio baja de 1. Tipo no programado: `TT_Other` queda como «no la calculó el motor». Sin `task_id`, `compared` es 0.

Eso no lleva calendars, engine ni logic a 8.1. No reejecuta la mutación.

## Abierto y no es conformidad con P6

No se cierra. No es un pass del criterio de conformidad de la sección 11. El contrato lo dice: no hay `p6_verified`. `tests/fixtures/p6_verified/` solo tiene `.gitkeep`. La sección 10.2 manda la validación manual a `docs/VALIDACIONES_PENDIENTES.md` y no detiene la ejecución por ella. Por eso no se reclasifica como resultado numérico incorrecto: esta evidencia no trae un número de P6. Tampoco autoriza a llamarlo conformidad.

| Brecha | Requisito | Qué dice el contrato | Qué queda abierto |
|---|---|---|---|
| B-08 | R-012, R-163 | implementado, [VALIDAR] con `p6_verified` | restricciones. `VALIDACIONES_PENDIENTES.md` pide confirmar `CS_MANDSTART` y `CS_MANDFIN` |
| B-09 | R-013, R-165 | implementado, [VALIDAR] | longest path. No hay contraste con P6 |
| B-21 | R-015, R-164 | implementado, [VALIDAR] | hito de inicio. `VALIDACIONES_PENDIENTES.md` pide confirmar si el que cae a las 16:00 pasa al inicio laboral siguiente |

G10 en pass solo comprueba que el archivo de test citado existe. No convierte esas filas en conformidad.

El contrato tampoco declara la UDF como marca de hito contractual: no hay columna verificada; el camino que declara es la lista de códigos. No se da por cumplido ese punto. B-04 es alcance de E2.

## No medido — no es pass

La sección 11 dice que «no medido» nunca equivale a cumplido. `docs/qa/E1/perf.md` mide una sola fila y deja el resto sin cifra. G6 en pass no cubre lo no medido. El test `tests/perf/test_scale.py` exige menos de 15 s y cronometra solo `read_xer`. El 0.59 s del detalle de G6 es la duración de esa corrida de pytest, no el tiempo de lectura.

Medición que sí está, en esta máquina, el 2026-10-21, fuera de la aserción del test. No se versionó el XER.

| Dato | Valor |
|---|---|
| CPU | Intel Core Ultra 9 185H |
| RAM | 31.4 GB |
| SO | Windows 11 Enterprise |
| Archivo | `gen_scale.py`, 30 000 actividades, `series=False` |
| Tamaño | 4 218 499 bytes |
| `read_xer` | 0.197 s |

0.197 s está bajo 15 s. Cumple esa fila y ninguna otra. No es un crítico: no supera la meta.

| Criterio de la sección 11 | Meta | Estado en esta etapa |
|---|---|---|
| Lectura de un XER de 30k | < 15 s | medido, 0.197 s, bajo la meta |
| DCMA + chequeos de calidad | < 10 s | no medido; no es pass. La fila es de E3 |
| Redundancia con confirmación | < 3 min | no medido; no es pass. El contrato lo dice. La fila es de E2. También dice que el algoritmo de 30k no está |
| Monte Carlo, 1 000 iteraciones, 30k | < 5 min | no medido; no es pass. La fila es de E4 |
| Conformidad CPM vs. P6 | ≥ 99,5 % en reales; 100 % en `p6_verified`; 100 % de diferencias explicadas | no medido; no hay export verificado; no es pass |

No se baja de etapa el trabajo de E2, E3 o E4. No se sube tampoco: estas cuatro filas no quedan cumplidas.

## Menor

No bloquean. No autorizan el cierre.

### M-7 — el encabezado del ciclo 3 está; queda una frase vieja

`docs/ESTADO.md` ya describe el ciclo 3: salida 1, test_count 173, cobertura_total 88.8, y G4 y G13 en fail. También deja, más arriba, la frase de que el veredicto de trabajo sigue siendo el del ciclo 1 hasta que el revisor del ciclo 2 lo reemplace. Eso ya no es cierto: el ciclo 2 quedó RECHAZADO en `1773c0d`. Esta revisión no editó ese archivo. No cambia cifras ni cierra un importante.

### M-8 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest` en este equipo.

### M-9 — G12 no compara tiempos

Pass: tests 173 frente a 137 de E0. `gate.json` trae `"benchmarks": {}`. No hay comparación de benchmark contra la etapa anterior. No es un fail de G12 y no acredita tiempos de la sección 11. La cobertura_total 88.8 frente a 87.5 de E0, y frente a 87.9 del ciclo 2, no se usa para declarar G4 en pass.

### M-10 — `gate.md` corta el detalle

La línea de G4 en `docs/qa/E1/gate.md` se corta en «engine lineas 89.». La de G6 se queda en la barra de progreso. Las cifras completas, incluido el modelo en 100/100, el resto en 88.9 / 74.7 y el «1 passed in 0.59s», están en `gate.json`. No cambia I-11 ni el fail.

## Gate

Exit code 1. test_count 173. Cobertura citada por el control: 88.8. Rechazo 3 de 3. No se autoriza un cuarto ciclo ni bajar umbrales. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-8 |
| G4 | fail | I-11. No es pass. No cerrado. Las cifras subieron y no alcanzan 8.1 |
| G5 | pass | invariantes a-e con perfil qa. No se releyeron los tests. El contrato atribuye 500 ejemplos al perfil `qa` del round-trip (R-016) |
| G6 | pass | un test, 0.59 s. Solo la lectura. El resto de la sección 11 no es pass |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 36 requisitos citan un archivo que existe. No es conformidad ni cierra [VALIDAR] |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | 173 frente a 137. Ver M-9 |
| G13 | fail | I-12. No es pass. No cerrado. Sabotaje sin reejecutar |
