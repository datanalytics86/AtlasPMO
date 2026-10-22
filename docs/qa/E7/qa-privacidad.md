# qa-privacidad — E7 ciclo 3

**Resultado: PASA.** No hay hallazgo. No aplica severidad.

Alcance: `git diff 8a268ca0c4f626df84ae6992c7bee5bab7597577..HEAD` en la rama `v3`, HEAD `577c6ba3a1bad4729ee139bb6709033ed9f9954e`. El base es ancestro (`git merge-base --is-ancestor` sale 0). Siete commits: `4ec574c`, `7dda433`, `73666eb`, `de37f8a`, `6052e9b`, `c75ef9f`, `577c6ba`. 26 archivos, +3135 / −8. El producto del ciclo 3 es `577c6ba` (empaquetado de fechas: 6 archivos, +137 / −18). `c75ef9f` solo documenta el rechazo del ciclo 2 (4 archivos, +131 / −75). `6052e9b..HEAD` son 10 archivos, +268 / −93. Al empezar, `git status --porcelain` estaba vacío. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se ejecutó Streamlit ni la suite. No hubo commit ni push de este informe. El script de apoyo quedó en `$env:TEMP` y se borró.

## Sección 14

| Límite | Evidencia | Resultado |
|---|---|---|
| No leer `data/real/` ni el golden | `git ls-files data/real` vacío. `.gitignore` línea 2 sigue en `data/real/` y `git check-ignore -v -- data/real/probe.xer` apunta a esa regla (salida 0). `ATLASPMO_GOLDEN_DIR` no está definida en Process, User ni Machine; no se imprimió ningún valor ni se abrió esa ruta. `check_g8` solo recorre `git ls-files`, así que no abre `data/real/`. Las menciones del diff son la prohibición, no una lectura. | cumple |
| Sin cronogramas fuera de `tests/fixtures/` | El diff no trae `.xer`, `.mpp` ni `.xml`. Los versionados son 9 `.xer` y 2 `.xml`, todos bajo `tests/fixtures/`. No hay `.mpp`. | cumple |
| Sin rutas de perfil | En las 3135 líneas agregadas el patrón de G8 no coincide (0). Tampoco hay `C:/Users/`, `\\Users\\`, `%USERPROFILE%` ni el nombre de la cuenta (0). El texto completo de los 26 archivos del rango tampoco coincide (0). `6052e9b..HEAD` tampoco (0). `NUMBA_CACHE_DIR` y `NUMBA_CACHE_LOCATOR_CLASSES` no están definidas en Process, User ni Machine. `numba.config.CACHE_DIR` y `CACHE_LOCATOR_CLASSES` están vacíos. | cumple |
| Sin secretos | No hay `.env`, `.env.local` ni `.streamlit/secrets.toml` (`Test-Path` ausente; `git ls-files` no los lista). En las líneas agregadas no hay asignación de clave, token ni llave privada, ni correo. | cumple |
| Red solo la permitida, y anotada | `docs/qa/E7/acciones.md` sigue con los dos `uv add` del ciclo 1: `py -3.12 -m uv add numba` (numba 0.68.0, llvmlite 0.50.0) y `py -3.12 -m uv add numpy` (numpy 2.5.4). `git log` de ese archivo en el rango solo muestra `7dda433`. El diff de `uv.lock` agrega 54 URLs: 2 de `pypi.org` (`source = { registry = "https://pypi.org/simple" }` en los paquetes nuevos `llvmlite` y `numba`) y 52 de `files.pythonhosted.org`. No hay otro host ni otro índice. `numpy` entra como dependencia directa; su bloque ya estaba en el lock y también apunta a ese registro. La única URL fuera de `uv.lock` es la cita de ese registro en el informe del ciclo 2 (`c75ef9f`, `qa-privacidad.md`). `577c6ba` no trae URL. Este ciclo no toca `uv.lock`, `pyproject.toml` ni `acciones.md`, y no repite instalaciones. | cumple |
| Git | El diff no empuja a `main`, no reescribe historia publicada y no toca hooks. `git status -sb`: `v3` va 7 commits adelante de `origin/claude/beautiful-goodall-m0q2zj` (`git rev-list --left-right --count` da `7 0`). `refs/remotes/origin/v3` no existe. En `git reflog --date=iso -40` los siete commits de E7 son `commit:`; no hay entrada de push, reset, rebase ni amend. Las menciones de «push» del reflog son mensajes de cierre de E0 a E6, anteriores al checkout de `v3`. `acciones.md` no anota push. | cumple |
| Sistema | El diff no toca PATH, registro ni servicios. Los dos `uv add` de la bitácora declaran wheel, sin compilador y sin administrador. Este ciclo no los repitió. | cumple |
| Controles que el diff no debilita | `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks/` y `scripts/qa_gate.py` está vacío. Siguen el deny de `data/real/**` y de `.env` en `.grok/config.toml`, y los hooks `reject-schedules`, `commit-g8` y `push-v2-g8`. | cumple |

