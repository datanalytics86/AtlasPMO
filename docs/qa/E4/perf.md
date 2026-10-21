# Rendimiento E4

Equipo: Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise. Fecha 2026-10-21. Red de `gen_scale`, 30 000 actividades, `series=False`. No se usó un XER real.

| Medición | Cifra | Qué es |
|---|---|---|
| Un CPM, 30 000 actividades | 9.401 s | Una sola llamada a `schedule_cpm`. No es Monte Carlo. |
| Monte Carlo, 30 000 por 1 000 | no corrido | La proyección 1 000 × 9.401 s son unas 2,6 h. No es una medición y no cumple 5 minutos. |
| Tornado de 30 000 | no corrido | Hoy es un CPM completo por actividad. No se proyecta como cumplimiento. |

`tests/perf/test_montecarlo.py` cronometra 4 iteraciones de dos actividades y exige menos de 30 s. Ese verde no es el criterio de la sección 11.

numba no está cargado. El tornado no recorta al cono.
