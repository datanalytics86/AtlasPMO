# qa-spec — E7 ciclo 2

Auditoría de QC-1 de R-360, R-361, R-362, R-363 y R-364, y de si el ciclo 2 sigue cubriéndolos. HEAD `6052e9b` (`6052e9b4401f6c8c360d6038e8f0fe8070336dc6`), rama `v3`. Se contrastaron `docs/qa/TRAZABILIDAD.md`, `docs/qa/E7/QC1_contrato.md`, la sección 10.3 de `docs/MEGAPROMPT_v3.md` y los tests citados. El diff del ciclo 2 que toca tests es `de37f8a`: segundos en el inicio `TK_Active` de `tests/property/test_e7_differential.py` y `test_actual_seconds_do_not_widen_the_longest_path_or_driving` en `tests/test_e7_match.py`. No se reescribieron el contrato ni la trazabilidad. No se editó código de producto ni tests. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se reejecutó pytest ni la red de 30 000. Este informe no afirma un verde propio de la suite.

## Veredicto

**PASA.** R-360, R-361, R-362, R-363 y R-364 siguen con criterio ejecutable y fuente de oráculo. El ciclo 2 no les quita esa fuente. No corresponde severidad.

## R-360

**PASA.**

Criterio de la fila: ES, EF, LS, LF, TF, FF y aproximaciones idénticos al minuto frente a la referencia. El archivo citado es `tests/property/test_e7_differential.py`. El oráculo de la fila es `schedule_cpm_reference`, hypothesis con 500 ejemplos y el perfil `qa`.

Criterio del contrato, que es el que se audita: hypothesis, 500 ejemplos, deriva fija; ES, EF, LS, LF, TF y FF al minuto; la misma lista de aproximaciones; el mismo crítico; el mismo orden de predecesoras conductoras. La conformidad contra P6 no deja el requisito en verde.

El test citado compara eso. `test_fast_matches_reference_to_the_minute` fija `@settings(max_examples=500, deadline=None, derandomize=True)`. `tests/property/conftest.py` registra el perfil `qa` con esos tres valores y lo carga. `derandomize=True` es la deriva fija. Por actividad, el lado rápido se contrasta con el lado referencia así: ES, EF, LS y LF truncados al minuto; TF y FF por `round(horas * 60)`; `approximations` con igualdad de tupla; `critical` igual; `driving_pred_ids` con igualdad de tupla, así que el orden cuenta. También compara `skipped`, el término del proyecto al minuto y el conjunto de ids. Si el inicio temprano de la referencia trae segundos o microsegundos, además exige el mismo `datetime` de inicio y fin tempranos, no solo el minuto. Eso no reemplaza el corte al minuto de LS y LF, que es lo que el contrato pide.

El oráculo no es el motor rápido. El lado esperado es `schedule_cpm(schedule, replace(options, engine="reference"))`. En `src/atlaspmo/engine/cpm.py`, `engine == "reference"` retorna `schedule_cpm_reference` y no importa el motor rápido. Esa función no llama a `schedule_cpm` ni a `schedule_cpm_fast`. El otro lado es una llamada distinta, con `engine="fast"`. `schedule_cpm_fast` solo vuelve a `schedule_cpm_reference` si el calendario es `UnsupportedCalendar`. Los calendarios del generador tienen un turno por día. El solape, que sí cae a la referencia, está en R-362 y no es este sorteo.

El ciclo 2 cubre el borde que el diferencial del ciclo 1 no generaba. Antes, el inicio real de `TK_Active` se armaba en el minuto `08:00` sin segundos. Ahora `second` sale de `(0, 45)` y entra en `act_start`. El fin real de una `TK_Complete` ya salía con 0 o 45 s y no cambió. Con eso, el mismo crítico, el mismo orden de conductoras y, cuando el inicio temprano conserva segundos, la igualdad de `datetime` del inicio y del fin tempranos quedan dentro del soporte de los 500 ejemplos. No corrí hypothesis: no afirmo que la semilla fija haya sorteado un empate concreto.

El empate que el ciclo 1 reprodujo a mano no queda solo en ese sorteo. Lo ejecuta siempre `tests/test_e7_match.py::test_actual_seconds_do_not_widen_the_longest_path_or_driving`, contra el mismo oráculo. El detalle está en R-362. Ese archivo no sustituye al diferencial: R-360 sigue citando hypothesis.

La sección 10.3 pide, en el generador, varios calendarios (feriado, media jornada, 24 h, 7 días), los cuatro vínculos, lags positivos y negativos, cada restricción, avance fuera de secuencia, hitos, LOE y WBS. El criterio del contrato no enumera ese dominio. La estrategia `_nets` sigue sorteándolo, igual que en el ciclo 1, y ahora con segundos en el inicio en curso.

## R-361

**PASA.**

Criterio de la fila: tablas de intervalos iguales a `WorkCalendar`. El test es `tests/test_e7_intervals.py`. El oráculo es `add_work`, `subtract_work` y `work_between`.

