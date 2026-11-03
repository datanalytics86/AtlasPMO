# Hallazgos E8

HEAD `71b42f3`. El gate de `docs/qa/E8/gate.json` sale 0: G1–G12 en pass, G13 en info. 272 tests frente a 239. Cobertura 91,0. No reejecuté el gate. Reejecuté `tests/test_e7_match.py` con el python del .venv del clon: 11 passed en 1,09 s.

## H-1 — crítico

Una ruta de perfil sigue en el historial que `origin/v3` todavía no tiene. El patrón es el de G8. No la copio.

`d279d8e` la escribe en `docs/qa/E8/acciones.md`, en el `uv sync`, como argumento `--directory`. El archivo de ese commit tiene una coincidencia. `67d306e` y `ef5fc85` conservan el archivo y no tocan esa línea. `b8ae699` la quita del árbol; el parche de ese commit todavía la contiene. En HEAD el archivo tiene cero coincidencias. Los mensajes del rango `origin/v3..HEAD` también. El diff neto de ese archivo contra `origin/v3` tampoco: el alta y la baja se cancelan. El push no manda el neto. Manda los commits.

Esos cuatro commits son ancestros de HEAD y no de `origin/v3` (`0dd3e40`). La rama va 11 commits adelante. G8 pasa porque lee el árbol versionado, no los blobs anteriores. La sección 8.5 trata la violación de privacidad como crítico. Bloquea el cierre y bloquea el push.

## H-2 — importante

`docs/qa/E8/acciones.md` dice que la red fue PyPI. El segundo comando de la tabla, `py -3.11 -m uv python install 3.12`, no lo es. La documentación oficial de uv, en la página de versiones de Python, dice que CPython no publica binarios oficiales y que uv los baja de python-build-standalone. La sección 14.1.3 solo admite dependencias con uv desde PyPI, documentación oficial y el fetch o push de `v3`.

Los otros dos comandos sí caben en PyPI: instalar uv y el `uv sync` del grupo dev. No hay evidencia de una subida del repositorio ni de un cronograma. `origin/v3` sigue en `0dd3e40`. Es desviación de la spec. Bloquea. El preámbulo de la sección 14 llamaría crítico a cualquier límite duro; con la tabla 8.5 queda importante, y el efecto sobre el cierre es el mismo.

## H-3 — menor

`test_masked_pass_matches_the_reference_on_scale_200` arma el drop con los ocho primeros estados. Los confirmados se publican después. En la red de 200 esos ocho son `no_candidato`, así que el drop es el primer vínculo, no el conjunto que la confirmación quita.

No bloquea. En esa red medí 462 vínculos, 72 confirmados y la misma clasificación que la referencia. El conjunto confirmado, comparado al minuto con el motor de referencia, dio diferencia máxima 0. El primer vínculo también. `mask_passes` fue 1 y `LAST["path"]` fue `fast`. Una diferencia de más de un minuto en ese conjunto cambiaría el estado, y `_assert_same` del mismo test caería.

## H-4 — menor

`test_open_end_is_not_confirmed_even_if_dates_could_match` tiene un solo vínculo. El filtro lo deja `no_candidato`: no hay otro camino, y la regla de extremo no llega a correr.

No bloquea. El SS junto al FS de `test_s7_not_driver_and_not_redundant` sí es candidato. Quitarlo no mueve fechas ni holguras en la referencia, y los dos motores lo dejan `candidato_no_confirmado`. El índice de cobertura y el recorrido anterior coincidieron en 81 borrados de la red de 200, incluido el conjunto confirmado.

## H-8 de E7

Sigue menor y abierto en `docs/qa/E7/hallazgos.md`. No se reabre. El empaque de `a15628a` y `074792d` no lo convierte en importante: el diferencial de `tests/test_e7_match.py` compara el datetime exacto y pasó.

## Segunda pasada

**APROBADO.** HEAD `15494f4`. La reescritura fue solo de commits locales. No hubo push ni `--force`. `origin/v3` sigue siendo ancestro.

### H-1 — cerrado

`d279d8e` no es ancestro de HEAD (`merge-base --is-ancestor` sale 1) y ninguna rama ni etiqueta lo contiene. En los 10 commits de `origin/v3..HEAD` el archivo `docs/qa/E8/acciones.md` no coincide con el patrón de ruta de perfil, tampoco los parches ni los mensajes. Tres commits del rango son anteriores a ese archivo. El sync no lleva `--directory`. Un fast-forward de `v3` no publicaría la ruta.

### H-2 — cerrado

El texto vigente separa las dos redes. PyPI queda para uv y las dependencias. El resultado de `uv python install 3.12` dice que CPython 3.12.16 se bajó de python-build-standalone. No hay un push en la tabla. Frente a `71b42f3` el único cambio del árbol es ese párrafo y esa celda.

No aparece un crítico ni un importante nuevo. H-3 y H-4 siguen menores. H-8 de E7 sigue menor.
