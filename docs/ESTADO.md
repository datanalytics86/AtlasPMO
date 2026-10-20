# Estado

Memoria de trabajo entre sesiones. La Fase 1 no empieza sin aprobación del gate.

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

## Siguiente

Gate. Si lo apruebas, Fase 1: lector y escritor XER.