Criterio del contrato: esa reproducción en snap de 0 minutos, fin de semana, feriado, media jornada y jornada de 24 h. Un calendario con turnos solapados dentro de numba no deja el requisito en verde.

El ciclo 2 no tocó este archivo. Sigue siendo ejecutable y el oráculo sigue siendo el reloj, no un esperado inventado. Los cinco casos están: `test_zero_minute_snaps_forward_and_backward`, `test_weekend_gap_and_full_shift`, `test_holiday_is_not_work_and_half_day_stays_at_noon`, `test_full_day_shift_moves_twenty_four_hours`. `work_between` se afirma en fin de semana y en la jornada de 24 h. En feriado y media jornada el contraste de la tabla es `add_work` y `subtract_work`. El criterio no exige las tres operaciones en cada escenario. `test_seven_day_calendar_matches_a_grid_of_moves` suma el calendario de 7 días que la 10.3 pide en el generador.

El solape no es un caso de éxito de esta fila. `build_tables` levanta `UnsupportedCalendar` si un turno pisa al anterior. Ese calendario no se tabula dentro de numba. La caída a la referencia está en R-362.

## R-362

**PASA.**

Criterio de la fila: camino rápido, ALAP antes de la holgura libre, restricciones, avance, hitos, LOE, WBS, horizonte y turno solapado. El test es `tests/test_e7_match.py`. El oráculo de la fila es `schedule_cpm_reference`.

Criterio del contrato: el camino de semana usa `path=fast`; la holgura libre ve a la sucesora después de ALAP; el solape cae a la referencia sin nota nueva; el horizonte corto crece; el horizonte agotado nombra el límite. Que toda red de 30 000 quepa en 0,5 s antes de medirla no deja esta fila en verde. El tiempo está en R-364.

El ciclo 2 no borra esas cláusulas. Cada una sigue con caso y oráculo en el mismo archivo:

| Cláusula del contrato | Test | Oráculo |
|---|---|---|
| El camino de semana usa `path=fast` | `test_weekday_chain_uses_the_fast_path` | fechas contra la referencia y `LAST["path"] == "fast"` |
| La holgura libre ve a la sucesora después de ALAP | `test_free_float_sees_the_successor_after_alap` | la referencia en la red fija (A, B con `CS_ALAP` y lag −8, C). `_same` incluye la holgura libre |
| El solape cae a la referencia sin nota nueva | `test_overlapping_shifts_fall_back_without_an_extra_note` | mismas `approximations`, mismo early finish, `LAST["path"] == "reference"` |
| El horizonte corto crece | `test_short_horizon_grows_and_still_matches` | la referencia, con `path=fast`, al forzar `horizon_days` a 1 |
| El horizonte agotado nombra el límite | `test_exhausted_horizon_names_the_limit` | `CalendarLimitError` con el texto `horizonte de calendario agotado` |

`_same` obtiene el esperado con `schedule_cpm(..., engine="reference")`, que es `schedule_cpm_reference`, y el sujeto con `engine="fast"`. Compara el `datetime` completo de ES, EF, LS, LF y del término, no el minuto truncado, y además TF, FF, `critical`, el orden de `driving_pred_ids` y `approximations`.

El ciclo 2 agrega `test_actual_seconds_do_not_widen_the_longest_path_or_driving`, dos redes fijas, las dos por `_same`:

1. A completa con fin real `2026-01-05 16:00:45` y B de 8 h sin vínculos, `critical_rule="longest"`.
2. Hito con `CS_MSO` a las 16:00 del `2026-01-05` y sucesora `TK_Active` con inicio real `2026-01-06 08:00:45`, `PR_SS` y lag 0. La llamada usa `EngineOptions()`: el avance queda en `retained` y el crítico en `float`, que son los defectos.

El calendario de las dos es el de un turno `08:00–16:00`, no el solapado. No es el caso que `schedule_cpm_fast` devuelve llamando a la referencia. El test nuevo no afirma `LAST["path"]`. No hace falta para el oráculo: el lado esperado no entra al motor rápido. El camino de semana sigue afirmando `path=fast` en su propio test.

El parche de `horizon_days` sigue llegando al motor: `_ensure` lo resuelve en `atlaspmo.engine.fast`. La afirmación `horizon_days(100, 10) == 24` usa el nombre ya importado en el test, así que comprueba la fórmula real (`max(21, minutos / jornada + 14)`), no el parche. Con lag 0, `lag_days` queda en 2 y la primera ventana es el 2026-01-05 ± 2 días. La cadena de 40 h + 40 h en calendario de 8 h no cabe ahí. Si el horizonte no creciera, el caso no coincidiría con la referencia ni mantendría `path=fast`. El criterio se puede fallar.

Restricciones, avance, hitos, LOE y WBS no están en la frase corta del contrato y sí en la fila. No quedan sin oráculo: `test_constraints_progress_milestones_and_rollup_match` los corre contra la referencia en los tres avances, las dos reglas de crítico y los tres tipos de holgura. Los tests de mano de R-363 los vuelven a exigir con fechas calculadas a mano.

