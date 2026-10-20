# AtlasPMO

Aplicación local para analizar cronogramas de Primavera P6 y MS Project.
La especificación está en [docs/MEGAPROMPT.md](docs/MEGAPROMPT.md).
El avance está en [docs/ESTADO.md](docs/ESTADO.md).

## Instalación

Hace falta Python 3.12 y [uv](https://docs.astral.sh/uv/). En este equipo, sin administrador:

```
py -3.12 -m pip install --user uv
```

En la raíz del repositorio, un paso deja el entorno de desarrollo listo:

```
py -3.12 -m uv sync --group dev
```

Comprobar:

```
py -3.12 -m uv run python -m pytest
py -3.12 -m uv run python -m ruff check .
py -3.12 -m uv run python -m mypy src
```

## Uso

`atlaspmo.bat` abre la interfaz en localhost. Equivale a:

```
uv run python -m streamlit run src/atlaspmo/ui/app.py
```

En este equipo `uv run pytest` y `uv run streamlit` fallan con `os error 5`.
El detalle está en [docs/DECISIONES.md](docs/DECISIONES.md) (ADR-004).
`AGENTS.md` sigue citando `uv run pytest`.

La pantalla lista los módulos en español y no carga un archivo.
El manual está en [docs/MANUAL_USUARIO.md](docs/MANUAL_USUARIO.md).
La app no usa red ni telemetría (`browser.gatherUsageStats = false`).

## Qué no se commitea

Los cronogramas reales no entran al repositorio. Van en `ATLASPMO_GOLDEN_DIR`,
fuera de cualquier carpeta que abra Grok Build. `data/real/` está en
`.gitignore`. Un hook rechaza `*.xer`, `*.mpp` y XML de cronograma fuera de
`tests/fixtures/`. Esta aplicación no abre esa carpeta.
