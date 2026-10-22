# qa-spec — E7 ciclo 3

Auditoría de QC-1 de R-360, R-361, R-362, R-363 y R-364, y de si el ciclo 3 sigue cubriéndolos. HEAD `577c6ba` (`577c6ba3a1bad4729ee139bb6709033ed9f9954e`), rama `v3`. Se contrastaron `docs/qa/TRAZABILIDAD.md`, `docs/qa/E7/QC1_contrato.md`, la sección 10.3 de `docs/MEGAPROMPT_v3.md` y los tests citados. El diff del ciclo 3 que toca tests es `577c6ba`: `tests/property/test_e7_differential.py` sortea `act_start` con segundos también en `TK_NotStart`, y `tests/test_e7_match.py` suma `test_not_started_actual_does_not_erase_driving` y `test_project_finish_seconds_survive_a_constraint_that_does_not_bind`. No se reescribieron el contrato ni la trazabilidad. No se editó código de producto ni tests. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se reejecutó pytest ni la red de 30 000. Este informe no afirma un verde propio de la suite.

## Veredicto

**PASA.** R-360, R-361, R-362, R-363 y R-364 siguen con criterio ejecutable y fuente de oráculo. El ciclo 3 no les quita esa fuente. El oráculo de los dos tests nuevos y del diferencial sigue siendo `schedule_cpm_reference` (`engine="reference"`), no el motor rápido. No corresponde severidad.

## R-360

**PASA.**

Criterio de la fila: ES, EF, LS, LF, TF, FF y aproximaciones idénticos al minuto frente a la referencia. El archivo citado sigue siendo `tests/property/test_e7_differential.py`. El oráculo de la fila es `schedule_cpm_reference`, hypothesis con 500 ejemplos y el perfil `qa`. La fila no cambió en este ciclo.

Criterio del contrato, que es el que se audita: hypothesis, 500 ejemplos, deriva fija; ES, EF, LS, LF, TF y FF al minuto; la misma lista de aproximaciones; el mismo crítico; el mismo orden de predecesoras conductoras. La conformidad contra P6 no deja el requisito en verde.

El test citado compara eso. `test_fast_matches_reference_to_the_minute` fija `@settings(max_examples=500, deadline=None, derandomize=True)`. `tests/property/conftest.py` registra el perfil `qa` con esos tres valores y lo carga. `derandomize=True` es la deriva fija. Por actividad, el lado rápido se contrasta con el lado referencia así: ES, EF, LS y LF truncados al minuto; TF y FF por `round(horas * 60)`; `approximations` con igualdad de tupla; `critical` igual; `driving_pred_ids` con igualdad de tupla, así que el orden cuenta. También compara `skipped`, el término del proyecto al minuto y el conjunto de ids. Si el inicio temprano de la referencia trae segundos o microsegundos, además exige el mismo `datetime` de inicio y fin tempranos, no solo el minuto. Eso no reemplaza el corte al minuto de LS y LF, que es lo que el contrato pide. El corte al minuto no ve un segundo que solo tenga el lado rápido: si la referencia queda en `:00` y el rápido en `:45`, el `datetime` completo de ese inicio no se exige aquí. El orden de conductoras y el crítico sí. La igualdad de `datetime` del fin de proyecto, cuando la restricción no mueve, está en R-362.

El oráculo no es el motor rápido. El lado esperado es `schedule_cpm(schedule, replace(options, engine="reference"))`. En `src/atlaspmo/engine/cpm.py`, `engine == "reference"` retorna `schedule_cpm_reference` y no importa el motor rápido. Esa función no llama a `schedule_cpm` ni a `schedule_cpm_fast`. El real de inicio solo entra al pase si el estado es `TK_Active` o `TK_Complete`. El otro lado es una llamada distinta, con `engine="fast"`. `schedule_cpm_fast` solo vuelve a `schedule_cpm_reference` si el calendario es `UnsupportedCalendar`. Los calendarios del generador tienen un turno por día, incluida la jornada `00:00`–`00:00` leída como 24 h, que la tabla admite porque el fin del turno no pasa de `DAY`. El solape, que sí cae a la referencia, está en R-362 y no es este sorteo.

