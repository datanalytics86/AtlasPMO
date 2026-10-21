# E1 · xer-io (B-05, B-20)

Rama `e1-xer-io`, desde `7dbb92a`. Sin push. Worktree propio del agente; no se tocó `engine`, `calendars`, el gate, `skips.toml`, oráculos ni perfiles.

## Archivos

- `src/atlaspmo/io/validate.py` — detección de ciclos con pila explícita, sin recursión de Python.
- `src/atlaspmo/io/xer.py` — los bytes sin carácter en cp1252 se leen, se reescriben igual y quedan en `XerFile.parse_notes`.
- `src/atlaspmo/io/load.py` — esa nota se copia a `Schedule.parse_notes` (campo que ya existía; no se añadió ninguno al modelo).
- `tests/test_e1_cycles.py` — cadena de 60.000 en memoria y ciclo de tres.
- `tests/test_e1_cp1252.py` — celda con `0x81`, `0x8D`, `0x8F`, `0x90` y `0x9D`.
- `docs/XER_SPEC.md` — el párrafo que rechazaba esos bytes ahora dice que se preservan y se anotan.
- `docs/qa/E1/rojo-xer.md` — salida en rojo, guardada antes del arreglo.

## Commits

- `c24e02b` test(io): B-05 y B-20 en rojo antes del arreglo
- `8601485` fix(io): deteccion de ciclos iterativa (B-05)
- `1ebebd5` fix(io): preservar bytes indefinidos de cp1252 (B-20)

## Comandos

En el worktree, con `py -3.12 -m uv run`.

Rojo, antes del arreglo (salida 1). Detalle en `docs/qa/E1/rojo-xer.md`.

```
python -m pytest -q tests/test_e1_cycles.py tests/test_e1_cp1252.py tests/test_phase1.py tests/test_synthetic_xer.py --tb=line
```

```
FAILED tests/test_e1_cycles.py::test_serial_chain_of_60k_does_not_recurse - RecursionError: maximum recursion depth exceeded
FAILED tests/test_e1_cp1252.py::test_undefined_cp1252_bytes_round_trip - ValueError: el archivo no decodifica como cp1252
2 failed, 21 passed in 1.73s
```

El ciclo de tres ya pasaba: la versión recursiva lo reportaba. La cadena larga reventaba en `validate.py:181`. `read_xer_bytes` rechazaba `0x81`.

Verde, después del arreglo (salida 0):

```
23 passed in 1.92s
```

```
python -m ruff check src/atlaspmo/io tests/test_e1_cycles.py tests/test_e1_cp1252.py
```

```
All checks passed!
```

```
python -m mypy src
```

```
Success: no issues found in 56 source files
```

La cadena de 60.000 entra en ese segundo y medio junto con el resto del subconjunto. No se escribió un XER de 60.000 al repositorio.

## Qué quedó hecho

B-05. El recorrido es un DFS con pila de marcos `(nodo, índice de arista)`. Un ciclo sigue siendo un hallazgo `cycle` con el texto `Ciclo: A → B → C → A` (una vez por arista de retorno, como antes). La cadena en serie no informa ciclo y no lanza `RecursionError`.

B-20. La decodificación usa `cp1252` con `surrogateescape`. Esos cinco bytes vuelven al mismo valor al escribir. La nota es: `Aproximación: bytes sin carácter definido en cp1252 (0x81, 0x8D, 0x8F, 0x90, 0x9D) preservados para el round-trip.` Un BOM UTF-8 se sigue rechazando. No hay columnas nuevas.

## Supuestos

- El surrogate no es un carácter de P6: solo transporta el byte para el round-trip. La aproximación queda visible en `parse_notes`.
- Si `drop_rows` no borra nada, conserva las notas. Si borra filas, relee los bytes que quedan y recalcula la nota.

## No verificado

- El CPM sobre la cadena de 60.000. La aceptación de B-05 lo pide; este brief dice que no hace falta correrlo. Queda para `motor-cpm`.
- Que P6 importe un XER con `0x81`.
- El gate completo (`scripts/qa_gate.py` no es de este agente).
- No leí `data/real` ni `ATLASPMO_GOLDEN_DIR`. No hubo push.
