# E7 — rendimiento del motor rápido

Mismo equipo y la misma red de 30 000 que `inicio.md`. El script quedó fuera del repositorio. `schedule_cpm` por defecto, `LAST["path"]=fast` en el calentamiento y en el pase medido.

| Tramo | Segundos |
|---|---|
| Lectura del XER ya generado | 0,751 |
| Calentamiento (compilación de arrays 0,518 + pase 0,307 + empaquetado 0,222) | 1,324 |
| Segundo CPM, arrays ya compilados | 0,331 |
| de ese segundo CPM: pase numba | 0,032 |
| de ese segundo CPM: empaquetado a `ScheduledActivity` | 0,299 |
| DCMA, incluyendo un CPM | 0,547 |

La corrida que afirma el test, `pytest -m seccion11 -k "cpm_30k or dcma_30k"`, dio `cpm_30k` 0,237 s (límite 0,5) y `dcma_30k` 1,494 s (límite 10). Las dos pasaron. `dcma_30k` incluye el CPM de un cronograma recién leído, sin el calentamiento del otro test. Por eso quedan activas en `seccion11.toml` junto con `lectura_30k` (ADR-019). La topo y el armado de arrays están dentro de los 0,518 s de compilación; el pase medido no los repite.

La línea base de referencia en este equipo era 9,892 s para el CPM y 10,127 s para DCMA.
