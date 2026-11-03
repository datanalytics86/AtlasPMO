APROBADO

HEAD `0750b2d`, rama `v3`. El producto revisado es el de `436bc55` sobre `cf35f17`. `0750b2d` solo agrega `docs/qa/E9/gate.json` y `gate.md`. No reejecuté el gate ni la red de 30 000. No leí `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No activé `montecarlo_30k`.

`docs/qa/E9/gate.json` sale 0: G1–G12 en pass, G13 en info. 283 tests frente a 272. Cobertura de la etapa 91,1. La línea TOTAL del reporte mezcla ramas y dice 88 %; no es la cifra de la etapa y no la corrijo. G6 corrió las cuatro metas activas: `lectura_30k`, `cpm_30k`, `dcma_30k` y `redundancia_30k`. `montecarlo_30k` no está en `activas`.

H-1 queda cerrado. H-2 queda cerrado. No hay crítico ni importante abierto. El detalle está en `docs/qa/E9/hallazgos.md`.

La ventana nueva es una sola recompilación, antes del lote, y solo si alguna hora redondeada supera `compiled.duration`. No es un `Schedule` por iteración. En el evento de 176 h conté una llamada a `_with_hours`. Con un rango fijo de 4 h, por debajo de la base, conté cero. El test que parchea `_with_hours` sigue cubriendo el caso sin rangos ni eventos: ahí `_needs_room` es falso. Si la recompilación no devuelve tablas o el segundo lote lanza `CalendarLimitError`, `_reference_instead` quita la nota de numba y pone la de fallback. Está en el código. Al forzar esa excepción la nota cambió, `passes` quedó en 0 y `full_cpm` en las iteraciones. Con probabilidad 0,5 ese forzamiento igualó un segundo sorteo, no el de la semilla. No lo abro: no hallé un cronograma que el motor rápido pueda correr y que entre ahí. El evento de 176 h, la mezcla de 8 h y 184 h, un lag negativo y dos rangos hasta 80 h se quedan en el lote, conservan la nota de numba y el término iguala al reference.

Autorizo activar `montecarlo_30k` en `seccion11.toml`. No la activo yo. `docs/qa/E9/perf.md` deja el pytest en 63,569 s, límite 300 s. El test exige 1 000 términos; no afirmo `passes` de esa impresión porque el archivo no los trae. La fila hermana sí: 61,581 s, `passes` 1 000, `full_cpm` 0. Esa red no trae rangos ni eventos, así que no recompila por pico. La varianza cero no salta el bucle.

Reejecuté, con el Python del `.venv`, los dos tests nuevos de `tests/test_e9_risk.py`: 2 passed en 24,47 s.
