# Hallazgos E9

HEAD `cf35f17`. El gate de la etapa no corrió. No hay `gate.json`. No reejecuté la suite de 281 ni la red de 30 000 por 1 000. Las cifras de `docs/qa/E9/perf.md` quedan como las midió el orquestador.

## H-1 — crítico

El lote se cae cuando la duración muestreada no cabe en la ventana que se compiló para el CPM base. La misma duración, pasada por `schedule_cpm` o por `schedule_cpm_reference`, termina bien.

Entrada válida: una actividad de 8 h, calendario de 7 días de 08:00 a 16:00, fecha de corte 2026-01-05 08:00. Dos formas equivalentes:

- un evento de probabilidad 1 e impacto 176 h (la duración queda en 184 h);
- un rango de ancho cero en 184 h.

`run_risk` levanta `CalendarLimitError` con el texto «horizonte de calendario agotado». No devuelve término ni nota. Con impacto 168 h (duración 176 h) el lote sí termina, en 2026-01-26 16:00, igual que el motor rápido y que la referencia. Con 176 h de impacto los dos motores, sobre el cronograma ya aumentado, terminan en 2026-01-27 16:00. El lote no.

La causa está en el corte de E9. `run_risk` primero programa el cronograma de 8 h. Esa compilación deja la ventana en `horizon_days` (aquí 21 días) y la guarda en la caché. `run_batch` llama a `run_passes` sobre esas tablas. No repite el crecimiento de `_ensure` en `src/atlaspmo/engine/fast.py`, que es lo que permite al CPM suelto agrandar el horizonte. Si algún pase devuelve un código distinto de 0, `src/atlaspmo/numeric/batch.py` levanta la excepción. El calendario sí entra en el motor rápido, así que no se usa el bucle de referencia, el que arma un `Schedule` por iteración y sí cabría en la duración larga.

Lo mismo ocurre con el tracer activo, por `_python_batch`: no es solo el camino numba. La sonda sin tracer es la que corre `batch_passes`.

La suite no llega a ese borde. El rango más ancho de los tests de mano es 40 h. Bajo cobertura, la línea del `raise` no se ejecuta. La sección 8.5 pone la caída con una entrada válida entre lo crítico. El término de la referencia existe y el lote no lo entrega. Bloquea el cierre. No autoriza activar `montecarlo_30k`.

## H-2 — menor

Ningún test corre Iman-Conover cuando la matriz sí admite Cholesky a través de `run_risk`. `test_invalid_correlation_is_skipped` solo cubre el rechazo. `test_column_matches_sample_duration_and_a_zero_event_advances_rng` no trae correlación. Las líneas del reorden y de la nota de la diagonal quedan fuera del subconjunto medido con cobertura.

No bloquea. Con semilla 3, seis iteraciones y correlación 1 entre A y B, las columnas de `TRACE` igualaron a `iman_conover` usando el generador ya avanzado por las duraciones, y la nota de `1e-8` apareció. La fórmula no se reescribió. El fallo de Cholesky sigue afirmado.

## QC-6

HEAD `0750b2d`. El gate de `docs/qa/E9/gate.json` sale 0: 283 tests, cobertura 91,1, G1–G12 pass, G13 info. No lo reejecuté. No reejecuté la red de 30 000. El relato de arriba es el de `cf35f17`, antes del fix, y queda.

### H-1 — cerrado

`436bc55` recompila una vez cuando alguna hora, ya con el evento, redondea a más minutos que `compiled.duration`. `_compiled_for_peaks` arma un cronograma con el máximo de cada columna, llama a `schedule_cpm` para crecer la ventana y el lote usa esa compilación. No hay un `Schedule` por iteración. `_minutes` escribe los minutos absolutos de la muestra; si todos igualan la duración pico, la columna no se pisa y el lote corre con esa duración ya compilada.

Lo medí sobre el mismo calendario de 7 días, 08:00 a 16:00, actividad de 8 h y fecha de corte 2026-01-05 08:00. Evento cierto de 176 h, tres iteraciones: el término es 2026-01-27 16:00, igual que `schedule_cpm` de referencia con 184 h. `passes` 3, `full_cpm` 0, una sola llamada a `_with_hours`, y la nota dice que el lote corrió en numba. No está la de fallback. El rango de ancho cero en 184 h lo afirma `test_a_long_duration_uses_a_window_that_fits`, que pasó en esta pasada. Una probabilidad 0,5 con el mismo impacto dejó iteraciones en 8 h y en 184 h; las ocho igualaron al reference, `passes` 8 y `full_cpm` 0. Un rango fijo de 4 h no recompila (`_with_hours` cero veces) y también iguala.

Si la recompilación no devuelve un compilado o el segundo lote lanza `CalendarLimitError`, `_reference_instead` quita la nota de numba y agrega la de fallback. Lo leí en `_reference_instead`. Al forzar la excepción en `run_batch` la nota cambió como dice el código. Ese forzamiento, con probabilidad distinta de 0 y de 1, volvió a sortear el evento porque `_columns` ya había avanzado el generador: no lo promuevo a hallazgo. No apareció en el evento de 176 h, ni en la mezcla, ni en un lag de −40 h, ni en dos rangos hasta 80 h. Esos se quedan en el lote.

### H-2 — cerrado

`test_perfect_correlation_reorders_like_iman_conover` es el caso que faltaba: semilla 3, seis iteraciones, correlación 1 entre A y B. Exige que las columnas de `TRACE` igualen a `iman_conover` con el generador ya avanzado por las dos duraciones, y que una nota traiga `1e-8`. Pasó en esta pasada. `test_invalid_correlation_is_skipped` sigue cubriendo el rechazo de Cholesky. La fórmula de `iman_conover` no se reescribió.

No queda un crítico ni un importante abierto.