## R-363

**PASA.**

Criterio de la fila: los tests de mano del motor siguen pasando con el motor rápido por defecto. Cita `tests/test_cpm.py`. El oráculo son los casos a mano de CPM.

Criterio del contrato: `tests/test_cpm.py` y los de restricciones, longest path e hitos corren con el motor rápido por defecto. Borrar la referencia no deja el requisito en verde. `schedule_cpm_reference` sigue en `src/atlaspmo/engine/cpm.py`.

El ciclo 2 no tocó estos archivos. Sigue siendo ejecutable. El defecto de `EngineOptions.engine` es `"fast"`. `schedule_cpm` solo entra a la referencia si `engine="reference"`. No hay `conftest` que cambie el motor. Estos archivos no pasan `engine="reference"`:

- `tests/test_cpm.py`. Las dos `EngineOptions` fijan solo `progress` (`progress_override` y `actual_dates`). El resto llama `schedule_cpm(schedule)`.
- `tests/test_e1_constraints.py`. Tres casos a mano, `schedule_cpm(schedule)`.
- `tests/test_e1_longest.py`. `EngineOptions(critical_rule="longest")` no toca `engine`.
- `tests/test_e1_milestone.py`. Tres casos a mano, `schedule_cpm(schedule)`.

El oráculo son las fechas y notas escritas en esos tests, no la salida del propio motor rápido. La sección 10.3 pide que los tests existentes del motor pasen con el rápido. Esa lectura, alineada con la fila, es este conjunto. Otros llamadores tampoco fijan `engine="reference"` y heredan el mismo defecto. No son el oráculo a mano del CPM y el contrato no los necesita para que el criterio sea ejecutable.

## R-364

**PASA.**

Criterio de la fila: `cpm_30k` y `dcma_30k` medidos a 30 000, y activarlos solo si cumplen. El test es `tests/perf/test_seccion11.py`. El oráculo es `gen_scale.py` en este equipo.

Criterio del contrato: `test_s11_cpm_30k` y `test_s11_dcma_30k` se miden a 30 000 y entran en `seccion11.toml` solo si quedan bajo 0,5 s y 10 s. Copiar los tiempos de la revisión en Linux no los deja en verde.

El ciclo 2 no tocó el test ni `docs/qa/seccion11.toml`. Sigue siendo ejecutable. `SIZE` sale de `ATLASPMO_S11_SIZE` y por defecto es 30 000. `FULL` exige el límite solo en ese tamaño. `test_s11_cpm_30k` calienta y luego exige menos de 0,5 s. `test_s11_dcma_30k` exige menos de 10 s. Ambos arman la red con `write_scale` de `scripts/gen_scale.py`. La red no es un XER real. Por debajo de 30 000 el test imprime el tiempo y no exige la meta. La medición que el criterio nombra es la corrida a 30 000.

No reejecuté esa corrida. No confirmo ni desmiento los tiempos de `docs/qa/E7/perf.md`. En el árbol, `activas` de `docs/qa/seccion11.toml` incluye `cpm_30k` y `dcma_30k`. El gate del orquestador, que no repetí, registra G6 en pass para esas metas activas (`docs/qa/E7/gate.json`, `exit_code` 0, `test_count` 237, escrito en `de37f8a` y presente en este HEAD). La regla sigue teniendo oráculo: el reloj de esos dos tests sobre `gen_scale.py` en este equipo. No es el cuadro de Linux de la sección 8.3.

## Sección 10.3

| Exigencia | Dónde queda ejecutable | Oráculo |
|---|---|---|
| Hypothesis al minuto: ES, EF, LS, LF, TF, FF, la misma lista de aproximaciones, el mismo crítico y el mismo orden de conductoras | R-360, `tests/property/test_e7_differential.py` | `schedule_cpm_reference` |
| Esas redes cubren calendarios, vínculos, lags, restricciones, avance, hitos, LOE y WBS, y ahora segundos 0 o 45 en el inicio `TK_Active` | el mismo test, en la estrategia `_nets` | el mismo |
| Los dos reales con segundos del ciclo 1, con igualdad de `datetime` y no solo del minuto | R-362, `test_actual_seconds_do_not_widen_the_longest_path_or_driving` | el mismo |
| Los tests existentes del motor pasan con el rápido | R-363; defecto `engine="fast"` y los cuatro archivos de mano | casos a mano |
| `cpm_30k` &lt; 0,5 s y `dcma_30k` &lt; 10 s, solo si se miden a 30 000 | R-364 | `gen_scale.py` en este equipo |

## Comandos

`git rev-parse HEAD` → `6052e9b4401f6c8c360d6038e8f0fe8070336dc6`. Rama `v3`. Se leyó el diff de tests de `de37f8a` con `git show`. No hubo pytest, gate ni medición de la sección 11.
