# qa-privacidad — E7 ciclo 2

**Resultado: PASA.** No hay hallazgo. No aplica severidad.

Alcance: `git diff 8a268ca0c4f626df84ae6992c7bee5bab7597577..HEAD` en la rama `v3`, HEAD `6052e9b4401f6c8c360d6038e8f0fe8070336dc6`. El base es ancestro. Cinco commits: `4ec574c`, `7dda433`, `73666eb`, `de37f8a`, `6052e9b`. 26 archivos, +2960 / −8. El producto del ciclo 2 es `de37f8a` (7 archivos, +165 / −24). `6052e9b` solo documenta el rechazo del ciclo 1 (4 archivos, +177). `73666eb..HEAD` son 11 archivos, +342 / −24. Al empezar, `git status --porcelain` estaba vacío: no hay otro trabajo sin commitear. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se ejecutó Streamlit ni la suite. No hubo commit ni push de este informe.

## Sección 14

| Límite | Evidencia | Resultado |
|---|---|---|
| No leer `data/real/` ni el golden | `git ls-files` no lista nada bajo `data/real/`. `.gitignore` línea 2 sigue en `data/real/` y `git check-ignore -q -- data/real/probe.xer` sale 0. `ATLASPMO_GOLDEN_DIR` no está definida; no se imprimió ningún valor ni se abrió esa ruta. Las menciones del diff (`QC1_contrato.md`, `qa-spec.md`, `DECISIONES.md`, `ESTADO.md`, `TRAZABILIDAD.md`) son la prohibición, no una lectura. | cumple |
| Sin cronogramas fuera de `tests/fixtures/` | El diff no trae `.xer`, `.mpp` ni `.xml`. Los versionados son 9 `.xer` y 2 `.xml`, todos bajo `tests/fixtures/`. No hay `.mpp`. | cumple |
| Sin rutas de perfil | En las 2960 líneas agregadas y en el texto completo de los 26 archivos, el patrón de G8 no coincide (0). El ciclo 2 (`73666eb..HEAD`) tampoco (0). `NUMBA_CACHE_DIR` y `NUMBA_CACHE_LOCATOR_CLASSES` no están definidas. | cumple |
| Sin secretos | No hay `.env`, `.env.local` ni `.streamlit/secrets.toml` (`Test-Path` ausente; `git ls-files` no los lista). En las líneas agregadas no hay asignación de clave, token ni llave privada, ni correo. | cumple |
| Red solo la permitida, y anotada | `docs/qa/E7/acciones.md` registra `py -3.12 -m uv add numba` (numba 0.68.0, llvmlite 0.50.0) y `py -3.12 -m uv add numpy` (numpy 2.5.4). El diff de `uv.lock` agrega 54 URLs: 2 de `pypi.org` y 52 de `files.pythonhosted.org`. `numba`, `llvmlite` y `numpy` quedan con `source = { registry = "https://pypi.org/simple" }`. No hay otro host. El ciclo 2 no toca `uv.lock`, `pyproject.toml` ni `acciones.md`, y sus líneas agregadas no traen URL (0). | cumple |
| Git | El diff no empuja a `main`, no reescribe historia publicada y no toca hooks. `git status -sb`: `v3` va 5 commits adelante de `origin/claude/beautiful-goodall-m0q2zj` (`git rev-list --left-right --count` da `5 0`). `refs/remotes/origin/v3` no existe. En `git reflog --date=iso -30` los cinco commits de E7 son `commit:`; no hay entrada de push. `acciones.md` no anota push. | cumple |
| Sistema | El diff no toca PATH, registro ni servicios. Los dos `uv add` de la bitácora declaran wheel, sin compilador y sin administrador. Este ciclo no repitió esas instalaciones. | cumple |
| Controles que el diff no debilita | `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks/` y `scripts/qa_gate.py` está vacío. Siguen el deny de `data/real/**` y de `.env` en `.grok/config.toml`, y los hooks `reject-schedules`, `commit-g8` y `push-v2-g8`. | cumple |

`.env` y `.env.local` no están en `.gitignore` (`git check-ignore -q` sale 1). No es hallazgo de E7: el diff no tocó esa regla, no hay `.env` en el árbol, y un `.env` versionado lo rechazan el hook y G8.

## G8

`check_g8` sobre el árbol versionado: **pass**, «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red».

Eso cubre cronogramas y XML de cronograma fuera de fixtures, `data/real/`, nombres `.env`, el patrón de perfil en `.py`, `.md`, `.toml`, `.yaml`, `.yml`, `.bat` y `.json`, imports de `socket`, `requests`, `httpx`, `aiohttp`, `http.client` y `urllib.request` en `src/`, y `.streamlit/config.toml`.

Ese config no cambió: `address = "localhost"` y `gatherUsageStats = false`. Un recorrido AST de `src/**/*.py` y de los `.py` del diff no encontró esos imports.