`.env` y `.env.local` no están en `.gitignore` (`git check-ignore -q` sale 1). No es hallazgo de E7: el diff no tocó esa regla, no hay `.env` en el árbol, y un `.env` versionado lo rechazan el hook y G8.

## G8

`check_g8` sobre el árbol versionado: **pass**, «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red».

Eso cubre cronogramas y XML de cronograma fuera de fixtures, `data/real/`, nombres `.env`, el patrón de perfil en `.py`, `.md`, `.toml`, `.yaml`, `.yml`, `.bat` y `.json`, imports de `socket`, `requests`, `httpx`, `aiohttp`, `http.client` y `urllib.request` en `src/`, y `.streamlit/config.toml`.

Ese config no cambió: `address = "localhost"` y `gatherUsageStats = false`. Un recorrido AST de `src/**/*.py` y de los `.py` del diff no encontró esos imports ni `urllib`, `ftplib`, `smtplib` o `websocket`. En `src/` del diff no hay llamadas a `open`, `print`, `urlopen`, `subprocess` ni `getenv`.

ERMHDR: los 9 `.xer` de `tests/fixtures/` tienen encabezado. `ermhdr_bad=0`. Ocho traen el único campo `20.12`; `minimal.xer` no trae campos después de `ERMHDR`. El diff no agrega fixtures. Esos 9 `.xer` y los 2 `.xml` tampoco contienen el patrón de perfil de G8.

## Empaquetado de fechas

`577c6ba` cambia `src/atlaspmo/engine/fast.py` y tests sintéticos. `_dates` publica `raw_start` solo si la actividad ya empezó (`started == 1`); si no, usa el minuto calculado. `_driving` aplica la misma condición antes de descartar un real con segundos. `_finish_anchor` conserva los segundos del fin de proyecto cuando la restricción no gana el pase atrás, y un hito de inicio no iniciado no los conserva. No importa red, no abre archivos, no lee el entorno y no escribe logs. Los tests usan códigos `P`, `B`, `A`, `M` y fechas de 2026. No hay nombres de cronograma real.

## Caché de numba

`src/atlaspmo/numeric/kernels.py` sigue con `njit(cache=True)` en `run_passes`. El ciclo 3 no toca ese archivo. Con `NUMBA_CACHE_DIR` vacío, el primer locator que aplica es `InTreeCacheLocator` (`.venv/Lib/site-packages/numba/core/caching.py`, numba 0.68.0): `UserProvidedCacheLocator` sale si `config.CACHE_DIR` está vacío, y el directorio de `InTree` es `__pycache__` junto al `.py`. En disco están `src/atlaspmo/numeric/__pycache__/kernels.run_passes-22.py312.nbi` y `kernels.run_passes-22.py312.1.nbc` (y tres `.pyc`). `git check-ignore -v` los atribuye a `.gitignore` línea 9 (`__pycache__/`). `git ls-files` de `*.nbi`, `*.nbc` y de esa carpeta no devuelve nada. Un `.nbc` suelto al lado del módulo no estaría ignorado (`git check-ignore -q` sale 1); no hay ninguno (`Test-Path` ausente) y no hay ninguno versionado. La caché es el compilado de la función, no un cronograma.

## Comandos

