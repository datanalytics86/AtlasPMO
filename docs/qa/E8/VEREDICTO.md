RECHAZADO

El gate de E8 está en verde y la redundancia cumple el contrato, pero hay un crítico y un importante abiertos. No autorizo activar `redundancia_30k`.

`docs/qa/E8/gate.json` (commit `71b42f3`) sale 0: G1–G12 en pass, G13 en info. 272 tests frente a 239. Cobertura 91,0. Engine en 93,1 de líneas y 85,1 de ramas, por encima de la meta. La meta pendiente de calendarios y de logic no bloquea (ADR-019). No reejecuté el gate.

H-1 y H-2 quedan abiertos en `docs/qa/E8/hallazgos.md`. H-1 es crítico: tres commits aún no publicados llevan una ruta de perfil en `docs/qa/E8/acciones.md`, y el commit que la borra también la lleva en el parche. Un push de `v3` la publicaría. G8 no la ve porque mira el árbol, y el árbol ya está limpio. H-2 es importante: la bitácora dice que la red fue PyPI, y `uv python install 3.12` baja CPython de python-build-standalone, no de PyPI.

H-3 y H-4 quedan menores. H-8 de E7 sigue menor y no se reabre. `tests/test_e7_match.py` pasó con el python del .venv del clon: 11 passed en 1,09 s.

## Segunda pasada

**APROBADO.**

HEAD `15494f4`. `origin/v3` (`0dd3e40`) sigue siendo ancestro: el próximo push sería fast-forward, 10 commits, sin push y sin `--force`. `d279d8e` ya no está en ninguna rama. El recorrido `origin/v3..HEAD` de `docs/qa/E8/acciones.md`, los parches de esos commits y sus mensajes no coinciden con el patrón de ruta de perfil. El sync no lleva `--directory`.

H-1 queda cerrado. H-2 queda cerrado: la bitácora dice que la red fue PyPI para uv y las dependencias, y que `uv python install` baja CPython de python-build-standalone. No hay push en la tabla. El árbol de producto, tests y gate es el de `71b42f3`; solo cambió esa bitácora. No hay crítico ni importante nuevo. H-3, H-4 y H-8 de E7 siguen menores y no bloquean.

Autorizo activar `redundancia_30k` en `seccion11.toml`. No la activo yo. La medición sigue bajo 180 s, con `mask_passes` 1.
