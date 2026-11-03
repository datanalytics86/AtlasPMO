# qa-privacidad — E10

**Resultado: PASA.** El diff está limpio. No hay hallazgo. No aplica severidad.

Alcance: `git diff 8934ffc..HEAD` en la rama `v3`, HEAD `5edd81e6dd5c9d96d39b9d94aca6332a062aeccb`. El base es ancestro (`git merge-base --is-ancestor` sale 0) y es `origin/v3`. Diez commits, de `d38bdaa` a `5edd81e`: contrato de E10, rechazo y segunda redacción, aceptación de qa-spec, reparto de duración remanente, segunda firma de CPLI con feriado y de BEI, FS entre dos proyectos, baseline y visor, float paths, y el estado «en curso». 36 archivos, +1958 / −53. `origin/v3` va 10 commits atrás (`git rev-list --left-right --count origin/v3...HEAD` da `0 10`). Al empezar, `git status --porcelain` estaba vacío. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se ejecutó Streamlit ni la suite. No hubo commit ni push de este informe. No se importó `scripts/qa_gate.py` por importlib. El script de apoyo quedó en el directorio temporal y se borró. No se reabre E8 ni E9.

## Sección 14

| Límite | Evidencia | Resultado |
|---|---|---|
| No leer `data/real/` ni el golden | `git ls-files data/real` vacío. `git check-ignore -v -- data/real/probe.xer` apunta a `.gitignore` línea 2. `ATLASPMO_GOLDEN_DIR` no está definida en Process, User ni Machine; no se imprimió ningún valor ni se abrió esa ruta. `ATLASPMO_GIT` tampoco está definida en esos tres ámbitos. Las 7 líneas agregadas que nombran `data/real` y las 7 que nombran `GOLDEN` son la prohibición ya escrita en los informes de esta etapa, no una lectura. | cumple |
| Sin cronogramas fuera de `tests/fixtures/` | El diff agrega dos `.xer`, los dos bajo `tests/fixtures/synthetic/cases/`: `cpli_ss.xer` y `bei.xer`. No agrega `.mpp` ni `.xml`. Versionados: 11 `.xer` y 2 `.xml`, todos bajo `tests/fixtures/`. No hay `.mpp`. Las 40 líneas agregadas con `.xer` son nombres de esos fixtures, imports `read_xer` / `read_xer_bytes` o archivos que el test escribe bajo `tmp_path`. | cumple |
| Sin rutas de perfil | 1958 líneas agregadas y 53 borradas: el patrón de G8 coincide 0 veces. El texto completo de los 36 archivos en HEAD también da 0. Los diez mensajes de commit dan 0. No hay `%USERPROFILE%`, `C:/Users/` ni `/home/`. | cumple |
| Sin hosts, telemetría ni secretos | URL en el parche: 0. Correos: 0. Asignaciones de clave, token o llave: 0. No hay `.env`, `.env.local` ni `.streamlit/secrets.toml`. Doce coincidencias de un patrón de host son el paquete `atlaspmo.io`, no un sitio. La única URL en el texto completo de los 36 archivos es la cita previa del esquema de Microsoft Project en `docs/XER_SPEC.md`; este rango no la agrega. El diff no toca `.streamlit/config.toml`: sigue `address = "localhost"` y `gatherUsageStats = false`. La única línea agregada con `socket` es la prohibición del contrato: «Abrir un socket.» | cumple |
| Red y bitácora | No hay `docs/qa/E10/acciones.md`. El rango no toca `uv.lock` ni `pyproject.toml`, no agrega una URL y no anota un `git push`. El reflog de estos diez HEAD es solo commits locales. No hubo instalación ni push que registrar. | cumple |
| Git | No hay push a `main`, `--force`, reset, rebase ni amend en este rango. `origin/v3` sigue en `8934ffc`. Los diez movimientos nuevos del reflog son los commits de E10. | cumple |
| Sistema | El diff no toca PATH, registro ni servicios. No hay `subprocess` ni `os.system` en las líneas agregadas. | cumple |
| Controles que el diff no debilita | `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks/`, `scripts/qa_gate.py`, `pyproject.toml`, `uv.lock`, `docs/qa/seccion11.toml` y `docs/qa/baseline.json` está vacío. | cumple |

## G8

`.\.venv\Scripts\python.exe scripts\hooks\pre_commit_g8.py`: salida 0 y silencio. El hook corre `check_g8` con un import normal. Resultado: **pass**, «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red».

Eso cubre cronogramas y XML de cronograma fuera de fixtures, `data/real/`, nombres `.env`, el patrón de perfil en `.py`, `.md`, `.toml`, `.yaml`, `.yml`, `.bat` y `.json`, imports de `socket`, `requests`, `httpx`, `aiohttp`, `http.client` y `urllib.request` en `src/`, el `ERMHDR` de los `.xer` de `tests/fixtures/`, y `.streamlit/config.toml`. Este rango no modifica `scripts/qa_gate.py`.

ERMHDR: `cpli_ss.xer` y `bei.xer` empiezan por `ERMHDR` y el único campo es `20.12`, que cae en `ANON_ERMHDR`. No hay otro `.xer` agregado. Los 11 `.xer` de `tests/fixtures/` tienen encabezado y ningún campo cae fuera de ese patrón. `ERMHDR_BAD=0`. Esos dos no traen columnas cuyo nombre mencione user, obs o db. Los nombres son códigos sintéticos: proyectos `CUR` y `BASE`, calendario `Base` / `C1`, tareas `A`, `B`, `LATE`, `OPEN` y `EARLY`. No hay nombres de persona, de obra ni de base. Los 11 `.xer` y el resto de `tests/fixtures/` revisado (23 archivos entre `.xer`, `.xml`, `.yaml` y `.json`) tampoco contienen el patrón de perfil. `PROFILE=0`.

