# E8 — redundancia a 30 000

Equipo de esta corrida, distinto del de E7: 11th Gen Intel Core i5-1145G7 @ 2.60 GHz, 39,7 GB de RAM, Windows-11-10.0.26200-SP0, CPython 3.12.16. Red realista de `scripts/gen_scale.py` (`series=False`). `classify_links` por defecto. El reloj del test no incluye la escritura ni la lectura del XER.

| Actividades | Segundos | `mask_passes` |
|---|---|---|
| 200 | 0,03 | 1 |
| 400 | 0,08 | 1 |
| 800 | 0,13 | 1 |
| 2 000 | 0,29 | 1 |
| 30 000 | 14,839 | 1 |

La fila de 30 000 es `pytest -m seccion11 tests/perf/test_seccion11.py -k redundancia -s`: `S11 redundancia_30k n=30000 14.839s limite=180s`, 1 passed. El límite se cumplió. La meta no se activa en `seccion11.toml` hasta el cierre aprobado (ADR-019). Los 52,5 s de la revisión eran 300 actividades y no se copian.

Antes del atajo, el mismo `classify_links` en 800 actividades hacía 926 pases enmascarados y tardaba 14,72 s. A 30 000 eso no cabía en 180 s.