El ciclo 3 cubre el borde que el diferencial no generaba. Antes, `act_start` solo salía en `TK_Active` y en `TK_Complete`. Ahora, si el estado es `TK_NotStart` y un booleano sale verdadero, `second` sale de `(0, 45)` y entra en `act_start` el día `2026-01-05` a `2026-01-12` a las `08:00`. LOE y WBS se fuerzan a `TK_NotStart` antes de ese sorteo, así que también pueden traer ese real. El inicio de `TK_Active` y el fin real de `TK_Complete` no cambiaron. Con eso, el mismo crítico y el mismo orden de conductoras quedan dentro del soporte de los 500 ejemplos también cuando hay un real en una no iniciada. No corrí hypothesis: no afirmo que la semilla fija haya sorteado el empate del minuto.

Ese empate no queda solo en el sorteo. Lo ejecuta siempre `tests/test_e7_match.py::test_not_started_actual_does_not_erase_driving`, contra el mismo oráculo y con igualdad de `datetime`, no solo del minuto. El detalle está en R-362. Ese archivo no sustituye al diferencial: R-360 sigue citando hypothesis.

La sección 10.3 pide, en el generador, varios calendarios (feriado, media jornada, 24 h, 7 días), los cuatro vínculos, lags positivos y negativos, cada restricción, avance fuera de secuencia, hitos, LOE y WBS. El criterio del contrato no enumera ese dominio. La estrategia `_nets` sigue sorteándolo, igual que en el ciclo 2, y ahora con segundos en el real de una no iniciada.

## R-361

**PASA.**

Criterio de la fila: tablas de intervalos iguales a `WorkCalendar`. El test es `tests/test_e7_intervals.py`. El oráculo es `add_work`, `subtract_work` y `work_between`.

Criterio del contrato: esa reproducción en snap de 0 minutos, fin de semana, feriado, media jornada y jornada de 24 h. Un calendario con turnos solapados dentro de numba no deja el requisito en verde.

El ciclo 3 no tocó este archivo. Sigue siendo ejecutable y el oráculo sigue siendo el reloj, no un esperado inventado. Los cinco casos están: `test_zero_minute_snaps_forward_and_backward`, `test_weekend_gap_and_full_shift`, `test_holiday_is_not_work_and_half_day_stays_at_noon`, `test_full_day_shift_moves_twenty_four_hours`. `work_between` se afirma en fin de semana y en la jornada de 24 h. En feriado y media jornada el contraste de la tabla es `add_work` y `subtract_work`. El criterio no exige las tres operaciones en cada escenario. `test_seven_day_calendar_matches_a_grid_of_moves` suma el calendario de 7 días que la 10.3 pide en el generador.

El solape no es un caso de éxito de esta fila. `build_tables` levanta `UnsupportedCalendar` si un turno pisa al anterior o se sale del día. Ese calendario no se tabula dentro de numba. La caída a la referencia está en R-362.

## R-362

**PASA.**

Criterio de la fila: camino rápido, ALAP antes de la holgura libre, restricciones, avance, hitos, LOE, WBS, horizonte y turno solapado. El test es `tests/test_e7_match.py`. El oráculo de la fila es `schedule_cpm_reference`.

Criterio del contrato: el camino de semana usa `path=fast`; la holgura libre ve a la sucesora después de ALAP; el solape cae a la referencia sin nota nueva; el horizonte corto crece; el horizonte agotado nombra el límite. Que toda red de 30 000 quepa en 0,5 s antes de medirla no deja esta fila en verde. El tiempo está en R-364.

El ciclo 3 no borra esas cláusulas. Cada una sigue con caso y oráculo en el mismo archivo:

| Cláusula del contrato | Test | Oráculo |
|---|---|---|
| El camino de semana usa `path=fast` | `test_weekday_chain_uses_the_fast_path` | fechas contra la referencia y `LAST["path"] == "fast"` |
| La holgura libre ve a la sucesora después de ALAP | `test_free_float_sees_the_successor_after_alap` | la referencia en la red fija (A, B con `CS_ALAP` y lag −8, C). `_same` incluye la holgura libre |
| El solape cae a la referencia sin nota nueva | `test_overlapping_shifts_fall_back_without_an_extra_note` | mismas `approximations`, mismo early finish, `LAST["path"] == "reference"` |
| El horizonte corto crece | `test_short_horizon_grows_and_still_matches` | la referencia, con `path=fast`, al forzar `horizon_days` a 1 |
| El horizonte agotado nombra el límite | `test_exhausted_horizon_names_the_limit` | `CalendarLimitError` con el texto `horizonte de calendario agotado` |

