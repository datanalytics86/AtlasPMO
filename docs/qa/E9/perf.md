# E9 — Monte Carlo a 30 000

Equipo de esta corrida, el mismo de E8: 11th Gen Intel Core i5-1145G7 @ 2.60 GHz, 39,7 GB de RAM, Windows-11-10.0.26200-SP0, CPython 3.12.16. Red realista de `scripts/gen_scale.py` (`series=False`). `RiskConfig(seed=1, iterations=1000, tornado_hours=0)`, sin rangos. El reloj incluye la compilación numba: no hay calentamiento. No incluye la escritura ni la lectura del XER.

| Corrida | Segundos | `passes` | `full_cpm` | Tornado |
|---|---|---|---|---|
| Misma llamada, impresión de `TRACE` | 61,581 | 1 000 | 0 | 0 |
| `pytest -o addopts= tests/perf/test_seccion11.py::test_s11_montecarlo_30k -s` | 63,569 | el test exige 1 000 términos |  |  |

La fila del test es `S11 montecarlo_30k n=30000 63.569s limite=300s`, 1 passed. El límite es 300 s. Se cumplió. `montecarlo_30k` no entra en `seccion11.toml` hasta el cierre aprobado (ADR-019). Los 49,1 s de la revisión eran 300 actividades y 5 iteraciones: no se copian.

numba avisa que no puede guardar en disco `batch_passes` porque ve un global dinámico. Esa compilación queda dentro de los 63,569 s. No se baja el límite ni se salta el bucle: con varianza cero igual corren las 1 000 pasadas.
