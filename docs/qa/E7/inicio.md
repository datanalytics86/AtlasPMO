# E7 — línea base en este equipo

Medición del 2026-10-22, antes del motor rápido. Red realista de `scripts/gen_scale.py` con 30 000 actividades. Procesador que reporta el sistema: Intel64 Family 6 Model 170 Stepping 4, GenuineIntel. RAM 31,4 GB. SO Windows-11-10.0.26200-SP0. Es el mismo equipo de `docs/qa/E1/perf.md`.

El motor medido aquí es el de referencia. Los tiempos de la revisión en Linux (`docs/qa/v3_linea_base.md`) no se usan como resultado de este equipo.

| Meta | Límite | Valor | Activa al arranque |
|---|---|---|---|
| lectura_30k | 15 s | 0,655 s | sí |
| cpm_30k | 0,5 s | calentamiento 9,346 s; pase 9,892 s | no |
| dcma_30k | 10 s | 10,127 s (incluye un CPM) | no |
| redundancia_30k | 180 s | más de 30 min | no |
| montecarlo_30k | 300 s | más de 30 min | no |

`redundancia_30k` y `montecarlo_30k` se lanzaron en paralelo con corte a 30 minutos. La redundancia no terminó. Monte Carlo seguía en ejecución al pasar los 30 minutos y se cortó. Ninguna de las dos se anota como tiempo finito.

Generar el XER tardó 0,152 s. El gate inicial de E7, con el árbol todavía sin requisitos, salió 1 solo por G10 (`sin requisitos de E7`). G1 a G9, G11 y G12 pasaron. 222 tests. Cobertura 89,8. Ese gate no es el cierre.
