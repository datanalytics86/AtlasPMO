# qa-revisor — E8

Revisión de cierre de E8, brecha B-02, HEAD `71b42f3`. Se contrastaron las secciones 8.4, 8.5, 10.3 (E8), 11 y 14 de `docs/MEGAPROMPT_v3.md`, ADR-004, ADR-011, ADR-016, ADR-019, ADR-020 y ADR-021, el contrato y la segunda pasada de `docs/qa/E8/qa-spec.md`, `QC1_contrato.md`, `perf.md`, `logica-red.md`, `acciones.md`, `gate.md`, `gate.json`, las filas R-370 a R-376 de `docs/qa/TRAZABILIDAD.md` y el código de confirmación. No se reescribió el RECHAZADO de la primera pasada de qa-spec. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó producto, tests, gate, umbrales ni `seccion11.toml`.

## Veredicto

**RECHAZADO.** El motor y la confirmación cumplen R-370 a R-376, y el gate está en verde. H-1 (crítico) y H-2 (importante) siguen abiertos. Con la sección 8.5 eso impide el cierre. No autorizo activar `redundancia_30k`.

## Gate

`docs/qa/E8/gate.json` sale 0. No lo reejecuté. G1 a G12 en pass, G13 en info porque no hay `sabotaje.md`. 272 tests frente a 239. Cobertura total 91,0, 0,2 bajo el 91,2 de E7: G12 admite hasta 0,5. Nueve tests de rendimiento quedaron deseleccionados de la suite, como en el diseño de G6.

| Paquete | Línea base | Gate E8 | Efecto |
|---|---|---|---|
| engine, líneas | 95,0 | 93,1 | sobre la meta 90 |
| engine, ramas | 89,8 | 85,1 | sobre la meta 85 |
| logic, líneas | 88,6 | 89,2 | meta pendiente |
| logic, ramas | 75,3 | 80,1 | meta pendiente |
| calendars, ramas | 81,6 | 81,6 | meta pendiente |

El piso de G4 es el mínimo entre la meta y la línea base menos 0,5. Engine ya superaba la meta, así que puede bajar hasta ella. 85,1 no la cruza. `074792d` quitó dos ramas muertas del empaque: el resultado vacío no llega a armar actividades, y un grafo acíclico siempre tiene un extremo abierto. Quitar el retorno anticipado no cambia el resultado. Logic subió respecto de la línea base. La distancia a la meta queda informada y no bloquea (ADR-019). El código nuevo de la confirmación entra en ese paquete y no lo hizo caer.

G3 pasó con `python -m pytest`. `uv run pytest` no arranca en este equipo. La frase «No suitable Python runtime found» solo se acepta como hueco de entorno después de que `python -m pytest` ya salió 0, y solo en el intento de `uv` (ADR-004, ADR-011). Una suite en rojo sigue fallando G3. El cambio del gate es una línea, en `ef5fc85`, y el mensaje cita esos ADR. G11 pasa.

G6 pasó las metas activas: `lectura_30k`, `cpm_30k` y `dcma_30k`. `docs/qa/seccion11.toml` no lista `redundancia_30k`. El assert de `cpm_30k` sigue en 0,5 s. No se relajó.

## Requisitos

R-370. El diferencial de `tests/property/test_e8_differential.py` usa el perfil qa, redes de a lo más 8 actividades y descarta el ejemplo si `LAST["path"]` no es `fast`, para no comparar la referencia consigo misma. Los casos fijos de la sección 7 están en `tests/test_e8_mask.py`: cuatro vínculos, lag positivo y negativo, feriado, media jornada, jornada de 24 h, cada restricción soportada, retained y progress override, hitos, LOE, WBS, par SS+FF, vínculo que no es driver y cadena con un atajo. El oráculo es `classify_links` con `engine="reference"`. Entraron en los 272 del gate.

R-371. `test_confirmation_masks_edges_and_keeps_the_calendar_tables` cuenta `schedule_cpm`, `schedule_cpm_fast`, `_compile` y `build_tables` mientras `mask_passes` ya subió, y compara el id de las tablas de calendario. El filtro por origen no se reescribió: el diff de E8 no cambia `_candidate_ids` ni `_origin_candidates`.

R-372. `tests/test_e2_joint.py` sigue exigiendo un solo `redundante_confirmado` en el par de dos FS iguales, y la limpieza quita una fila. `test_mutual_pair_matches_the_reference` iguala ese caso a la referencia. El atajo no confirma el par entero: si quitar todos los candidatos mueve el CPM, `quiet` no se arma y la bisección con `_join` sigue igual que ADR-016.

R-373. La lista a mano de seis actividades no sale de `_candidate_ids`. El camino A–B–C sigue en `tests/oracle/pathlen.py`, que no importa `src/atlaspmo`. El par SS+FF sale `protegido` y no entra a candidatos.

