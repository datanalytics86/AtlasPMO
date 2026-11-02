# logica-red — E8

No hubo corrida en rojo previa. El agente de implementación se detuvo sin escribir código. Los tests de `tests/test_e8_mask.py` y `tests/property/test_e8_differential.py` se escribieron junto con el código y después se ejecutaron. No hay un log rojo que citar.

## Qué hace la confirmación rápida

El filtro por origen no se tocó. `_confirm` y `_join` siguen: un subconjunto que pasa solo no se une a otro hasta que el conjunto, quitado entero, deja el CPM quieto. El motor de referencia sigue siendo el oráculo. No hay cono. El núcleo numba no se modificó.

1. La base corre el CPM rápido una vez y reutiliza el CSR compilado.
2. Un vínculo se aparta de la bisección, sin confirmarlo, solo si es el único predecesor que fija el inicio temprano, ese inicio está después de la fecha de datos ya ajustada al calendario, y no hay actual ni restricción que pueda sostener la fecha (ni LOE ni WBS). Quitarlo tiene que mover el inicio. Si la prueba no alcanza, el vínculo sigue en la bisección.
3. Sobre el resto se hace un solo pase enmascarado. Si los minutos (fechas y holguras) igualan a la base, cualquier subconjunto conserva esos minutos: agregar de vuelta un vínculo no afloja una fecha que ya coincidía en los dos extremos. La holgura libre no cumple eso. Se calcula, con la misma resta del núcleo, qué sucesoras empatan el mínimo, y el atajo solo responde sí si cada actividad conserva una de esas sucesoras. Si no, se corre el pase enmascarado.
4. La cobertura de inicios y fines usa un índice armado una vez. La regla es la de antes: no se confirma un borrado que deja un evento sin vínculos.

`engine="reference"` no usa el atajo. Reconstruye el cronograma y llama al motor de referencia.

## Igualdad

En esta máquina, el diccionario de estados del rápido y el de la referencia coincidieron en `gen_scale` de 40 y de 100 actividades. En 200, 400, 800 y 2 000 el conteo de estados del rápido quedó igual al de la versión que hacía un pase por candidato. `LAST["path"]` fue `fast` y `mask_passes` fue 1.

## Rendimiento

El detalle y el reloj de 30 000 están en `docs/qa/E8/perf.md`. 14,839 s, límite 180 s. No se editó `seccion11.toml` ni `baseline.json`.