`_same` obtiene el esperado con `schedule_cpm(..., engine="reference")`, que es `schedule_cpm_reference`, y el sujeto con `engine="fast"`. Compara el `datetime` completo de ES, EF, LS, LF y del término, no el minuto truncado, y además TF, FF, `critical`, el orden de `driving_pred_ids` y `approximations`. El lado esperado no entra al motor rápido: el `return` de `engine == "reference"` ocurre antes del import de `schedule_cpm_fast`.

El ciclo 3 agrega dos tests. Los dos pasan por `_same`. El calendario es el de un turno `08:00`–`16:00` los siete días, no el solapado. No es el caso que `schedule_cpm_fast` devuelve llamando a la referencia. Ninguno de los dos afirma `LAST["path"]`. No hace falta para el oráculo. El camino de semana sigue afirmando `path=fast` en su propio test.

`test_not_started_actual_does_not_erase_driving` arma el real que el diferencial ahora también sortea, y lo exige siempre:

1. P de 8 h sin real y B de 8 h en `TK_NotStart` (el defecto de `_activity`) con `act_start` `2026-01-06 08:00:45`, `PR_FS` y lag 0. Una llamada con `critical_rule="longest"` y otra con `EngineOptions()`, o sea `float` y `retained`.
2. El mismo vínculo con B hito de inicio (`TT_Mile`, 0 h, el mismo real y el mismo estado no iniciado), solo con `longest`.

La igualdad incluye el orden de conductoras, el crítico y el `datetime` del inicio temprano. Si el rápido borrara la predecesora o publicara el real de una no iniciada, `_same` falla. El test no fija a mano la tupla `('P',)`: la tupla esperada sale de la referencia.

`test_project_finish_seconds_survive_a_constraint_that_does_not_bind` exige igualdad de `datetime` del término, y del resto de fechas, contra esa misma referencia. No trunca al minuto. Los casos son una completa con fin real `2026-01-05 16:00:45` y una B de 8 h sin vínculos, con `CS_MEOB` al `2026-01-08 16:00`, con `CS_MSOA` al `2026-01-05 08:00`, con `CS_MSO` sin fecha, y con `CS_ALAP` más `CS_MSOA` al `2026-01-05 08:00`. El quinto caso cambia el fin real a `2026-01-05 15:30:45` y pone un hito de inicio no iniciado, sin restricción ni vínculos. No están como llamada propia el par `CS_ALAP` más `CS_MSO` sin fecha, ni el hito de inicio con `CS_ALAP`. No hace falta para el criterio del contrato: las cinco cláusulas de arriba siguen, y estos cinco `_same` ya pueden fallar si el término o el fin tarde pierden o ganan el segundo frente a la referencia.

El parche de `horizon_days` sigue llegando al motor: `_ensure` lo resuelve en `atlaspmo.engine.fast`. La afirmación `horizon_days(100, 10) == 24` usa el nombre ya importado en el test, así que comprueba la fórmula real (`max(21, minutos / jornada + 14)`), no el parche. Con lag 0, `lag_days` queda en 2 y la primera ventana es el 2026-01-05 ± 2 días. La cadena de 40 h + 40 h en calendario de 8 h no cabe ahí. Si el horizonte no creciera, el caso no coincidiría con la referencia ni mantendría `path=fast`. El criterio se puede fallar.

Restricciones, avance, hitos, LOE y WBS no están en la frase corta del contrato y sí en la fila. No quedan sin oráculo: `test_constraints_progress_milestones_and_rollup_match` los corre contra la referencia en los tres avances, las dos reglas de crítico y los tres tipos de holgura. Los tests de mano de R-363 los vuelven a exigir con fechas calculadas a mano.

## R-363

**PASA.**

Criterio de la fila: los tests de mano del motor siguen pasando con el motor rápido por defecto. Cita `tests/test_cpm.py`. El oráculo son los casos a mano de CPM.

Criterio del contrato: `tests/test_cpm.py` y los de restricciones, longest path e hitos corren con el motor rápido por defecto. Borrar la referencia no deja el requisito en verde. `schedule_cpm_reference` sigue en `src/atlaspmo/engine/cpm.py`. El ciclo 3 no la tocó: el diff de producto es solo `src/atlaspmo/engine/fast.py`.

El ciclo 3 no tocó estos archivos. Sigue siendo ejecutable. El defecto de `EngineOptions.engine` es `"fast"`. `schedule_cpm` solo entra a la referencia si `engine="reference"`. No hay `conftest` que cambie el motor. Estos archivos no pasan `engine="reference"`:

