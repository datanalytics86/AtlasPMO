# qa-spec — E7

Auditoría de QC-1 de R-360, R-361, R-362, R-363 y R-364. HEAD `73666eb` (`73666ebeddad0db948c2f53b978b3f78ebbf7bee`), rama `v3`. Se contrastaron `docs/qa/TRAZABILIDAD.md`, `docs/qa/E7/QC1_contrato.md`, la sección 10.3 de `docs/MEGAPROMPT_v3.md` y los tests citados. No se editó el contrato, la trazabilidad ni código. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se reejecutó pytest ni la medición de 30 000. Este informe no afirma que la suite esté en verde y no reproduce como propios los tiempos de `docs/qa/E7/perf.md`.

## Veredicto

**PASA.** R-360, R-361, R-362, R-363 y R-364 tienen criterio ejecutable y fuente de oráculo. Los tests citados implementan esos criterios. No corresponde severidad.

La sección 10.3 queda cubierta en lo que se pidió auditar: diferencial hypothesis al minuto de ES, EF, LS, LF, TF, FF y aproximaciones contra el motor de referencia, y los tests de mano del motor corriendo con el rápido por defecto.

## R-360

La fila pide ES, EF, LS, LF, TF, FF y aproximaciones idénticos al minuto frente a la referencia. El test es `tests/property/test_e7_differential.py`. El oráculo de la fila es `schedule_cpm_reference`, hypothesis con 500 ejemplos y el perfil `qa`.

El contrato pide lo mismo y, además, el mismo crítico y el mismo orden de predecesoras conductoras, con 500 ejemplos y deriva fija. La conformidad contra P6 no deja el requisito en verde.

Es ejecutable. `test_fast_matches_reference_to_the_minute` fija `@settings(max_examples=500, deadline=None, derandomize=True)`. `tests/property/conftest.py` registra el perfil `qa` con esos mismos tres valores y lo carga. `derandomize=True` es la deriva fija.

El oráculo existe. `schedule_cpm` con `engine="reference"` llama a `schedule_cpm_reference` en `src/atlaspmo/engine/cpm.py`. El test corre esa vía y `engine="fast"`. No usa un cronograma real ni P6.

El test afirma, por actividad, ES, EF, LS y LF truncados al minuto; TF y FF por `round(horas * 60)`; la misma tupla de `approximations`; `critical` igual; y `driving_pred_ids` igual, de modo que el orden cuenta. También compara `skipped`, el término del proyecto al minuto y el conjunto de ids.

La sección 10.3 pide que el generador traiga varios calendarios (feriado, media jornada, 24 h, 7 días), los cuatro vínculos, lags positivos y negativos, cada restricción, avance fuera de secuencia, hitos, LOE y WBS. El criterio del contrato no enumera ese dominio. El test citado sí lo sortea: dos calendarios, feriado opcional, media jornada, `00:00–00:00` (el parser lo lee como jornada de 24 h) y semana de 7 días; `PR_FS`, `PR_SS`, `PR_FF` y `PR_SF`, más un `PR_OTHER` ocasional; lags en `{-8, -1, 0, 4, 8}`; cada tipo de `_CSTR`, incluida `CS_ALAP`; `retained`, `progress_override` y `actual_dates`, con actividades en curso o terminadas que pueden quedar fuera de secuencia; hitos, LOE y WBS. El soporte de la estrategia alcanza para ejecutar esa frase. No queda un requisito sin oráculo: el oráculo sigue siendo el motor de referencia.

## R-361

La fila pide tablas de intervalos iguales a `WorkCalendar`. El test es `tests/test_e7_intervals.py`. El oráculo es `add_work`, `subtract_work` y `work_between`.

El contrato pide esa reproducción en snap de 0 minutos, fin de semana, feriado, media jornada y jornada de 24 h. Un calendario con turnos solapados dentro de numba no deja el requisito en verde.

Es ejecutable y el oráculo es `WorkCalendar`, no un esperado inventado. El archivo compara la tabla contra el reloj en los cinco casos: `test_zero_minute_snaps_forward_and_backward`, `test_weekend_gap_and_full_shift`, `test_holiday_is_not_work_and_half_day_stays_at_noon`, `test_full_day_shift_moves_twenty_four_hours`. `work_between` se afirma en fin de semana y en la jornada de 24 h. En feriado y media jornada el contraste de la tabla es `add_work` y `subtract_work`. El criterio no exige las tres operaciones en cada escenario. `test_seven_day_calendar_matches_a_grid_of_moves` suma el calendario de 7 días, que la 10.3 pide en el generador.

El solape no es un caso de éxito de esta fila. `build_tables` levanta `UnsupportedCalendar` si un turno pisa al anterior. Ese calendario no se tabula dentro de numba. La caída a la referencia está en R-362.

## R-362

La fila pide camino rápido, ALAP antes de la holgura libre, restricciones, avance, hitos, LOE, WBS, horizonte y turno solapado. El test es `tests/test_e7_match.py`. El oráculo de la fila es `schedule_cpm_reference`.

El criterio del contrato es más corto y sigue siendo ejecutable. Cada cláusula tiene caso y oráculo en ese archivo:

| Cláusula del contrato | Test | Oráculo |
|---|---|---|
| El camino de semana usa `path=fast` | `test_weekday_chain_uses_the_fast_path` | fechas contra la referencia y `LAST["path"] == "fast"` |
| La holgura libre ve a la sucesora después de ALAP | `test_free_float_sees_the_successor_after_alap` | la referencia en la red fija (A, B con `CS_ALAP` y lag −8, C). `_same` incluye la holgura libre |
| El solape cae a la referencia sin nota nueva | `test_overlapping_shifts_fall_back_without_an_extra_note` | mismas `approximations`, mismo early finish, `LAST["path"] == "reference"` |
| El horizonte corto crece | `test_short_horizon_grows_and_still_matches` | la referencia, con `path=fast`, al forzar `horizon_days` a 1 |
| El horizonte agotado nombra el límite | `test_exhausted_horizon_names_the_limit` | `CalendarLimitError` con el texto `horizonte de calendario agotado` |

