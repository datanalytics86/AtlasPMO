# qa-revisor — E9

Revisión de E9, brecha B-07, HEAD `cf35f17`, rama `v3`. Se contrastaron el contrato aceptado (`docs/qa/E9/QC1_contrato.md`), ADR-022, las secciones 8.1, 8.5, 10.3 (E9), 11 y 12 de `docs/MEGAPROMPT_v3.md`, las filas R-380 a R-386 de `docs/qa/TRAZABILIDAD.md`, `docs/qa/E9/riesgo.md`, `docs/qa/E9/perf.md` y el diff `82f9fa4..cf35f17`. No se editó producto, tests, gate, umbrales ni `seccion11.toml`. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se escribió `docs/qa/E9/VEREDICTO.md`. No se reejecutó la red de 30 000 por 1 000.

## Cierre

No emito veredicto de etapa. El gate no corrió, así que no cabe dar la etapa por cerrada. H-1 es crítico (sección 8.5: caída con una entrada válida; el motor de referencia sí tiene término). Eso impide el cierre aunque el gate salga en verde. H-2 es menor y no bloquea. No autorizo activar `montecarlo_30k`.

## Diff

`git diff --stat 82f9fa4..cf35f17` toca `montecarlo.py`, `fastloop.py`, `numeric/batch.py`, `tests/test_e9_risk.py`, `tests/property/test_e9_differential.py`, `tests/test_risk.py`, `tests/test_e4_tornado.py`, `docs/qa/E9/riesgo.md`, `docs/qa/E9/perf.md` y una línea de `docs/ESTADO.md`. No entran `kernels.py`, `fast.py`, `tests/perf/test_seccion11.py`, `docs/qa/baseline.json`, `scripts/qa_gate.py`, `docs/qa/skips.toml` ni `docs/qa/seccion11.toml`. En `activas` siguen lectura, cpm, dcma y redundancia. `montecarlo_30k` no está.

## Requisitos

R-380. La columna sin correlación iguala a `sample_duration` con la misma semilla, y un evento de probabilidad 0 avanza el generador: lo afirma `test_column_matches_sample_duration_and_a_zero_event_advances_rng`. El fallo de Cholesky ya estaba en `test_invalid_correlation_is_skipped` y sigue. El reorden con Cholesky no tiene assert en la suite. Lo corrí aparte, con la misma semilla y el mismo estado del generador después de las duraciones: las columnas igualan a `iman_conover` y la nota de la diagonal (`1e-8`) aparece. Queda como H-2, menor. La fórmula de `iman_conover` no se reescribió.

R-381. En el camino rápido `TRACE["passes"]` queda en las iteraciones y `TRACE["full_cpm"]` en 0. El bucle rápido no llama a `_with_hours` ni arma un `Schedule` por iteración; el test que parchea `_with_hours` lo cubre, y el código de `_fast_iterations` no lo usa. `batch_passes` está decorado con `parallel=True` y el bucle es `prange`. Cada pase llama a `run_passes` sobre una copia de la duración (`i64` del hilo, no el array de la caché). El término es `max` de `ef_pre` (el quinto buffer). El fin vigilado de hitos y convergencias sale de `ef`, el early finish ya pasado por ALAP. En la cadena con hito ALAP las dos iteraciones igualaron al `project_finish` y al `early_finish` empaquetado de la referencia, crítico incluido. El join ALAP igualó el fin determinístico. No se copia el cuerpo de `run_passes`.

R-382. Con `tornado_hours <= 0` la función vuelve antes de armar nodos: tornado `()`, `cones` vacío, `tornado_visited` 0, y no aparecen las dos frases viejas. Lo vi en una corrida de varianza cero y está en `test_tornado_off_visits_nothing`. Con horas positivas, el cono de la cadena A–B–C–D–E está afirmado en el test, y el delta sale de un forward parcial del motor de referencia comparado con `schedule_cpm_reference`. Una cadena con SS y lag de 8 h dio los mismos deltas que la referencia (A 0, B 8, C 8) y los conjuntos `{A,B,C}`, `{B,C}` y `{C}`. El caso con LOE y WBS enlazados no los mete en `cones`; el delta de A y de B es 8 h, igual que la referencia. Esos resúmenes no tienen fila: subirles la duración no mueve el término de la referencia (delta 0).

