# E1 · motor-cpm

Rama `e1/motor-cpm` (worktree hermano del checkout `v2`, sin push). Base `d5ac773`.

Commits:

- `f0854f7` `feat(calendars): indice laboral O(log n) y horizonte dinamico (B-06)`
- `6864dc4` `fix(engine): obligatorias, longest path e hito de inicio (B-08, B-09, B-21)`

B-08, B-09 y B-21 comparten `schedule_cpm`. Fueron un solo commit para que la revisión quede en verde. El índice de calendario va aparte.

## Qué cambió

- `WorkCalendar.add_work`, `subtract_work` y `work_between` usan minutos laborales acumulados desde el lunes `0001-01-01`, con el delta de cada excepción en un prefijo. La fecha se busca en binario sobre ese índice. No hay bucle día por día ni tope de 3.660 días. Si el calendario no tiene tiempo laboral, sigue `CalendarLimitError` con el texto `horizonte`.
- `EngineOptions.critical_rule`: `float` (default, holgura total ≤ `critical_hours`) o `longest`. En longest, es crítica la actividad cuyo fin temprano es el fin del proyecto, o la que la conduce por un vínculo cuyo límite coincide con el inicio temprano (un `TT_Mile` puede haber corrido ese límite al siguiente inicio). Se calcula antes de ALAP. LOE y WBS no son críticas. `critical_hours` no se usa en modo longest.
- `CS_MANDSTART` y `CS_MANDFIN` fijan la fecha en el pase adelante y en el pase atrás, aunque quede antes que la red. No se tratan como `CS_MSO` / `CS_MEO`, que solo atrasan. La violación entra en `approximations`. La fecha impuesta es el minuto de la restricción, sin inventar un campo XER.
- `TT_Mile` cuyo instante cae al cierre (o fuera de la jornada) pasa al siguiente inicio laboral (`add_work(..., 0)`). `TT_FinMile` se queda en el cierre. Fechas reales de una actividad ya iniciada no se mueven.

`test_cpm.py::test_milestones_can_sit_on_the_shift_end` no se tocó: el hito de inicio de ese caso nace a las 08:00 y el de fin sigue a las 16:00. Ningún test verde esperaba un `TT_Mile` sentado a las 16:00. Un turno `00:00–24:00` que sumaba un día exacto antes lanzaba `ValueError` (hora 24); ahora cae en la medianoche siguiente. No había un test verde de ese caso.

La parte de calendario de B-14 (feriado, media jornada, 24 h, 7 días, día hábil) está cubierta por `tests/test_e1_calendar.py` y por los XER temporales de los otros tests E1. No se escribió fixture bajo `tests/fixtures/` ni se tocó el generador: eso no es de este agente.

Semántica nueva en `docs/XER_SPEC.md`, marcada `[VALIDAR]`. No se inventaron columnas.

## Rojo, antes del arreglo

`docs/qa/E1/rojo-motor.md`. Misma selección de pytest, 8 failed, 21 passed. El tope de 3.660 días seguía en `add_work` y `work_between`; la hora 24 reventaba; `CS_MANDSTART` dejaba el inicio el martes 12:00; `CS_MANDFIN` dejaba el fin el martes 16:00; `critical_rule` no existía; el hito de inicio quedaba a las 16:00.

## Comandos y resultados

En el worktree, con el `.venv` de esa copia (el editable del checkout principal sigue en `AtlasPMO`):

```
py -3.12 -m uv run python -m pytest -q tests/test_calendars.py tests/test_cpm.py tests/test_e1_calendar.py tests/test_e1_constraints.py tests/test_e1_longest.py tests/test_e1_milestone.py --tb=line
```

29 passed in 0.59s.

```
py -3.12 -m uv run python -m ruff check src/atlaspmo/calendars src/atlaspmo/engine tests/test_e1_calendar.py tests/test_e1_constraints.py tests/test_e1_longest.py tests/test_e1_milestone.py
```

All checks passed. `ruff format --check` sobre esos mismos paths también quedó limpio.

```
py -3.12 -m uv run python -m mypy src
```

Success: no issues found in 56 source files.

Extra, no pedido en el brief: `py -3.12 -m uv run python -m pytest -q --tb=line` → 139 passed in 30.53s. No se corrió `scripts/qa_gate.py`.

## No verificado

- Nada de esto está contrastado con P6. `p6_verified` no existe en el repo y no se leyó `data/real` ni `ATLASPMO_GOLDEN_DIR`. Obligatorio, hito de inicio y longest path quedan `[VALIDAR]`.
- No hay conformidad anonimizada contra un golden. `engine/conformance.py` no se modificó; sigue llamando a `schedule_cpm`.
- No se usó numba.
- No se midió un microbenchmark aparte del tramo de 20 años dentro de pytest (la selección completa tardó menos de un segundo).
- B-14 de generadores, tablas `SYNTH` y esperados con doble firma no se hizo aquí.
- Avance (retained / override / actual dates) no cambió de regla; `test_cpm.py` sigue verde, pero no hay un caso nuevo de avance fuera de secuencia.
