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
