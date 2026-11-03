# Acciones de red y de sistema — E8

Este equipo no tenía el clon, ni `uv` en PATH, ni CPython 3.12. No se editó PATH, el registro ni `git config`. No se corrió `uv python update-shell`. La red fue PyPI para uv y las dependencias, y la descarga de CPython de python-build-standalone que hace `uv python install`. Al cierre, el push de `v3` si el veredicto lo autoriza. No hay push en esta tabla hasta que ocurra.

| Comando | Motivo | Resultado |
|---|---|---|
| `py -3.11 -m pip install --user uv` | no había `uv` invocable | uv 0.13.6 |
| `py -3.11 -m uv python install 3.12` | el proyecto pide 3.12 y el launcher solo tenía 3.11 y 3.14 | CPython 3.12.16 en el almacén de uv, bajado de python-build-standalone |
| `py -3.11 -m uv sync --group dev --python 3.12` | el clon no tenía `.venv` | exit 0; grupo dev, incluido hypothesis, mypy, numba, numpy, pytest y ruff |
| `git push -u origin v3` | cierre de E8 aprobado en la segunda pasada | fast-forward `0dd3e40..5a7ee95`, sin `--force` |