AST de los 21 `.py` del rango, en el texto de HEAD: ningún import de `socket`, `requests`, `httpx`, `aiohttp`, `urllib`, `ftplib` ni `smtplib`, y ninguna llamada a `open`.

## Fixtures y biblioteca

`scripts/build_cases.py` solo suma `_cpli_ss`, `_bei` y su llamada desde `main`. Escribe bajo `tests/fixtures/synthetic/cases`. El calendario de `cpli_ss` es lunes a viernes 08:00–16:00 con la excepción del 2026-01-07. No lee `data/real/` ni el entorno.

Los tests nuevos que tocan disco usan `tmp_path` o `tests/fixtures/synthetic/cases`. `tests/test_e10_ui.py` arma los XER con `write_xer` (encabezado `ERMHDR`, códigos `LATE` / `OPEN` / `EARLY`) y los sube en memoria. La biblioteca por defecto no guarda el cronograma: la casilla nace apagada y el test comprueba que el DuckDB de `tmp_path` no contiene `ERMHDR`. Si se prende, el texto se escribe solo en el DuckDB de esa ruta temporal. `Library` no abre red: el camino lo escribe quien usa la pantalla, y el pie sigue diciendo que nada sale de este equipo.

`docs/ESTADO.md` agrega la fila y el plan de E10. `docs/VALIDACIONES_PENDIENTES.md` agrega tres puntos de P6 y de `RSRCRATE`, sin URL ni carpeta de usuario. `docs/XER_SPEC.md` pasa `driving_path_flag` a leído. Esos tres no traen ruta de perfil.

## Comandos

- `git rev-parse HEAD`; `git branch --show-current`; `git status --porcelain` (vacío al empezar); `git status -sb` (`v3...origin/v3 [ahead 10]`); `git merge-base --is-ancestor 8934ffc HEAD` (salida 0); `git rev-parse --short` de ambos extremos; `git rev-parse origin/v3` (igual a `8934ffc`)
- `git log --oneline 8934ffc..HEAD` (diez commits); `git diff --shortstat` y `--name-status` (36 archivos, +1958 / −53); `git rev-list --left-right --count origin/v3...HEAD` (`0 10`); `git rev-list --count origin/v3..HEAD` (10)
- `.\.venv\Scripts\python.exe scripts\hooks\pre_commit_g8.py` (salida 0, sin texto)
- Script en el directorio temporal (borrado) sobre `git diff -U0`: patrón de perfil de G8, URL, correos, secretos, `%USERPROFILE%`, `.xer`, imports de red, `open` / `read_text` / `read_bytes`, `getenv`, `subprocess`, push y `--force`. Líneas agregadas 1958. Perfil, URL, correo, secreto, entorno, push y force en 0. Una línea de red es la prohibición «Abrir un socket». Hosts de URL: ninguno; las doce coincidencias de host son `atlaspmo.io`. El mismo patrón sobre las 53 líneas borradas y sobre los mensajes: 0
- Segundo pase del mismo script: texto completo de los 36 archivos en HEAD (`BLOB_PROFILE=0`, `BLOB_URL=1` ya citada y no agregada, `BLOB_EMAIL=0`); AST de imports y de `open`; ERMHDR de los dos `.xer` nuevos y de `tests/fixtures/**/*.xer` (`FIXTURE_XER=11`, `ERMHDR_BAD=0`); patrón de perfil sobre los 23 archivos `.xer`, `.xml`, `.yaml` y `.json` de `tests/fixtures/` (`PROFILE=0`); `git ls-files` de `*.xer`, `*.mpp`, `*.xml`, `.env` y `data/real`
- `git diff --name-only` de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml`, `scripts/hooks`, `scripts/qa_gate.py`, `pyproject.toml`, `uv.lock`, `docs/qa/seccion11.toml` y `docs/qa/baseline.json` (vacío)
- `ATLASPMO_GOLDEN_DIR` y `ATLASPMO_GIT` en Process, User y Machine: UNSET, sin imprimir valores. `Test-Path` de `.env`, `.env.local`, `.streamlit/secrets.toml` y `docs/qa/E10/acciones.md`: ausentes. `git check-ignore -v -- data/real/probe.xer`: `.gitignore:2`
- `git diff` de `src/atlaspmo/io/load.py`, `src/atlaspmo/io/xer.py`, `src/atlaspmo/library/store.py`, `src/atlaspmo/ui/app.py`, `scripts/build_cases.py`, `docs/ESTADO.md`, `docs/VALIDACIONES_PENDIENTES.md` y `docs/XER_SPEC.md`. Lectura de `cpli_ss.xer`, `bei.xer` y sus YAML. `git reflog --date=iso -20`: los movimientos posteriores a `8934ffc` son los diez commits; no hay push, reset, rebase ni amend del rango
- Lectura de `docs/MEGAPROMPT_v3.md` (secciones 8.5 y 14), `scripts/qa_gate.py` (`check_g8` y `ANON_ERMHDR`), `scripts/hooks/pre_commit_g8.py`, `.streamlit/config.toml` y `.gitignore`

No se corrió la aplicación Streamlit ni la suite. La lectura de código y de docs se hizo sin abrir `data/real/`.
