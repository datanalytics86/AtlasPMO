RECHAZADO

# qa-spec — E9

Auditoría de QC-1 antes del código. Se contrastaron `docs/qa/E9/QC1_contrato.md` (commit `79fd58d`, rama `v3`), las filas R-380 a R-386 de `docs/qa/TRAZABILIDAD.md`, ADR-022 y ADR-020 en `docs/DECISIONES.md`, y las secciones 8.4, 8.5, 9.5, 10.3 (párrafo E9), 11 y 12 de `docs/MEGAPROMPT_v3.md`. El bucle actual de `src/atlaspmo/analysis/risk/montecarlo.py` se leyó solo para ver qué comportamiento hay que reemplazar. No se editó producto, tests, gate, umbrales, oráculos ni el contrato. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se calculó la fecha de un cronograma. No hay producto que cerrar.

Los tests `tests/test_e9_risk.py` y `tests/property/test_e9_differential.py` no están en el árbol. El contrato los marca como no verdes. Eso no es motivo de rechazo.

## Requisitos

R-380: **sí.** Con semilla fija, la columna de cada actividad con rango es la lista que hoy arma `_consume_duration_rng` vía `sample_duration`. Después va Iman-Conover, sin reescribir la fórmula: si la matriz admite Cholesky, reordena y deja la nota de la diagonal (`1e-8`); si no, deja la nota de Cholesky y no reordena. Los eventos gastan un `random()` por iteración y por evento, en ese orden, después de las duraciones. Probabilidad 1 suma horas; probabilidad 0 no suma y aun así avanza el generador, como `_apply_events` hoy (`rng.random() >= probability` antes de sumar). El oráculo son `sample_duration` e `iman_conover` ya existentes, no el lote nuevo. Una matriz que no reproduzca esa secuencia no queda en verde.

R-381: **no.** Hay criterio y el oráculo de fechas no es el código nuevo: en un calendario que el rápido sí corre, `TRACE["passes"]` igual a `iterations`, `TRACE["full_cpm"]` igual a 0, sin `_with_hours`, sin `schedule_cpm` dentro del bucle ni una vez por actividad del tornado, dispatcher con `parallel=True`, bucle `prange`, cada pase sobre una copia de la duración, y al salir el `schedule_cpm` del cronograma original devuelve las mismas fechas. Copiar el cuerpo de `run_passes` o saltar pasadas por varianza cero no queda en verde. Falta el término de la iteración. Ver el hueco 2.

R-382: **no.** El delta en horas de trabajo, en los casos de mano ya escritos y en la cadena, iguala a `schedule_cpm_reference` con esa sola duración aumentada en `tornado_hours`. Comparar el delta solo contra el pase rápido no queda en verde. Con `tornado_hours <= 0` el tornado es `()` y `tornado_visited` es 0. La visita por actividad no se puede afirmar con el contador definido, y el caso LOE o WBS quedó condicional. Ver los huecos 1 y 3.

R-383: **sí.** `tests/property/test_invariant_e.py` sigue en verde. El perfil `qa` ya está en `tests/property/conftest.py`: 500 ejemplos, sin deadline, con deriva fija, y el conftest lo carga. El test de mano con rangos de ancho cero y evento de probabilidad 0 no se reescribe: los términos son el `project_finish` de `schedule_cpm`, la criticidad de A y de B sigue en 1, y `ssi_status` y `sensitivity_status` siguen en `no_evaluable`. El oráculo es el CPM determinístico, no el Monte Carlo contra sí mismo. No se toca el `== 1` ni el `WED_16`.

R-384: **sí.** No relaja la meta de 300 s ni el test. `test_s11_montecarlo_30k` sigue intocable: a 30 000 actividades son 1 000 iteraciones, `RiskConfig(seed=1, tornado_hours=0)` sin rangos, el reloj parte antes de `run_risk` y no hay calentamiento, y el límite que ya exige el test es 300 s. `TRACE["passes"]` de esa corrida es 1 000: no se saltan iteraciones aunque la varianza sea cero. `montecarlo_30k` no está en `activas` de `docs/qa/seccion11.toml`. Entra solo si la corrida de 30 000 por 1 000 baja de 300 s y qa-revisor aprueba la etapa. El implementador no edita ese archivo, ni `baseline.json`, ni el gate. Copiar los 49,1 s de la revisión (300 actividades y 5 iteraciones) no queda en verde.

