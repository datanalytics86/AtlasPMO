# qa-privacidad — E9

**Resultado: PASA.** El diff está limpio. No hay hallazgo. No aplica severidad.

Alcance: `git diff 82f9fa4..cf35f17` en la rama `v3`, HEAD `cf35f17904f7e36c962b41d55c3feda89eaec2b0`. El base es ancestro (`git merge-base --is-ancestor` sale 0). Un solo commit, `cf35f17`: «feat(risk): Monte Carlo en numba y tornado por cono (B-07, ADR-022)». 10 archivos, +1151 / −79. `origin/v3` va 5 commits atrás (`git rev-list --left-right --count origin/v3...HEAD` da `0 5`). Al empezar, `git status --porcelain` estaba vacío. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se ejecutó Streamlit ni la suite. No hubo commit ni push de este informe. El script de apoyo quedó en el directorio temporal y se borró.

## Sección 14

| Límite | Evidencia | Resultado |
|---|---|---|
| No leer `data/real/` ni el golden | `git ls-files data/real` vacío. `git check-ignore -v -- data/real/probe.xer` apunta a `.gitignore` línea 2. `ATLASPMO_GOLDEN_DIR` no está definida en Process, User ni Machine; no se imprimió ningún valor ni se abrió esa ruta. `check_g8` solo recorre `git ls-files` y los `.xer` de `tests/fixtures/`. Las menciones del rango son la prohibición ya escrita fuera de este diff, no una lectura. | cumple |
| Sin cronogramas fuera de `tests/fixtures/` | El diff no trae `.xer`, `.mpp` ni `.xml`. Versionados: 9 `.xer` y 2 `.xml`, todos bajo `tests/fixtures/`. No hay `.mpp`. `SCHED` en líneas agregadas: la única mención es `from atlaspmo.io.xer import read_xer_bytes`. | cumple |
| Sin rutas de perfil | 1151 líneas agregadas y 79 borradas: el patrón de G8 coincide 0 veces. El texto completo de los 10 archivos en HEAD también da 0. El mensaje del commit da 0. No hay `%USERPROFILE%`, `C:/Users/` ni `/home/`. | cumple |
| Sin hosts, telemetría ni secretos | URL en el parche: 0. Correos: 0. Asignaciones de clave, token o llave: 0. No hay `.env`, `.env.local` ni `.streamlit/secrets.toml`. Las tres coincidencias de un patrón de host son el paquete `atlaspmo.io`, no un sitio. El diff no toca `.streamlit/config.toml`: sigue `address = "localhost"` y `gatherUsageStats = false`. | cumple |
| Red y bitácora | No hay `docs/qa/E9/acciones.md`. El rango no toca `uv.lock` ni `pyproject.toml`, no agrega una URL y no anota un `git push`. El reflog de este HEAD es un commit local. No hubo instalación ni push que registrar. | cumple |
| Git | No hay push a `main`, `--force`, reset, rebase ni amend en este rango. El único movimiento nuevo del reflog es el commit `cf35f17`. | cumple |
| Sistema | El diff no toca PATH, registro ni servicios. No hay `subprocess` ni `os.system` en las líneas agregadas. | cumple |
| Controles que el diff no debilita | `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks/`, `scripts/qa_gate.py`, `pyproject.toml`, `uv.lock`, `docs/qa/seccion11.toml` y `docs/qa/baseline.json` está vacío. | cumple |

## G8

`check_g8` sobre el árbol versionado: **pass**, «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red».

Eso cubre cronogramas y XML de cronograma fuera de fixtures, `data/real/`, nombres `.env`, el patrón de perfil en `.py`, `.md`, `.toml`, `.yaml`, `.yml`, `.bat` y `.json`, imports de `socket`, `requests`, `httpx`, `aiohttp`, `http.client` y `urllib.request` en `src/`, y `.streamlit/config.toml`. Este commit no modifica `scripts/qa_gate.py`.

ERMHDR: los 9 `.xer` de `tests/fixtures/` tienen encabezado y ningún campo cae fuera de `ANON_ERMHDR`. `ERMHDR_BAD=0`. El diff no agrega fixtures. Esos 9 `.xer` y los otros archivos de `tests/fixtures/` revisados (19 en total, entre `.xer`, `.xml`, `.yaml` y `.json`) tampoco contienen el patrón de perfil. `PROFILE=0`.

AST de los siete `.py` del rango: ningún import de `socket`, `requests`, `httpx`, `aiohttp`, `urllib`, `ftplib` ni `smtplib`, y ninguna llamada a `open`.

## Monte Carlo y archivos

`run_risk` recibe un `Schedule` ya cargado. `fastloop.py` arma el lote sobre los arrays de `Compiled` y llama a `run_batch`. `numeric/batch.py` solo recorre esos arrays con `prange` o con el bucle Python de cobertura. Ninguno de los tres abre un path, lee el entorno ni llama a la red. `LAST.get("path")` compara el nombre `"fast"` o `"reference"`, no una ruta de disco.

