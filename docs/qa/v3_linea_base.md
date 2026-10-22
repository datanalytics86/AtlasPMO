# Línea base de la v3

Revisión externa del 2026-10-22, sobre el commit que integra `v2` (`cc81a31`) con el gate de ADR-019. Equipo: contenedor Linux de la revisión. Los tiempos del equipo de Nicolás los registra Grok en `docs/qa/E7/inicio.md`.

## Gate (`--etapa E7 --base cc81a31`)

| Control | Estado | Nota |
|---|---|---|
| G1, G2, G3 | pass | 222 tests |
| G4 | pass | trinquete sobre `baseline.json`; meta pendiente en calendars, engine, logic y resto |
| G5, G7, G8, G9, G11, G12 | pass | |
| G6 | pass | `tests/perf` y la meta activa `lectura_30k` |
| G10 | fail | esperado: E7 aún no tiene requisitos; lo resuelve QC-1 |
| G13 | info | no medido |

## Metas de la sección 11 (red de `gen_scale.py`)

| Meta | Límite | Medido | Escala |
|---|---|---|---|
| `lectura_30k` | 15 s | 1,8 s | 30.000 |
| `cpm_30k` | 0,5 s | 15,8 s | 30.000 |
| `dcma_30k` (CPM + DCMA) | 10 s | 16,1 s | 30.000 |
| `redundancia_30k` | 180 s | 52,5 s | **300** |
| `montecarlo_30k` | 300 s | 49,1 s (5 iteraciones) | **300** |

## Perfil (300 actividades, cProfile)

- CPM: el 85–90 % del tiempo está en `WorkCalendar._earliest` / `_cumulative` (búsqueda binaria de ~30 pasos en Python por cada `add_work` y `subtract_work`).
- Monte Carlo: `_tornado` corre un CPM completo por actividad aunque `tornado_hours` sea 0 (148 de 151 s).
- Redundancia: 336 CPM completos entre la bisección (`_confirm`) y la validación conjunta (`_join`).