- `git rev-parse HEAD`; `git branch --show-current`; `git status -sb`; `git status --porcelain` (vacío al empezar); `git merge-base --is-ancestor 8a268ca0c4f626df84ae6992c7bee5bab7597577 HEAD` (salida 0); `git log --oneline` del rango; `git diff --stat` y `--name-status`; `git rev-list --count` (7); `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'`; `git rev-list --left-right --count 'HEAD...@{u}'` (`7 0`)
- `git show --stat --format=fuller 577c6ba`; `git show --stat c75ef9f`; `git diff --stat` y `--name-status 6052e9b..HEAD`; `git diff --shortstat c75ef9f..577c6ba`; `git diff -U3 6052e9b..577c6ba` de `fast.py` y de los dos tests
- `git diff -U3` de `pyproject.toml`; `git log --oneline` del rango sobre `docs/qa/E7/acciones.md` (solo `7dda433`)
- Script en `$env:TEMP` (borrado) con `py -3.12` sobre `git diff -U0` del rango y sobre el texto de los 26 archivos: patrón de perfil de G8, barras `C:/Users/` y `%USERPROFILE%`, asignaciones de secreto, llaves, correos y URLs por host. Líneas agregadas 3135. `PROFILE_HITS=0`, `SECRET_HITS=0`, `EXTRA_HITS=0`, correos 0. Hosts en líneas agregadas: `pypi.org` 3 (2 en `uv.lock`, 1 cita en `qa-privacidad.md`) y `files.pythonhosted.org` 52, solo en `uv.lock`. El mismo patrón sobre `6052e9b..HEAD`: perfil 0, correos 0, URL 1 (la cita)
- El mismo script, segundo pase sobre el diff de `uv.lock` y `pyproject.toml`: 54 URLs, hosts `pypi.org` 2 y `files.pythonhosted.org` 52; `registry` solo en `llvmlite` y `numba`; `numpy` solo como dependencia (`{ name = "numpy" }` y el specifier), sin bloque nuevo
- `py -3.12` llamando a `check_g8`: pass. AST de imports de red en `src/**/*.py` y en los `.py` del diff: vacío. Llamadas de E/S en el `src/` del diff: vacío
- Variables `ATLASPMO_GOLDEN_DIR`, `NUMBA_CACHE_DIR` y `NUMBA_CACHE_LOCATOR_CLASSES` en Process, User y Machine: UNSET, sin imprimir valores. `ATLASPMO_GIT` en el proceso: UNSET
- ERMHDR de `tests/fixtures/**/*.xer` (cp1252, primera línea) y patrón de perfil en esos `.xer` y en los `.xml`: `XER_COUNT=9`, `ERMHDR_BAD=[]`, `XML_COUNT=2`, `FIXTURE_PROFILE=[]`
- `git ls-files` de `*.xer`, `*.mpp`, `*.xml`, `.env`, `.env.*`, `data/real`, `*.nbi`, `*.nbc`
- `git check-ignore -v` de `data/real/probe.xer` y de los `.nbi`, `.nbc` y `.pyc` bajo `src/atlaspmo/numeric/__pycache__/`; `git check-ignore -q` de `.env`, `.env.local`, `.streamlit/secrets.toml` y de un `.nbc` hermano del módulo
- `Test-Path` de `.env`, `.env.local`, `.streamlit/secrets.toml`, `src/atlaspmo/numeric/kernels.nbc` y del `.nbi` suelto (todos ausentes)
- `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks` y `scripts/qa_gate.py` (vacío)
- `git rev-parse --verify refs/remotes/origin/v3` (no existe); `git reflog --date=iso -40`, filtrado por push, reset, rebase, amend y force
- Lectura de `.streamlit/config.toml`, `.gitignore`, `.grok/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks/pre_push.py`, `docs/qa/E7/acciones.md` y del locator en la numba 0.68.0 del `.venv` (`CACHE_DIR` vacío; orden `UserProvidedCacheLocator`, luego `InTreeCacheLocator`)

No se corrió la aplicación Streamlit ni la suite. La lectura de código y de docs se hizo sin abrir `data/real/`.