Los tests nuevos que tocan disco usan el helper ya existente `_load`: escribe `case.xer` solo bajo el `tmp_path` de pytest, con tareas armadas en el test (`A`–`E`, calendario `C1`, encabezado `ERMHDR`), y lee ese mismo archivo. `tests/property/test_e9_differential.py` no abre archivo: `encode_xer` produce bytes y `read_xer_bytes` los parsea en memoria.

`docs/qa/E9/perf.md` cita `tests/perf/test_seccion11.py::test_s11_montecarlo_30k`. Ese test no cambia en este diff. Genera la red con `write_scale` (tablas sintéticas, encabezado `ERMHDR` y versión `20.12`, nombre de proyecto «Escala») en el temporal del test, y `run_risk` corre después, sobre el `Schedule`. El informe dice que el reloj no incluye esa escritura ni esa lectura. El producto no abre ese archivo.

`batch_passes` queda con `njit(cache=True)` y no fija un directorio de caché. El informe de perf dice que numba no pudo guardar `batch_passes` por un global dinámico. En `src/atlaspmo/numeric/__pycache__/` está el `.pyc` del módulo y la caché previa de `kernels.run_passes`; no hay caché de `batch_passes`. `git ls-files` de `*.nbc` y `*.nbi` no devuelve nada. `.gitignore` línea 9 ignora `__pycache__/`. Esa caché es el compilado de la función, no un cronograma.

`docs/ESTADO.md` solo cambia la fila de estado de E9. `docs/qa/E9/riesgo.md` y `perf.md` no traen URL ni carpeta de usuario. El informe de perf nombra CPU, RAM, build de Windows y CPython.

## Comandos

- `git rev-parse HEAD`; `git branch --show-current`; `git status --porcelain` (vacío al empezar); `git status -sb` (`v3...origin/v3 [ahead 5]`); `git merge-base --is-ancestor 82f9fa4 HEAD` (salida 0); `git rev-parse --short` de ambos extremos
- `git log --oneline 82f9fa4..cf35f17` (un commit); `git log -1 --format=%B`; `git diff --shortstat` y `--name-status` (10 archivos, +1151 / −79); `git rev-list --left-right --count origin/v3...HEAD` (`0 5`); `git rev-list --count origin/v3..HEAD` (5)
- Script en el directorio temporal (borrado) sobre `git diff -U0`: patrón de perfil de G8, URL, correos, secretos, `%USERPROFILE%`, `.xer`, imports de red, `open` / `read_text` / `read_bytes`, `getenv`, `subprocess`. Líneas agregadas 1151. Todo en 0, salvo una línea con `.xer` que es el import `read_xer_bytes`. Hosts de URL: ninguno. El mismo patrón sobre las 79 líneas borradas y sobre el mensaje: 0
- Segundo pase del mismo script: texto completo de los 10 archivos en HEAD (`BLOB_USER=0`, `BLOB_URL=0`); AST de llamadas; `check_g8` (**pass**); ERMHDR de `tests/fixtures/**/*.xer` (`FIXTURE_XER=9`, `ERMHDR_BAD=0`); `git ls-files` de `*.xer`, `*.mpp`, `*.xml`, `.env` y `data/real`
- Patrón de perfil sobre los 19 archivos `.xer`, `.xml`, `.yaml` y `.json` de `tests/fixtures/`: `PROFILE=0`
- `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks`, `scripts/qa_gate.py`, `pyproject.toml`, `uv.lock`, `docs/qa/seccion11.toml` y `docs/qa/baseline.json` (vacío)
- `ATLASPMO_GOLDEN_DIR` y `ATLASPMO_GIT` en Process, User y Machine: UNSET, sin imprimir valores. `Test-Path` de `.env`, `.env.local` y `.streamlit/secrets.toml`: ausentes. `git check-ignore -v -- data/real/probe.xer`: `.gitignore:2`
- Nombres en `src/atlaspmo/numeric/__pycache__/`: `.pyc` de `batch` y `kernels`, más `kernels.run_passes-22.py312.nbi` y `.nbc`. No hay caché de `batch_passes`. `git ls-files` de `*.nbc` y `*.nbi`: vacío
- `git diff -U3` de `tests/test_e4_tornado.py` y `tests/test_risk.py` (solo el texto de la aproximación del cono y la frase de numba). `git reflog --date=iso -8`: el movimiento de este HEAD es el commit; no hay push, reset, rebase ni amend del rango
- Lectura de `docs/MEGAPROMPT_v3.md` (secciones 2, 8.3, 8.5 y 14), `scripts/qa_gate.py` (`check_g8`), `.streamlit/config.toml`, `.gitignore`, `montecarlo.py`, `fastloop.py`, `numeric/batch.py`, los tests del rango, `tests/test_cpm.py` (`_load`), `tests/perf/test_seccion11.py` (`test_s11_montecarlo_30k`) y `scripts/gen_scale.py` (`write_scale`)

No se corrió la aplicación Streamlit ni la suite. La lectura de código y de docs se hizo sin abrir `data/real/`.