R-385: **sí.** Si numba importó y `TRACE["passes"] > 0`, las aproximaciones no contienen «numba no se cargó» y dicen que el lote corrió en numba sobre los arrays del motor rápido. El assert de `tests/test_risk.py` que hoy exige la frase vieja pasa a exigir la nueva. No es un assert numérico. Las dos frases a la vez no quedan en verde. Si el calendario no cabe en el rápido, la nota dice que el lote fue el de referencia y no afirma que numba lo corrió. Ese camino no sirve de evidencia del lote: la comparación sería contra sí mismo. El oráculo es el import de numba y `TRACE["passes"]`, no una fecha calculada por el código nuevo.

R-386: **no** en el cierre del requisito, aunque los números no se relajan. Siguen intocados el término del evento cierto (`THU_16` por 4), el tornado 8 y 8, el tornado 8, 0 y 8, la convergencia del join en `TUE_16`, el SSI a menos de 0,05 de 1, Spearman mayor que 0,95, la crucialidad mayor que 0,95 (no está nombrada en la prosa, pero el oráculo son los asserts ya escritos), los hitos P50, P80 y P90 en `WED_16`, y las igualdades de `tests/test_e4_outputs.py` contra `schedule_cpm`. El conjunto del tornado de tres nodos sigue siendo A, B y C. Cambiar un esperado numérico para que el código nuevo pase no queda en verde. El mismo oráculo deja en pie dos asserts de nota que el cono vuelve falsos, y la línea de archivos no deja cambiarlos. Ver el hueco 1.

La cobertura que cita el contrato coincide con `docs/qa/E8/gate.json`: total 91,0 y ramas de engine 85,1. G12 falla si la cobertura baja de 90,5 (`stored - actual > 0,5` en `scripts/qa_gate.py`). El piso de ramas de engine es 85,0: la línea base está en 89,8, la meta de la sección 8.1 es 85, y el piso del gate es el mínimo entre la meta y la línea base menos 0,5. No es un hueco. `fast.py` limitado a un acceso a la caché, sin ramas nuevas, y `numeric/kernels.py` sin edición, no relajan un resultado.

## Huecos

1. Sobra, en los archivos del implementador, limitar `tests/test_e4_tornado.py` al comentario: faltan reemplazar ahí, o en R-382, los asserts «cronograma completo» y «No recorta al cono», que el test exige con `tornado_hours=8`, porque el cono los vuelve falsos y R-386 los deja como oráculo; el conjunto {A, B, C} no se toca.

2. Falta, en la fila R-381, que el término publicado de cada iteración iguale a `project_finish` de `schedule_cpm_reference` con esas duraciones, el máximo de los fin temprano de antes de ALAP (`ef_pre`, ADR-020 y ADR-022): «el término de cada actividad» es el early finish ya empaquetado, que ALAP puede mover, y no traba ese máximo.

3. Falta, en la definición de `TRACE` o en R-382, el conjunto visitado por cada actividad atrasada: `tornado_visited` solo suma, y una cadena de 5 puede sumar 15 sin probar que la última visita solo a esa y la primera a las cinco. Sobra, en esa misma fila, el «si el motor lo programa» del caso LOE o WBS: ADR-022 no deja el caso fuera.

## Comandos

En el worktree, sin pytest y sin red de 30 000:

