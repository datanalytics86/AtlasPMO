# E9 — riesgo

Ciclo 1. B-07. ADR-022. El contrato está aceptado. Esta nota registra el rojo de antes del cableado.

## Rojo

La colección de `tests/test_e9_risk.py` falló con `ImportError`: no se puede importar `TRACE` desde `atlaspmo.analysis.risk.montecarlo`. El lote y el cono todavía no estaban conectados a `run_risk`. No es un fallo de números.

## Verde

Después del cableado, la suite por defecto pasa: 281 tests, 9 deseleccionados. `tests/test_e9_risk.py`, `tests/test_risk.py`, `tests/test_e4_tornado.py`, `tests/test_e4_outputs.py`, `tests/property/test_invariant_e.py` y `tests/property/test_e9_differential.py` quedan en ese verde. `TRACE["passes"]` iguala las iteraciones en el camino rápido y `TRACE["full_cpm"]` queda en 0. Con `tornado_hours` en 0 el tornado no visita actividades. La medición de 30 000 por 1 000 está en `docs/qa/E9/perf.md`: 63,569 s, bajo 300 s.

## H-1

qa-revisor vio que un evento cierto de 176 h sobre una actividad de 8 h caía con `CalendarLimitError`: la ventana era la del CPM de 8 h. El arreglo recompila una vez, con la duración máxima de cada columna, y no arma un cronograma por iteración. El evento de 176 h y el rango fijo de 184 h igualan al reference. `passes` queda en las iteraciones y `full_cpm` en 0. La red de 30 000 no trae rangos, así que esa corrida no recompila.