Que toda red de 30 000 quepa en 0,5 s antes de medirla no deja esta fila en verde. El tiempo está en R-364.

El parche de `horizon_days` sí llega al motor: `_ensure` lo resuelve en `atlaspmo.engine.fast`. La afirmación `horizon_days(100, 10) == 24` usa el nombre ya importado en el test, así que comprueba la fórmula real (`max(21, minutos / jornada + 14)`), no el parche. Con lag 0, `lag_days` queda en 2 y la primera ventana es el 2026-01-05 ± 2 días. La cadena de 40 h + 40 h en calendario de 8 h no cabe ahí. Si el horizonte no creciera, el caso no coincidiría con la referencia ni mantendría `path=fast`. El criterio se puede fallar.

Restricciones, avance, hitos, LOE y WBS no están en la frase del contrato y sí en la fila. No quedan sin oráculo: `test_constraints_progress_milestones_and_rollup_match` los corre contra la referencia en los tres avances, las dos reglas de crítico y los tres tipos de holgura. Los tests de mano de R-363 los vuelven a exigir con fechas calculadas a mano. La frase corta del contrato no borra ese oráculo.

## R-363

La fila pide que los tests de mano del motor sigan pasando con el rápido por defecto. Cita `tests/test_cpm.py`. El oráculo son los casos a mano de CPM.

El contrato suma los de restricciones, longest path e hitos, y dice que corren con el motor rápido por defecto. Borrar la referencia no deja el requisito en verde. `schedule_cpm_reference` sigue en `src/atlaspmo/engine/cpm.py`.

Es ejecutable. El defecto de `EngineOptions.engine` es `"fast"`. `schedule_cpm` solo entra a la referencia si `engine="reference"`. No hay `conftest` que cambie el motor. Estos archivos no pasan `engine="reference"`:

- `tests/test_cpm.py`. Las dos `EngineOptions` fijan solo `progress` (`progress_override` y `actual_dates`). El resto llama `schedule_cpm(schedule)`.
- `tests/test_e1_constraints.py`. Tres casos a mano, `schedule_cpm(schedule)`.
- `tests/test_e1_longest.py`. `EngineOptions(critical_rule="longest")` no toca `engine`.
- `tests/test_e1_milestone.py`. Tres casos a mano, `schedule_cpm(schedule)`.

El oráculo son las fechas y notas escritas en esos tests, no la salida del propio motor rápido. La sección 10.3 pide que los tests existentes del motor pasen con el rápido. Esa lectura, alineada con la fila («tests de mano»), es este conjunto. Otros llamadores (`tests/test_phase2.py`, `tests/test_e2_clean.py`, `tests/test_risk.py`, `tests/test_e4_outputs.py`, `tests/property/test_invariant_e.py`, `tests/property/test_logic.py`) tampoco fijan `engine="reference"`, así que heredan el mismo defecto. No son el oráculo a mano del CPM y el contrato no los necesita para que el criterio sea ejecutable.

## R-364

La fila pide `cpm_30k` y `dcma_30k` medidos a 30 000, y activarlos solo si cumplen. El test es `tests/perf/test_seccion11.py`. El oráculo es `gen_scale.py` en este equipo.

El contrato nombra `test_s11_cpm_30k` y `test_s11_dcma_30k`, medidos a 30 000, y los mete en `seccion11.toml` solo si quedan bajo 0,5 s y 10 s. Copiar los tiempos de la revisión en Linux no los deja en verde.

Es ejecutable. `SIZE` sale de `ATLASPMO_S11_SIZE` y por defecto es 30 000. `FULL` exige el límite solo en ese tamaño. `test_s11_cpm_30k` calienta y luego exige menos de 0,5 s. `test_s11_dcma_30k` exige menos de 10 s. Ambos arman la red con `write_scale` de `scripts/gen_scale.py`. La red no es un XER real. Por debajo de 30 000 el test imprime el tiempo y no exige la meta, como ya dice la sección 8.3. La medición que el criterio nombra es la corrida a 30 000.

No reejecuté esa corrida. No confirmo ni desmiento los tiempos de `docs/qa/E7/perf.md` ni el hecho de que `cpm_30k` y `dcma_30k` ya figuren en `activas` de `docs/qa/seccion11.toml`. La regla sigue teniendo oráculo: el reloj de esos dos tests sobre `gen_scale.py` en este equipo. No es el cuadro de Linux de la sección 8.3.

## Sección 10.3

| Exigencia | Dónde queda ejecutable | Oráculo |
|---|---|---|
| Hypothesis al minuto: ES, EF, LS, LF, TF, FF y la misma lista de aproximaciones | R-360, `tests/property/test_e7_differential.py` | `schedule_cpm_reference` |
| Esas redes cubren calendarios, vínculos, lags, restricciones, avance, hitos, LOE y WBS | el mismo test, en la estrategia `_nets` | el mismo |
| Los tests existentes del motor pasan con el rápido | R-363; defecto `engine="fast"` y los cuatro archivos de mano | casos a mano |
| `cpm_30k` &lt; 0,5 s y `dcma_30k` &lt; 10 s, solo si se miden a 30 000 | R-364 | `gen_scale.py` en este equipo |

## Comandos

`git rev-parse HEAD` → `73666ebeddad0db948c2f53b978b3f78ebbf7bee`. Rama `v3`. No hubo pytest, gate ni medición de la sección 11.
