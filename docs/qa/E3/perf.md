# Rendimiento E3

Equipo: Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise. Fecha 2026-10-21. Red de `gen_scale`, 30 000 actividades, `series=False`. No se usó un XER real.

| Medición | Cifra |
|---|---|
| `evaluate` de calidad, sin baseline | 0.261 s |

El test `tests/perf/test_quality.py` exige menos de 10 s y cronometra solo `evaluate`. 0.261 s está bajo ese tope. No incluye el CPM: las métricas leen las fechas y holguras guardadas. CPLI, dentro de esa llamada, queda `no_evaluable` si la red no trae un término crítico usable. Eso no se presenta como un pass de la definición de CPLI, solo del tiempo.

Los otros criterios de la sección 11 no se miden aquí. La confirmación de redundancia de 30 000 sigue sin medirse (E2).