- `git rev-parse --short HEAD` y `git branch --show-current`: `79fd58d`, rama `v3`. El mensaje es el contrato de E9 anterior al código.
- `git status --porcelain` antes de este archivo: vacío.
- Existencia de `tests/test_e9_risk.py` y `tests/property/test_e9_differential.py`: los dos faltan.
- `docs/qa/seccion11.toml`: `activas` tiene lectura, cpm, dcma y redundancia. No tiene `montecarlo_30k`.
- `tests/perf/test_seccion11.py`: `iterations = 1000` si el tamaño es 30 000, si no 5; `RiskConfig(seed=1, iterations=iterations, tornado_hours=0)`; el reloj no calienta; el límite pasado a `_report` es 300.
- `tests/test_e4_tornado.py`: el conjunto {A, B, C} y, además, «cronograma completo» y «No recorta al cono».
- `tests/test_risk.py`: `WED_16` por 5, criticidad 1 y 1, tornado 8 y 8, P50=P80=P90=`WED_16`, evento cierto `THU_16` por 4, tornado 8, 0 y 8, join `TUE_16`, Spearman `> 0.95`, crucialidad `> 0.95`, y la frase vieja de numba.
- `docs/qa/E8/gate.json`: `coverage_percent` 91.0; engine líneas 93,1 y ramas 85,1.

## Qué no pude verificar

