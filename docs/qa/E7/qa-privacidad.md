# qa-privacidad — E7

**Resultado: PASA.** No hay hallazgo. No aplica severidad.

Alcance: `git diff 8a268ca..HEAD` en la rama `v3`, HEAD `73666ebeddad0db948c2f53b978b3f78ebbf7bee`. Tres commits (`7dda433`, `4ec574c`, `73666eb`), 22 archivos, +2642 / −8. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se ejecutó Streamlit. No hubo commit ni push de este informe.

## Sección 14

| Límite | Evidencia | Resultado |
|---|---|---|
| No leer `data/real/` ni el golden | `git ls-files` no lista nada bajo `data/real/`. `.gitignore` sigue en `data/real/` y `git check-ignore` ignora `data/real/probe.xer`. La variable `ATLASPMO_GOLDEN_DIR` no está definida; no se imprimió ningún valor ni se abrió esa ruta. La única mención nueva es la prohibición en `docs/qa/E7/QC1_contrato.md`. El diff no abre ni lista esa carpeta. | cumple |
| Sin cronogramas fuera de `tests/fixtures/` | En el diff no hay `.xer`, `.mpp` ni XML con `APIBusinessObjects` o el espacio de nombres MSPDI. Los versionados siguen siendo 9 `.xer` y 2 `.xml`, todos bajo `tests/fixtures/`. No hay archivos sin seguimiento. | cumple |
| Sin rutas de perfil | En las 2642 líneas agregadas no hay `X:\Users\`, `\\Users\`, `/home/` ni `/Users/`. Lo mismo en el contenido completo de los 22 archivos. | cumple |
| Sin secretos | No hay `.env`, `.env.local` ni `.streamlit/secrets.toml` en el árbol. Ninguno está versionado. No hay asignación de clave, token ni llave privada en las líneas agregadas. | cumple |
| Red solo la permitida, y anotada | `docs/qa/E7/acciones.md` registra `py -3.12 -m uv add numba` (numba 0.68.0, llvmlite 0.50.0) y `py -3.12 -m uv add numpy` (numpy 2.5.4). El diff de `uv.lock` solo agrega URLs de `pypi.org` y `files.pythonhosted.org` (53). No hay índice privado. La rama está 3 commits adelante de su upstream y no hay push en la bitácora ni en los commits. | cumple |
| Git y sistema | El diff no empuja a `main`, no usa `--force` y no toca hooks, PATH ni el registro. Los dos `uv add` declaran wheel, sin compilador y sin administrador. | cumple |
| Controles que el diff no debilita | Sin cambios en `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks/` ni `scripts/qa_gate.py`. El deny de `data/real/**` y de `.env` sigue en `.grok/config.toml`. | cumple |

`.env` no está en `.gitignore`. No es hallazgo de E7: el diff no tocó esa regla, no hay `.env` en el árbol y un `.env` versionado lo rechazan el hook y G8.

## G8

`check_g8` sobre el árbol versionado: **pass**, «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red».

Eso cubre cronogramas y XML de cronograma fuera de fixtures, `data/real/`, nombres `.env`, el patrón de perfil en `.py`, `.md`, `.toml`, `.yaml`, `.yml`, `.bat` y `.json`, imports de `socket`, `requests`, `httpx`, `aiohttp`, `http.client` y `urllib.request` en `src/`, y `.streamlit/config.toml`.

Ese config no cambió: `address = "localhost"` y `gatherUsageStats = false`.

ERMHDR: los 9 `.xer` de `tests/fixtures/` tienen encabezado y todos los campos cumplen `ANON`, vacío o `N.N` (en la práctica `ERMHDR` o `ERMHDR` + `20.12`). `ermhdr_bad=0`. El diff no agrega fixtures. Los dos XML de fixtures no entran en el diff y no traen ruta de perfil.

El código nuevo (`fast.py`, `numeric/intervals.py`, `numeric/kernels.py`, tests E7) no importa red, no abre archivos y no lee el entorno. La caché de `schedule_cpm_fast` es un diccionario en memoria. `njit(cache=True)` escribe en `__pycache__/`, que sigue ignorado; no hay `.nbi` ni `.nbc` versionados.

## Comandos

- `git rev-parse HEAD`; `git branch --show-current`; `git merge-base --is-ancestor 8a268ca HEAD`; `git diff --name-status 8a268ca..HEAD`; `git diff --stat 8a268ca..HEAD`; `git log --oneline 8a268ca..HEAD`
- `git diff -U3 8a268ca..HEAD` de los archivos chicos, filtrado por patrones de privacidad
- `git diff -U0 8a268ca..HEAD` de `pyproject.toml`, `seccion11.toml`, `baseline.json`, `DECISIONES.md`, `ESTADO.md`, `TRAZABILIDAD.md`, `docs/qa/E7`, `cpm.py`, `options.py`, `numeric/__init__.py`
- `git status -sb`; `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'`; `git ls-files` de `*.xer`, `*.mpp`, `*.xml`, `.env`, `data/real/*`, `*.nbi`, `*.nbc`; `git ls-files --others --exclude-standard`; comprobación de que `ATLASPMO_GOLDEN_DIR` no está definida, sin imprimir el valor
- Script en memoria sobre los 22 archivos del diff: patrón de perfil de G8, asignaciones de secreto y URLs. `profile_hits=0`, `secret_hits=0`, `net_hits=0`
- `git diff --name-only 8a268ca..HEAD` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks` y `scripts/qa_gate.py` (vacío)
- `git check-ignore -v -- data/real/probe.xer .env .env.local .streamlit/secrets.toml`
- `py -3.12 -c` llamando a `check_g8`: pass
- Script en memoria sobre las líneas agregadas, los ERMHDR de `tests/fixtures/**/*.xer` y los hosts agregados en `uv.lock`
- `Test-Path` de `.env`, `.env.local` y `.streamlit/secrets.toml` (los tres ausentes)

No se corrió la aplicación Streamlit ni la suite. La lectura de código y de docs se hizo con las herramientas de búsqueda del workspace, sin abrir `data/real/`.