R-374. No hay cono. El pase enmascarado reconstruye los CSR sin escribir los arrays compilados ni las tablas de calendario, y llama al mismo núcleo. En la red chica, el vínculo `13` se compara con la referencia. En `gen_scale` de 200, la clasificación del rápido y la de la referencia coincidieron (462 vínculos, 72 confirmados, `mask_passes` 1). El conjunto confirmado, al minuto, dio diferencia máxima 0 contra el motor de referencia. H-3 registra que el test de 200 no elige ese conjunto; no esconde una diferencia mayor que la tolerancia de `_same`.

R-375. El reloj de `perf.md` es 14,839 s, límite 180 s, `mask_passes` 1. No se copian los 52,5 s de la revisión, que eran 300 actividades. Lo medí aparte, con el CPM ya caliente: 30 000 actividades, 69 996 vínculos, 3,120 s, `mask_passes` 1, camino `fast`. Las dos cifras caben en 180 s. La diferencia cabe en un núcleo frío dentro del propio test. No autorizo el alta en `seccion11.toml`: ADR-019 la reserva al cierre de una etapa aprobada, y esta no lo está.

R-376. La regla de no dejar un inicio o un fin sin vínculo está en `_events_stay_covered`, antes de aceptar el atajo. H-4 dice que el test que lleva ese nombre no llega a la regla. El SS junto a un FS de 16 h sí llega: quitarlo no mueve fechas ni holguras, y los dos motores lo rechazan. El índice nuevo y el recorrido anterior coincidieron en 81 borrados de la red de 200.

`links_that_must_move` solo aparta un vínculo. No confirma ninguno. Hace falta un solo driver, fecha estrictamente posterior a la de datos ya ajustada, y que no haya actual, rollup ni restricción que pueda sostenerla. Si la pista no alcanza, el vínculo sigue en la bisección.

## Empaque del CPM

`a15628a` y `074792d` (ADR-020, R-364) convierten `ScheduledActivity` en `NamedTuple` y arman las fechas en bloque. Los segundos de un real y el fin de proyecto de un extremo abierto se reponen después. El assert de `cpm_30k` no se tocó. `perf.md` registra 0,396 s, 0,415 s y 0,378 s. Con el núcleo ya caliente medí 0,152 s, 0,202 s y 0,172 s. Las dos series quedan bajo 0,5 s. El diferencial de E7 está en `tests/test_e7_match.py` y `tests/property/test_e7_differential.py`, y el gate los contó entre los 272. Reejecuté solo el primero: 11 passed en 1,09 s. H-8 de E7 no se reabre.

## Lo que bloquea

El detalle está en `docs/qa/E8/hallazgos.md`.

H-1, crítico. La ruta de perfil ya no está en el árbol y G8 pasa. Sigue en `d279d8e`, `67d306e` y `ef5fc85`, y en el parche de `b8ae699`. `origin/v3` está en `0dd3e40`, 11 commits atrás. Publicar la rama publicaría la ruta.

H-2, importante. La frase «la red fue PyPI» no cubre `uv python install 3.12`. La documentación oficial de uv dice que ese CPython sale de python-build-standalone.

## Segunda pasada

**APROBADO.**

Comprobé el historial con git, sin copiar rutas. HEAD `15494f4`. `git merge-base --is-ancestor origin/v3 HEAD` sale 0: `0dd3e40` sigue siendo ancestro y el push de `v3` sería fast-forward (10 commits). El reflog reciente no tiene push ni `--force`. `d279d8e` sale 1 en `--is-ancestor` contra HEAD y `git branch --contains` / `git tag --contains` no lo listan.

Recorrí `origin/v3..HEAD`. Cero coincidencias del patrón de ruta de perfil en los mensajes, en cada parche y en cada versión de `docs/qa/E8/acciones.md` que ya existe en ese rango. Cero commits con `--directory`. El archivo vigente dice que la red fue PyPI para uv y las dependencias, y que `uv python install` baja CPython de python-build-standalone. La tabla no tiene push.

`git diff 71b42f3 15494f4` solo toca `docs/qa/E8/acciones.md` (dos líneas). Producto, tests, gate y `seccion11.toml` no se movieron. La revisión de R-370 a R-376, del empaque y del gate queda en pie. H-1 y H-2 quedan cerrados. No hay crítico ni importante nuevo. H-3, H-4 y H-8 de E7 siguen menores.

Autorizo activar `redundancia_30k`. No edito `seccion11.toml`. Sigue valiendo la medición bajo 180 s con `mask_passes` 1: 14,839 s en `perf.md` y 3,120 s en la pasada con el núcleo ya caliente.