- `tests/test_cpm.py`. Las dos `EngineOptions` fijan solo `progress` (`progress_override` y `actual_dates`). El resto llama `schedule_cpm(schedule)`.
- `tests/test_e1_constraints.py`. Tres casos a mano, `schedule_cpm(schedule)`.
- `tests/test_e1_longest.py`. `EngineOptions(critical_rule="longest")` no toca `engine`.
- `tests/test_e1_milestone.py`. Tres casos a mano, `schedule_cpm(schedule)`.

El oráculo son las fechas y notas escritas en esos tests, no la salida del propio motor rápido. La sección 10.3 pide que los tests existentes del motor pasen con el rápido. Esa lectura, alineada con la fila, es este conjunto. Otros llamadores tampoco fijan `engine="reference"` y heredan el mismo defecto. No son el oráculo a mano del CPM y el contrato no los necesita para que el criterio sea ejecutable.

## R-364

**PASA.**

Criterio de la fila: `cpm_30k` y `dcma_30k` medidos a 30 000, y activarlos solo si cumplen. El test es `tests/perf/test_seccion11.py`. El oráculo es `gen_scale.py` en este equipo.

Criterio del contrato: `test_s11_cpm_30k` y `test_s11_dcma_30k` se miden a 30 000 y entran en `seccion11.toml` solo si quedan bajo 0,5 s y 10 s. Copiar los tiempos de la revisión en Linux no los deja en verde.

El ciclo 3 no tocó el test ni `docs/qa/seccion11.toml`. Sigue siendo ejecutable. `SIZE` sale de `ATLASPMO_S11_SIZE` y por defecto es 30 000. `FULL` exige el límite solo en ese tamaño. `test_s11_cpm_30k` calienta y luego exige menos de 0,5 s. `test_s11_dcma_30k` exige menos de 10 s. Ambos arman la red con `write_scale` de `scripts/gen_scale.py`. La red no es un XER real. Por debajo de 30 000 el test imprime el tiempo y no exige la meta. La medición que el criterio nombra es la corrida a 30 000.

No reejecuté esa corrida. No confirmo ni desmiento los tiempos de `docs/qa/E7/perf.md`. En el árbol, `activas` de `docs/qa/seccion11.toml` incluye `cpm_30k` y `dcma_30k`. El gate del orquestador, que no repetí, está en este HEAD: `docs/qa/E7/gate.json` del commit `577c6ba`, `exit_code` 0, `test_count` 239, G6 en pass para `activas` `lectura_30k`, `cpm_30k` y `dcma_30k` (3 passed). El detalle de G6 no trae la línea `n=30000`. La regla sigue teniendo oráculo: el reloj de esos dos tests sobre `gen_scale.py` en este equipo, con el límite solo si `SIZE` es 30 000. No es el cuadro de Linux de la sección 8.3.

## Sección 10.3

| Exigencia | Dónde queda ejecutable | Oráculo |
|---|---|---|
| Hypothesis al minuto: ES, EF, LS, LF, TF, FF, la misma lista de aproximaciones, el mismo crítico y el mismo orden de conductoras | R-360, `tests/property/test_e7_differential.py` | `schedule_cpm_reference` |
| Esas redes cubren calendarios, vínculos, lags, restricciones, avance, hitos, LOE y WBS, y segundos 0 o 45 en el inicio `TK_Active` y, desde este ciclo, en `TK_NotStart` | el mismo test, en la estrategia `_nets` | el mismo |
| Real no iniciado con segundos: conductoras, crítico y `datetime`, en tarea (`longest` y `float`) y en hito de inicio (`longest`) | R-362, `test_not_started_actual_does_not_erase_driving` | el mismo, vía `engine="reference"` |
| Segundos del término cuando la restricción no gana, y del hito de inicio no iniciado, con igualdad de `datetime` | R-362, `test_project_finish_seconds_survive_a_constraint_that_does_not_bind` | el mismo |
| Los tests existentes del motor pasan con el rápido | R-363; defecto `engine="fast"` y los cuatro archivos de mano | casos a mano |
| `cpm_30k` &lt; 0,5 s y `dcma_30k` &lt; 10 s, solo si se miden a 30 000 | R-364 | `gen_scale.py` en este equipo |

## Comandos

`git rev-parse HEAD` → `577c6ba3a1bad4729ee139bb6709033ed9f9954e`. Rama `v3`. Se leyó el diff de tests y del gate de `577c6ba` con `git show`. No hubo pytest, gate ni medición de la sección 11.