ERMHDR: los 9 `.xer` de `tests/fixtures/` tienen encabezado. `ermhdr_bad=0`. Ocho traen el único campo `20.12`; uno no trae campos después de `ERMHDR`. El diff no agrega fixtures. Esos 9 `.xer` y los 2 `.xml` tampoco contienen el patrón de perfil de G8.

El código nuevo y el arreglo de `de37f8a` (`fast.py`, `numeric/intervals.py`, `numeric/kernels.py`, `cpm.py`, `options.py`, tests E7) no importa red, no abre archivos y no lee el entorno. La caché de `schedule_cpm_fast` es el diccionario `_CACHE` en memoria (tope 4). Las notas de restricción usan `task_code` o `task_id` del cronograma ya cargado; no hay `print` ni logging en `fast.py` ni en `kernels.py`.

## Caché de numba

`src/atlaspmo/numeric/kernels.py` aplica `njit(cache=True)` a `run_passes`. Con `NUMBA_CACHE_DIR` vacío, el locator por defecto de la numba instalada es `InTreeCacheLocator` (`.venv/Lib/site-packages/numba/core/caching.py`): el directorio es `__pycache__` junto al `.py`, e índice `.nbi` más datos `.nbc`. En disco están `src/atlaspmo/numeric/__pycache__/kernels.run_passes-22.py312.nbi` y `kernels.run_passes-22.py312.1.nbc` (y tres `.pyc`). `git check-ignore -v` los atribuye a `.gitignore` línea 9 (`__pycache__/`). `git ls-files` de `*.nbi`, `*.nbc` y de esa carpeta no devuelve nada. El ciclo 2 no cambia esa línea. Un `.nbc` suelto al lado del módulo no estaría ignorado (`git check-ignore -q` sale 1); numba no lo escribe ahí y no hay ninguno versionado.

## Comandos

- `git rev-parse HEAD`; `git branch --show-current`; `git status -sb`; `git merge-base --is-ancestor 8a268ca0c4f626df84ae6992c7bee5bab7597577 HEAD`; `git log --oneline 8a268ca0c4f626df84ae6992c7bee5bab7597577..HEAD`; `git diff --stat` y `--name-status` del mismo rango; `git status --porcelain` (vacío al empezar); `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'`; `git rev-list --left-right --count 'HEAD...@{u}'`
- `git show --stat de37f8a`; `git show --stat 6052e9b`; `git diff --stat` y `--name-status 73666eb..HEAD`
- `git diff -U3 73666eb..de37f8a` de `kernels.py`; `git diff -U1` de `cpm.py` y `options.py` contra el base
- Script en memoria (`py -3.12`) sobre `git diff -U0 8a268ca0c4f626df84ae6992c7bee5bab7597577..HEAD` y sobre el texto de los 26 archivos: patrón de perfil de G8, asignaciones de secreto, llaves y tokens, correos, URLs por host y por archivo, imports de red con `ast`. Líneas agregadas 2960. `PROFILE_HITS=0`, `SECRET_HITS=0`, `KEY_HITS=0`, correos 0, imports 0. Hosts: `pypi.org` 2, `files.pythonhosted.org` 52, todos en `uv.lock`. El mismo patrón sobre `73666eb..HEAD`: perfil 0, URLs 0
- `py -3.12` llamando a `check_g8`: pass. Variables `ATLASPMO_GOLDEN_DIR`, `NUMBA_CACHE_DIR` y `NUMBA_CACHE_LOCATOR_CLASSES` no definidas, sin imprimir valores
- Mismo proceso sobre los ERMHDR de `tests/fixtures/**/*.xer` (cp1252, primera línea) y el patrón de perfil en esos `.xer` y en los `.xml`: `XER_COUNT=9`, `ERMHDR_BAD=0`, `FIXTURE_XER_PROFILE=[]`, `XML_COUNT=2`, `FIXTURE_XML_PROFILE=[]`
- `git ls-files` de `*.xer`, `*.mpp`, `*.xml`, `.env`, `data/real`, `*.nbi`, `*.nbc`, `__pycache__`
- `git check-ignore -v` de `data/real/probe.xer`, `.streamlit/secrets.toml` y de los `.nbi`, `.nbc` y `.pyc` reales bajo `src/atlaspmo/numeric/__pycache__/`; `git check-ignore -q` de `.env`, `.env.local` y de un `.nbc` hermano del módulo
- `Test-Path` de `.env`, `.env.local` y `.streamlit/secrets.toml`
- `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks` y `scripts/qa_gate.py` (vacío)
- `git rev-parse --verify refs/remotes/origin/v3` (no existe); `git reflog --date=iso -30`
- Lectura de `.streamlit/config.toml`, `.gitignore`, `.grok/config.toml`, `.pre-commit-config.yaml`, `docs/qa/E7/acciones.md` y del locator en `numba/core/caching.py` de la numba del `.venv`

No se corrió la aplicación Streamlit ni la suite. La lectura de código y de docs se hizo con las herramientas de búsqueda del workspace, sin abrir `data/real/`.