R-383. `tests/property/test_invariant_e.py` pasó en el subconjunto de abajo, perfil qa. El test de mano de ancho cero sigue exigiendo `WED_16` por 5, criticidad 1 y 1, y los dos estados `no_evaluable`. Con `tornado_hours=0`, ancho cero y evento de probabilidad 0 medí `passes` 5, `full_cpm` 0 y cinco términos. No se compara el Monte Carlo contra sí mismo: el oráculo del test de mano es `schedule_cpm`.

R-384. No reejecuté las 30 000 por 1 000. `docs/qa/E9/perf.md` dice 63,569 s en el test y 61,581 s en la corrida hermana, con `passes` 1 000, `full_cpm` 0 y tornado 0. El test oficial no calienta, usa `tornado_hours=0` y no trae rangos; el límite que ya tiene es 300 s. El código no salta el bucle cuando la varianza es cero: si ninguna columna se aparta de la duración base, `row_minutes` queda con forma `(iteraciones, 0)` y `prange` igual recorre todas. `montecarlo_30k` no está en `activas`. No entra hasta un cierre aprobado. Los 49,1 s de la revisión no se copian: eran 300 actividades y 5 iteraciones.

R-385. La frase vieja salió de `montecarlo.py`. En el camino rápido la nota es «Monte Carlo corre en numba sobre los arrays del motor rápido.» y no está «numba no se cargó». En el camino de referencia la nota dice que el lote no corrió en numba y la frase nueva no aparece. No están las dos juntas. El test de mano exige la nueva. El aviso de numba de que `batch_passes` no se puede guardar en disco, por un global dinámico, ya está en `perf.md`. No cambia el resultado. La compilación queda dentro del reloj medido.

R-386. `tests/test_risk.py` solo cambia la frase. No se movieron el término del evento cierto, el tornado 8/8 ni el 8/0/8, el join, el SSI, Spearman, la crucialidad ni los hitos P50 P80 P90. `tests/test_e4_outputs.py` no está en el diff. `tests/test_e4_tornado.py` conserva el conjunto `{A, B, C}` y reemplaza las dos frases viejas por la del cono.

## Lo que había que buscar

Salto de pasadas por varianza cero: no está. El sello `passes = iterations` se escribe después de `run_batch`, y el bucle no tiene un retorno anticipado cuando el índice variado viene vacío. La corrida de ancho cero dejó `passes` en 5.

`Schedule` por iteración: no está en el camino rápido. Sigue en `_reference_iterations`, que es el respaldo cuando el calendario no entra en el rápido o `LAST["path"]` no es `fast`. Ese camino incrementa `full_cpm` y no afirma que numba corrió el lote.

Frase vieja junto a la nueva: no. Son excluyentes.

Tornado con horas 0: no recorre actividades.

Cono distinto de la referencia: no en la cadena del test, ni en el SS con lag, ni en la red con LOE y WBS enlazados. El delta usa el forward parcial de la referencia y el término de antes de ALAP (`_project_finish` se toma antes del backward). No es el early finish ya movido por ALAP.

LOE dentro del cono: no. `_nodes` sigue dejando fuera `TT_LOE` y `TT_WBS` antes de armar sucesoras, también si el vínculo existe. WBS cae en el mismo salto.

Cobertura del cuerpo `njit`: ver abajo. No alcanza para tirar G12 bajo 90,5.

## Cobertura y G12

No corrí el gate ni la suite de 281 con cobertura. La cuenta usa el total de E8 (`docs/qa/E8/gate.json`: 5 754 statements, 515 sin cubrir, 91,0) y el delta medido con el tracer sobre el código nuevo.

| Archivo | Statements que cuenta el tracer | Sin cubrir en el subconjunto |
|---|---|---|
| `fastloop.py` (nuevo) | 293 | 22 |
| `batch.py` (nuevo) | 88 | 25 |
| `montecarlo.py` | 269 ahora; 322 en `82f9fa4` | las ramas que faltan ya eran las defensivas; el alta del cableado está cubierta |

