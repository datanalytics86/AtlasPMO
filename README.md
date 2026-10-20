# AtlasPMO

Aplicación local para analizar cronogramas de Primavera P6 y MS Project.
La especificación está en [docs/MEGAPROMPT.md](docs/MEGAPROMPT.md).
El avance está en [docs/ESTADO.md](docs/ESTADO.md).

## Instalación

Hace falta Python 3.12 y [uv](https://docs.astral.sh/uv/). En este equipo, sin administrador:

```
py -3.12 -m pip install --user uv
```

Luego, en la raíz del repositorio:

```
uv sync --group dev
uv run pytest
```

## Uso

`atlaspmo.bat` abre la interfaz en localhost. Equivale a:

```
uv run streamlit run src/atlaspmo/ui/app.py
```

La app no usa red ni telemetría (`browser.gatherUsageStats = false`).

## Qué no se commitea

Los cronogramas reales no entran al repositorio. Van en `ATLASPMO_GOLDEN_DIR`,
fuera de cualquier carpeta que abra Grok Build. `data/real/` está en
`.gitignore`. Un hook rechaza `*.xer`, `*.mpp` y XML de cronograma fuera de
`tests/fixtures/`.

La Fase 0 no lee esos archivos. La conformidad la ejecuta Nicolás en su equipo.
