# E1 · xer-io · tests en rojo (antes del arreglo)

Comando, salida 1. Los tests de fase 1 y del XER sintético pasan. Fallan la cadena de 60.000 y el byte indefinido de cp1252. El ciclo de tres actividades ya se reportaba (pasa).

Las rutas del árbol se acortaron a rutas del repositorio. No hay rutas de usuario.

```
py -3.12 -m uv run python -m pytest -q tests/test_e1_cycles.py tests/test_e1_cp1252.py tests/test_phase1.py tests/test_synthetic_xer.py --tb=line
```

```
F.F....................                                                                                                                                                                                                                  [100%]
================================================================================================================== FAILURES ===================================================================================================================
E   RecursionError: maximum recursion depth exceeded
src/atlaspmo/io/validate.py:181: RecursionError: maximum recursion depth exceeded
E   UnicodeDecodeError: 'charmap' codec can't decode byte 0x81 in position 51: character maps to <undefined>
    decoding with 'cp1252' codec failed

The above exception was the direct cause of the following exception:
E   ValueError: el archivo no decodifica como cp1252
src/atlaspmo/io/xer.py:95: ValueError: el archivo no decodifica como cp1252
=========================================================================================================== short test summary info ===========================================================================================================
FAILED tests/test_e1_cycles.py::test_serial_chain_of_60k_does_not_recurse - RecursionError: maximum recursion depth exceeded
FAILED tests/test_e1_cp1252.py::test_undefined_cp1252_bytes_round_trip - ValueError: el archivo no decodifica como cp1252
2 failed, 21 passed in 1.73s
```
