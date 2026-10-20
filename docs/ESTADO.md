# Estado

Memoria de trabajo entre sesiones. La fase 0 quedó en su rama. Nicolás pidió seguir hasta terminar el producto y dejar las iteraciones con P6 para después. Esta sesión construye la fase 1 en `fase-1`. No hay push.

## Fase 0 — lista para el gate

Rama `fase-0`, sin push. Base `main` `00f05a6`.

### Entregado

- `AGENTS.md` y los nueve agentes en `.grok/agents/`, solo `name` y `description`.
- Contrato de módulo, registro vacío, runner, UI vacía en español, `atlaspmo.bat`.
- Generador estructural y fixture `tests/fixtures/synthetic/minimal.xer`.
- `.gitignore`, deny de `data/real/**` y hook que rechaza XER, MPP y XML de cronograma fuera de `tests/fixtures/`.
- Docs de alcance, arquitectura, decisiones, XER y reglas. `XER_SPEC.md` no inventa campos.

### Evidencia (2026-10-20)

- `py -3.12 -m uv run python -m pytest` — 20 passed in 1.20s.
- `py -3.12 -m uv run python -m ruff check .` — All checks passed.
- `py -3.12 -m uv run python -m mypy src` — Success: no issues found in 21 source files.
- `uv run pytest` y `uv run streamlit` fallan en este equipo con `os error 5` (acceso denegado al .exe del venv). Por eso el bat usa `uv run python -m streamlit`. Ver ADR-004.
- `grok --trust-folder inspect --json` con cwd en el repo: `projectTrusted` true, `AGENTS.md` cargado (307 tokens aprox.), 3 reglas de permiso desde `.grok/config.toml`, y los nueve agentes de proyecto más los tres built-in.
- `atlaspmo.bat` sirve en `127.0.0.1`. `/_stcore/health` responde `ok`. `AppTest` ve el título AtlasPMO y el aviso de selector vacío.

### Supuestos abiertos

- La ruta de `ATLASPMO_GOLDEN_DIR` no se conoce. El deny del repo no la cubre.
- Nombres de campo XER: ninguno verificado.
- `/agents` en la TUI: esta sesión arrancó en el home. Hay que abrir Grok dentro del repo para verlos en el modal. `grok inspect` ya los lista.

### Qué revisar tú

- `AGENTS.md`, los nueve agentes y las reglas de privacidad.
- Reiniciar Grok en `C:\Users\nicolas.andrade\AtlasPMO` y abrir `/agents`.
- Si quieres tapar el directorio golden, la regla está en `docs/DECISIONES.md`.

## Fase 1 — en `fase-1`

Encima de `da62a85`. Sin push.

### Entregado

- Lector y escritor XER que reponen los bytes si nada cambia. Lector PMXML mínimo. Modelo, carga y validación.
- M1 sin DCMA 12, tres perfiles YAML, modo A de la ruta, Excel, PDF y manifiesto.
- Casos a mano en `tests/fixtures/synthetic/cases/`, generados por `scripts/build_cases.py`. `gen_synthetic.py` no cambió.
- `scripts/sanitize_fixture.py` anonimiza el encabezado y las columnas cuyo nombre contiene user, obs o db. No se usa sobre archivos reales.

### Evidencia (2026-10-20)

- `py -3.12 -m uv run python -m pytest -q --durations=5` — 36 passed in 1.95s.
- El call de `test_read_30k_under_15_seconds` duró 0.10s. Ese tiempo incluye escribir las 30 000 filas. La aserción cronometra solo `read_xer` y exige menos de 15 s. El elapsed interno no se imprimió.
- `py -3.12 -m uv run python -m ruff check .` — All checks passed.
- `py -3.12 -m uv run python -m mypy src` — Success: no issues found in 32 source files.

### Abierto, y no es un fallo de esta corrida

- Nicolás importa los sintéticos en P6 y devuelve los `p6_verified`.
- Contraste de M1 contra un XER real en su equipo.
- DCMA 12, modo B, motor CPM, Monte Carlo, MSPDI, DuckDB y el PBIP quedan para las fases siguientes.
- El tiempo interno de `read_xer` sobre 30 000 filas no se imprime. El test completo, que también escribe el archivo, es el que mide pytest. La aserción es `elapsed < 15` solo sobre la lectura.

## Siguiente

Fase 2 en `fase-2`: parser de `clndr_data` limitado al fixture, índice de tiempo laboral y CPM.
