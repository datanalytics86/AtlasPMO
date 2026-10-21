# Lectura de 30k — E1

Medición en esta máquina, fuera de la aserción del test. El test `tests/perf/test_scale.py` exige menos de 15 s y cronometra solo `read_xer`.

| Dato | Valor |
|---|---|
| CPU | Intel Core Ultra 9 185H |
| RAM | 31.4 GB |
| SO | Windows 11 Enterprise |
| Archivo | `gen_scale.py`, 30 000 actividades, `series=False` |
| Tamaño | 4 218 499 bytes |
| `read_xer` | 0.197 s |

Los otros criterios de la sección 11 no están medidos en esta etapa: DCMA 30k, redundancia 30k, Monte Carlo 30k por 1 000, conformidad con P6. No medido no es cumplido.

El comando fue una corrida directa de `write_scale` y `read_xer` en un directorio temporal, el 2026-10-21. No se versionó el XER.
