# Hallazgos E7 ciclo 3

HEAD `577c6ba`. El gate de `docs/qa/E7/gate.json` sale 0: G1–G12 en pass, G13 en info. 239 tests, cobertura 91,2. La meta pendiente de cobertura no bloquea (ADR-019). No reejecuté el gate ni la red de 30 000; G6 queda como está en ese archivo (`cpm_30k` y `dcma_30k` en pass).

Reejecuté `tests/test_e7_match.py::test_not_started_actual_does_not_erase_driving`, `test_project_finish_seconds_survive_a_constraint_that_does_not_bind`, `test_actual_seconds_do_not_widen_the_longest_path_or_driving` y `tests/property/test_e7_differential.py`: 4 passed en 4,08 s. Además comparé el motor rápido contra `schedule_cpm_reference` en 458 redes (58 armadas y 400 al azar, semilla 7): tarea, hito de inicio, hito de fin, ALAP, MEO, rollup WBS y LOE, retained, progress override y actual dates, longest y float. Calendario 08:00–16:00 los siete días, salvo las redes al azar, que también usan semana, media jornada y 24 h. Cero diferencias de minuto, holgura, crítico, conductoras o aproximaciones.

## H-4 — cerrado

Una actividad no iniciada con `act_start_date` en el mismo minuto que el inicio por red ya no publica ese real ni vacía las conductoras. `_dates` usa `_keep` del real solo si `started==1`; si no, publica `from_minute(es)`. `_driving` descarta conductoras por segundos solo si `started==1` y el minuto del real coincide con `logic_es` (`src/atlaspmo/engine/fast.py`).

P de 8 h. B de 8 h, `TK_NotStart`, `act_start_date=2026-01-06 08:00:45`. Vínculo P→B `PR_FS` lag 0. Fecha de corte `2026-01-05 08:00`.

- Longest y float: inicio temprano de B `2026-01-06 08:00:00` en los dos motores. Conductoras `('P',)`. Con longest, P queda crítica en los dos. Holguras 0.
- El mismo real en un hito de inicio (`TT_Mile`): fin de proyecto `2026-01-06 08:00:00`, conductoras `('P',)`, P crítica con longest y con float.
- Hito de fin (`TT_FinMile`) con real `2026-01-05 16:00:45`: fechas `16:00:00` y conductoras `('P',)` en los dos.

El arreglo de una iniciada no se deshizo. B `TK_Active` con real `2026-01-06 08:00:45`, predecesora P en ese minuto y otra más tarde: conductoras `()` y P no crítica, en los dos. Sin segundos en el real: conductoras `('P',)` y P crítica, en los dos. Un `CS_MEO` que empuja el inicio más allá del real deja las conductoras vacías en los dos, porque el arranque ya no cae en el vínculo.

## H-5 — cerrado

`test_not_started_actual_does_not_erase_driving` arma la tarea y el hito de inicio, y `_same` exige datetime, holgura, crítico y orden de conductoras contra `schedule_cpm_reference`. La tarea corre con longest y con float; el hito, con longest. El float del hito lo corrí aparte y coincide. `tests/property/test_e7_differential.py` sortea `act_start` con segundos 0 o 45 también en `TK_NotStart`. Pasó, con 500 ejemplos y `derandomize=True`.

## H-6 — cerrado

Los casos del ciclo 2 quedan iguales a la referencia, segundos incluidos. Lo cubre `test_project_finish_seconds_survive_a_constraint_that_does_not_bind`: `CS_MEOB` al `2026-01-08 16:00`, `CS_MSOA` al `2026-01-05 08:00`, `CS_MSO` sin fecha y `CS_ALAP` más `CS_MSOA`. `CS_ALAP` más `CS_MSO` sin fecha, que el test no nombra, también coincide: fin temprano y fin tarde `2026-01-05 16:00:45` en los dos. Una tarea de 8 h con `CS_MSOB` al `2026-01-05 18:30` y fin de proyecto `18:00:45` conserva esos segundos. Donde la restricción sí mueve el minuto, los dos motores coinciden enteros.

## H-7 — cerrado

Hito de inicio no iniciado, fin de proyecto `2026-01-05 15:30:45`. El test y la comparación directa dejan el fin tarde en `15:30:00` en los dos motores: el snap de `add_work` tira los segundos. Con predecesora, las conductoras siguen `('A',)` y el hito no es crítico por longest. El hito de fin, en el mismo calendario, conserva `15:30:45`.

## H-8 — menor

El fin tarde todavía pierde los segundos del fin de proyecto en tres bordes que el ciclo 2 no listó. El minuto, la holgura total, la holgura libre, el crítico y las conductoras coinciden. R-360 pide igualdad al minuto. No bloquea.

1. Duración 0 y `CS_MSO` o `CS_MSOB` cuyo snap atrás cae antes del fin de proyecto, pero el snap adelante no. `_constraints_leave_project_finish` usa el snap atrás cuando `duration==0`; la referencia compara el snap adelante. A completa con fin real `2026-01-05 18:00:45`. B hito de fin con `CS_MSOB` al `2026-01-05 18:30:45`. Fin tarde de B: referencia `18:00:45`, rápido `18:00:00`. Holgura total y libre 8 h, crítico falso, conductoras `()`. Lo mismo con una tarea o un `TT_Rsrc` de 0 h. Con `CS_MSO` a las `17:00` la restricción sí mueve el hito al `2026-01-06 08:00` y no hay diferencia.
2. Actividad ya iniciada con `CS_MANDSTART` o `CS_MANDFIN`. El pase atrás no aplica esa restricción, pero el rápido la toma como si moviera el fin y no repone los segundos. B `TK_Active`, real de inicio `2026-01-05 08:00`, `CS_MANDFIN` al `2026-01-08 16:00`, sin sucesoras. Fin de proyecto `2026-01-05 16:00:45`. Fin tarde de B: referencia `16:00:45`, rápido `16:00:00`. Holgura 0, no crítica por longest, conductoras `()`.
3. Sucesora que no ata el fin (`PR_SS` o `PR_SF`) y el fin tarde sigue siendo el de proyecto. `_finish_anchor` sale en cuanto hay alguna sucesora. A completa con fin `2026-01-08 16:00:45`. B hito de inicio en curso. S completa con fin `2026-01-08 16:00:00`. Vínculo B→S `PR_SF` lag 0. Fin tarde de B: referencia `16:00:45`, rápido `16:00:00`. Holgura 32 h, crítico falso, conductoras `()`.

Si además hay `CS_ALAP` sin sucesoras, el fin temprano copia ese fin tarde ya truncado. En las redes al azar se vio (actividad 2 de la semilla 7, red 60): `15:00:30` contra `15:00:00` en fin temprano y fin tarde, holgura 0, no crítica, conductoras `()`. De las 458 redes, 11 diferencias fueron solo estos segundos.

## Lo demás que coincidió

Rollup WBS y LOE con un hijo completo a las `16:00:45` y otro no iniciado con real `08:00:45`: el hijo conserva la conductora, el resumen no es crítico y las fechas coinciden, segundos incluidos. Fecha de corte con segundos. Microsegundos en un real no iniciado. Dos predecesoras. `actual_dates` con las dos fechas reales, que la referencia trata como terminada. No hay otros hallazgos abiertos.