El 269 es el del tracer y coincide con el parser. El 322 del archivo viejo es solo el parser: no reejecuté la cobertura de E8.

El cuerpo de `batch_passes` (líneas 64 a 142), la llamada numba de la línea 341 y el `raise` de la línea 345 son los 25. Con el tracer activo `run_batch` usa `_python_batch`, así que el cuerpo `njit` no se ejecuta. En la suite sin tracer, la que midió el orquestador, sí corre numba: los tests de fechas no están mirando el gemelo. El `ImportError` de numba tiene `pragma: no cover` y no entra en los 88.

Cuenta pesimista: se suman 293 y 88, se restan los 53 statements que salieron de `montecarlo.py` suponiéndolos cubiertos, y se suman 47 sin cubrir. Total 6 082 statements, 562 sin cubrir, 5 520 cubiertos, 90,8 %. G12 compara el porcentaje ya redondeado a un decimal y falla si la baja es mayor que 0,5 (`scripts/qa_gate.py`: `stored - coverage > 0,5`). 91,0 − 90,8 = 0,2. No falla. Si alguna rama borrada ya estaba sin cubrir, o si otro test de la suite tapa parte de los 22 de `fastloop.py`, el porcentaje sube. Los 25 de `batch.py` no bajan con el resto de la suite: el gate siempre traza, y ningún test agota el horizonte.

El archivo `batch.py` queda en 72 % (25 de 88). La meta de la sección 8.1 para el resto es 80 % de líneas, por paquete, no por archivo. El piso de G4 para el resto es 80: la línea base está en 90,2 y la meta es 80. Decenas de statements sin cubrir no lo cruzan. No lo marco importante. El algoritmo que el tracer puede ver es `_python_batch`, y el numba lo ejercen los tests sin cobertura. El `raise` sin cubrir es el de H-1, no un segundo hallazgo de cobertura.

`fast.py` y `kernels.py` no se editaron. Las ramas de engine siguen en el 85,1 del gate de E8, sobre el piso 85,0.

## Comandos

No reejecuté `pytest` de la suite por defecto ni `test_s11_montecarlo_30k`. Esas cifras quedan como las midió el orquestador: 281 passed y 9 deseleccionados; 63,569 s y 61,581 s.

Con el Python del `.venv` del clon, sin cobertura de la suite entera:

- `tests/test_e9_risk.py`, `tests/test_risk.py`, `tests/test_e4_tornado.py`, `tests/test_e4_outputs.py`, `tests/property/test_invariant_e.py` y `tests/property/test_e9_differential.py`, con cobertura de `analysis/risk`: 21 passed en 12,44 s.
- Los mismos sin `test_e4_outputs.py` ni el diferencial, con cobertura de `batch.py` y `fastloop.py`: 19 passed en 10,72 s. `batch.py`: 88 statements, 25 sin cubrir, líneas 64-142, 341 y 345.

Sondas, sin la red de 30 000. Calendario de 7 días, 08:00 a 16:00, una actividad de 8 h, fecha de corte 2026-01-05 08:00:

- Impacto cierto de 168 h: el lote termina en 2026-01-26 16:00, igual que el rápido y que la referencia.
- Impacto cierto de 176 h, y también un rango de ancho cero en 184 h: `CalendarLimitError`, texto «horizonte de calendario agotado». El mismo cronograma con la duración ya aumentada termina en los dos motores en 2026-01-27 16:00. Con un tracer puesto, para forzar `_python_batch`, el impacto de 176 h cae igual.
- LOE y WBS enlazados, cono y delta, como arriba. Hito de fin con `CS_ALAP`: las fechas y el crítico igualan a la referencia. Correlación 1: columnas iguales a `iman_conover`.

## Qué no pude verificar

No corrí G1 a G13 ni la suite de 281. No medí de nuevo los 63,569 s. No abrí un cronograma real. La cuenta de 90,8 no es el `coverage_percent` del gate: es el delta sobre el 91,0 de E8. No sé cuántos de los 22 de `fastloop.py` tapa el resto de la suite; solo sé que no pueden ser más.