No reejecuté pytest, el gate ni `gen_scale` a 30 000. El 91,0 y el 85,1 son los del gate de E8 ya versionado, no una medición de esta auditoría. No importé numba: R-385 depende de ese import en la corrida futura, y aquí no hay lote nuevo. No comprobé fechas contra el motor de referencia porque el código de E9 no existe y el contrato prohíbe usar un cronograma real. No abrí `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

## Segunda pasada

ACEPTADO

Segunda lectura del contrato en `da79484` (rama `v3`), no del texto de `79fd58d`. El rechazo de arriba se conserva. Los tests `tests/test_e9_risk.py` y `tests/property/test_e9_differential.py` siguen sin existir y el contrato los deja no verdes: no es rechazo. No se calculó la fecha de un cronograma. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

Los tres huecos quedaron cerrados en el contrato. `tests/test_e4_tornado.py` en el árbol todavía trae «cronograma completo» y «No recorta al cono»: es el código viejo, anterior a la implementación. El contrato ya no los usa como oráculo.

1. Cerrado. R-382 manda reemplazar esos dos asserts: no aparecen, y sí una frase de que el tornado solo recalcula la actividad atrasada y su cono. R-386 dice que no son oráculo numérico y que conservarlos no queda en verde. El conjunto {A, B, C} no se toca. La lista de archivos autoriza ese reemplazo, no solo el comentario.
2. Cerrado. R-381 exige que cada `finishes[i]` iguale al `project_finish` de `schedule_cpm_reference` con las duraciones de esa iteración: máximo de los fin temprano de antes de ALAP (`ef_pre`, ADR-020). El early finish empaquetado puede diferir si ALAP lo movió, y usarlo como término del proyecto no queda en verde. Hitos y convergencias igualan al `early_finish` empaquetado del reference. La fila R-381 de `TRAZABILIDAD.md` dice lo mismo.
3. Cerrado. `TRACE["cones"]` mapea cada código atrasado al conjunto visitado. En la cadena A–B–C–D–E, `cones["E"]` es `{E}`, `cones["A"]` es `{A,B,C,D,E}` y `cones["C"]` es `{C,D,E}`. `tornado_visited` es solo la suma de esos tamaños. Una suma de 15 sin los conjuntos no queda en verde. El caso LOE o WBS no se salta: el delta iguala al reference y el resumen no está en `cones`, porque el pase no lo programa y no mueve el término. ADR-022 dice lo mismo. En `fast.py`, el rollup de `TT_LOE` y `TT_WBS` va después del pase (`has_rollup` y `_attach_rollup`); `kernels.py` no los nombra.

R-380: **sí.** Igual que en la primera pasada. Columna de cada rango igual a `_consume_duration_rng` vía `sample_duration`. Iman-Conover no se reescribe: reordena y deja la nota de la diagonal si hay Cholesky; si no, deja la nota de Cholesky y no reordena. Un `random()` de evento por iteración y por evento, después de las duraciones. Probabilidad 1 suma; probabilidad 0 no suma y avanza el generador. Oráculo: `sample_duration` e `iman_conover` ya existentes.

R-381: **sí.** El criterio de la primera pasada sigue, y ahora el término publicado es el `project_finish` de la referencia. `TRACE["passes"]` igual a `iterations`, `TRACE["full_cpm"]` en 0, sin `_with_hours`, sin `schedule_cpm` en el bucle ni una vez por actividad del tornado, `parallel=True`, `prange`, `run_passes` sobre una copia, y al salir el cronograma original conserva sus fechas. Oráculo de fechas: `schedule_cpm_reference`, no el lote nuevo. Saltar pasadas por varianza cero, armar un `Schedule` por iteración o copiar el cuerpo de `run_passes` no queda en verde.

R-382: **sí.** Con `tornado_hours <= 0`, tornado vacío, `cones` vacío, `tornado_visited` en 0, y no aparecen las dos frases viejas. Con horas positivas, los conjuntos de la cadena son los de arriba y el delta de los casos de mano (8/8 y 8/0/8) y de la cadena iguala al reference con esa sola duración aumentada. Oráculo: `schedule_cpm_reference` y `TRACE["cones"]`. Comparar el delta solo contra el pase rápido no queda en verde.

R-383: **sí.** Sin cambio de números. `tests/property/test_invariant_e.py` sigue en verde, perfil qa, 500 ejemplos. Ancho cero y evento de probabilidad 0: los términos son el `project_finish` de `schedule_cpm`, la criticidad de la cadena de ese caso sigue en 1, y los dos estados quedan `no_evaluable`. Oráculo: CPM determinístico.

R-384: **sí.** No se bajan los 300 s ni se edita `tests/perf/test_seccion11.py`. Sigue en 30 000 por 1 000, `tornado_hours=0`, sin rangos, sin calentar, y `TRACE["passes"]` de esa corrida es 1 000. `montecarlo_30k` no está en `activas`. Entra en `seccion11.toml` solo si baja de 300 s y la etapa está aprobada. Copiar los 49,1 s no queda en verde.

R-385: **sí.** Sin cambio. Si numba importó y `passes > 0`, no queda «numba no se cargó» y la nota dice que el lote corrió en numba sobre los arrays del motor rápido. La frase vieja del test de mano se reemplaza por la nueva. El camino de referencia por calendario no soportado lo dice y no afirma que numba corrió el lote. Oráculo: el import y `TRACE["passes"]`.

R-386: **sí.** Los números siguen intocados: evento cierto, tornado 8/8 y 8/0/8, join, SSI, Spearman, crucialidad (ahora nombrada), P50 P80 P90, y las tablas de `tests/test_e4_outputs.py`. El conjunto {A, B, C} no se toca. Los dos asserts de nota se reemplazan como dice R-382; cambiar un esperado numérico no queda en verde. `fast.py` no se edita: `cached_compiled` ya existe y el contrato usa ese acceso, sin agregar otro. `numeric/kernels.py` sigue sin edición.

## Comandos de la segunda pasada

- `git rev-parse --short HEAD` y `git log -1 --oneline`: `da79484`, «segunda redaccion del contrato de E9». `841318a` es antepasado y trae este rechazo.
- `git status --porcelain` antes de este agregado: vacío.
- `tests/test_e4_tornado.py` sigue con el conjunto {A, B, C} y con las dos frases viejas. El contrato, no el test, es el que ordena reemplazarlas.
- `docs/qa/seccion11.toml`: `activas` sin `montecarlo_30k`. `test_s11_montecarlo_30k`: 1 000 iteraciones a 30 000, `tornado_hours=0`, límite 300, sin calentar.
- `cached_compiled` está en `src/atlaspmo/engine/fast.py` y devuelve lo que ya guardó la caché. `kernels.py` no menciona LOE ni WBS.
- `tests/test_e9_risk.py` y `tests/property/test_e9_differential.py`: siguen ausentes.

## Qué no pude verificar en la segunda pasada

No reejecuté pytest, el gate ni la red de 30 000. No importé numba. No comparé fechas contra la referencia: el lote nuevo no está escrito. No abrí `data/real/` ni `ATLASPMO_GOLDEN_DIR`.
