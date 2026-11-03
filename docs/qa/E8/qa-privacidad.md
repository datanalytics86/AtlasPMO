HALLAZGOS
crítico
importante

# qa-privacidad — E8

**No cierro la etapa.** El veredicto lo escribe qa-revisor.

Alcance: `git diff 8a268ca...HEAD` en la rama `v3`, HEAD `71b42f3d70438b6bff92a9b64cb67c240b42b0f9`. El base es ancestro (`git merge-base --is-ancestor` sale 0). Veinte commits, 38 archivos, +4470 / −21. `origin/v3` está en `0dd3e40` y la rama va 11 commits adelante (`git rev-list --count origin/v3..HEAD`). Al empezar, `git status --porcelain` estaba vacío. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se ejecutó Streamlit ni la suite. No hubo commit ni push de este informe.

## Hallazgos

### H-1 · crítico — ruta de perfil en el historial de `acciones.md`

El archivo en HEAD no la tiene. `docs/qa/E8/acciones.md` no declara un push hecho: dice que el push de `v3` queda para el cierre, si el veredicto lo autoriza, y que no entra en la tabla hasta que ocurra. La tabla tiene tres comandos y ninguno es un push.

La ruta sí está en tres commits ancestros de HEAD que `origin/v3` todavía no tiene (`git merge-base --is-ancestor` contra HEAD sale 0 y contra `origin/v3` sale 1):

- `d279d8e` la introduce en `docs/qa/E8/acciones.md`, en el `uv sync`, como argumento `--directory`.
- `67d306e` y `ef5fc85` conservan esa línea.
- `b8ae699` la quita del árbol. El mensaje no copia la ruta.

`git grep -l` de la cuenta, en cada uno de esos tres commits, solo devuelve ese archivo. En `b8ae699` y en HEAD no devuelve ninguno. El diff neto `8a268ca...HEAD` tampoco contiene la cuenta (`NET_USER=0`). Los mensajes del rango tampoco (`MSG_USER=0`).

El patrón de G8 sí coincide con esa línea histórica (`match_lines=1`). `check_g8` no la ve porque solo lee el árbol de `git ls-files`, y ahí el control pasa. Un push de `v3` enviaría los tres blobs y el parche de `b8ae699`, que todavía lleva la línea borrada. Es violación de privacidad (sección 8.5). Bloquea el cierre.

### H-2 · importante — el intérprete no salió de PyPI

La bitácora resume: «La red fue PyPI y, al cierre, el push de `v3` si el veredicto lo autoriza». El push de E8 no está: `origin/v3` sigue en `0dd3e40` y el reflog de 200 entradas no tiene push, reset, rebase ni amend.

El segundo comando de la tabla, `py -3.11 -m uv python install 3.12`, no es el índice de PyPI. La documentación oficial de uv (guía de instalación de Python y el concepto de versiones, docs.astral.sh) dice que Python no publica binarios oficiales y que uv baja CPython de python-build-standalone, el proyecto de Astral. La bitácora anota el resultado CPython 3.12.16. El intérprete del `.venv` es 3.12.16. No abrí la caché de uv.

No hay evidencia de subida del repositorio ni de un cronograma. Es desviación de la sección 14.1.3. Por la sección 8.5 queda importante, no crítico: no es fuga de datos. El preámbulo de la sección 14 llama crítico a cualquier desvío de un límite duro; esta clasificación sigue 8.5, como pide el encargo. Importante también bloquea el cierre.

Los otros dos comandos de la tabla sí caben en PyPI: `py -3.11 -m pip install --user uv` (uv 0.13.6) y `py -3.11 -m uv sync --group dev --python 3.12` (exit 0). En todo el rango, las URL agregadas son solo `pypi.org` (3) y `files.pythonhosted.org` (52), todas en el lock o citadas desde el informe de E7. `uv.lock` y `pyproject.toml` no cambian desde `origin/v3`. El push de E7 está en `docs/qa/E7/acciones.md` (`git push -u origin v3`, sin `--force`) y coincide con `origin/v3`. El remoto es `github.com` y la URL no trae credenciales.

## Lo que sí cumple

| Límite | Evidencia | Resultado |
|---|---|---|
| Sin cronogramas reales ni lectura de `data/real/` | El rango no nombra `.xer`, `.mpp`, `.xml`, `.ppx` ni `.env` (`SCHED_LINES=0`). Versionados: 9 `.xer` y 2 `.xml`, todos bajo `tests/fixtures/`. No hay `.mpp`. `git ls-files data/real` vacío. `git check-ignore -v -- data/real/probe.xer` apunta a `.gitignore` línea 2. `ATLASPMO_GOLDEN_DIR` no está definida en el proceso. Las menciones del diff son la prohibición. Los tests de E8 arman redes con `write_scale` o tareas sintéticas, no un cronograma real. | cumple |
| `acciones.md` en HEAD | Sin ruta de perfil y sin un push que no ocurrió. El problema es el historial (H-1), no la copia del árbol. | cumple en HEAD |
| PATH, registro, `git config`, `uv python update-shell` | La bitácora dice que no se editaron y que no se corrió `update-shell`. En las líneas agregadas no hay un comando que lo haga (`EXEC_HITS=0`). El reflog revisado no tiene `config` ni `update-shell`. La documentación de uv separa `uv python install` (deja el ejecutable versionado en su directorio de binarios) de `uv python update-shell` (eso es lo que agrega el directorio al PATH). No inspeccioné el registro ni carpetas fuera del repositorio. | cumple, con ese límite |
| `scripts/qa_gate.py` | Cambia solo en `ef5fc85`, mensaje «G3 trata la falta de Python 3.12 como hueco de entorno (ADR-011, ADR-004)». El diff agrega la condición `No suitable Python runtime found` en `_environment_gap`. No toca G8. | cumple |
| Secretos y controles que el diff no debilita | Correos en líneas agregadas: 0. Líneas con asignación de secreto o llave privada: 0. No hay `.env`, `.env.local` ni `.streamlit/secrets.toml`. El diff no toca `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml` ni `scripts/hooks/`. Siguen el deny de `data/real/**` y de `.env` en `.grok/config.toml`. `.streamlit/config.toml` sigue con `address = "localhost"` y `gatherUsageStats = false`. | cumple |
| Red en el código de E8 | Siete `.py` cambiados desde `origin/v3`. El AST no tiene imports de `socket`, `requests`, `httpx`, `aiohttp`, `http.client`, `urllib`, `ftplib` ni `smtplib`. | cumple |
| ERMHDR | Nueve `.xer` de `tests/fixtures/`. `BAD=0`. El diff no agrega fixtures. | cumple |
| G8 sobre el árbol | `check_g8`: pass, «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red». Coincide con `docs/qa/E8/gate.md`. No cubre H-1. | cumple en el árbol |

## Comandos

- `git rev-parse HEAD`; `git branch --show-current`; `git status --porcelain` (vacío al empezar); `git status -sb` (`v3...origin/v3 [ahead 11]`); `git merge-base --is-ancestor 8a268ca HEAD` (salida 0)
- `git log --oneline 8a268ca...HEAD` (20); `git diff --name-status` y `--shortstat` (38 archivos, +4470 / −21); `git log --format=%h %s` del rango sobre `scripts/qa_gate.py` (solo `ef5fc85`)
- `git rev-parse --abbrev-ref --symbolic-full-name '@{u}'` (`origin/v3`); `git rev-parse --short origin/v3` (`0dd3e40`); `git rev-list --count origin/v3..HEAD` (11)
- Recorrido en Python del rango, borrado al terminar: versiones de `docs/qa/E8/acciones.md` por commit; `git grep` de la cuenta (solo nombres de archivo); diff neto; URL por host; menciones de `data/real` y de `ATLASPMO_GOLDEN_DIR`
- Segundo recorrido: `merge-base --is-ancestor` de `d279d8e`, `67d306e`, `ef5fc85` y `b8ae699` contra HEAD (0) y contra `origin/v3` (1); `NET_USER=0`; `HEAD_ACCIONES_USER=0`; `MSG_USER=0`; `SCHED_LINES=0`; diff de `.gitignore`, `.grok/config.toml`, `.streamlit/config.toml`, `.pre-commit-config.yaml` y `scripts/hooks` vacío; correos 0; secretos 0; `EXEC_HITS=0`
- ERMHDR de `tests/fixtures/**/*.xer`: `XER=9`, `BAD=0`. AST de imports de red en los 7 `.py` desde `origin/v3`: vacío
- `check_g8`: pass. El patrón de G8 sobre `d279d8e:docs/qa/E8/acciones.md`: `match_lines=1`
- `ATLASPMO_GOLDEN_DIR` en el proceso: no definida. `Test-Path` de `.env`, `.env.local` y `.streamlit/secrets.toml`: ausentes. `git check-ignore -v -- data/real/probe.xer`: `.gitignore:2`. `git remote get-url origin`: host `github.com`, sin credenciales en la URL
- `git reflog --date=iso -200`, filtrado por push, reset, rebase, amend, config y update-shell: 0
- Lectura de `docs/MEGAPROMPT_v3.md` (secciones 8.3, 8.5 y 14), `docs/qa/E8/acciones.md`, `gate.md`, `perf.md`, `logica-red.md`, `QC1_contrato.md`, `qa-spec.md`, `docs/qa/E7/acciones.md`, `docs/qa/E7/qa-privacidad.md`, el cambio de `scripts/qa_gate.py`, `.streamlit/config.toml` y `.grok/config.toml`
- Documentación oficial de uv, sin descargar el intérprete otra vez: guía de instalación de Python y concepto de versiones en docs.astral.sh

No se corrió la aplicación Streamlit ni la suite. La lectura de código y de docs se hizo sin abrir `data/real/`.

## Segunda pasada

HEAD `15494f48958a316a497d65fd3dccec6586bb4a7e`. `origin/v3` sigue en `0dd3e40` y es ancestro (`git merge-base --is-ancestor` sale 0). `git rev-list --left-right --count origin/v3...HEAD` da `0 10`: diez commits locales, ninguno del remoto falta. El reflog no tiene push ni `--force`. El movimiento nuevo es un reset local a `15494f4`. No se hizo commit ni push en esta pasada.

### H-1 cerrado

`d279d8e` ya no es ancestro de HEAD (sale 1). Tampoco lo son `67d306e`, `ef5fc85`, `b8ae699` ni `71b42f3`. Ninguna rama ni etiqueta los contiene. El objeto sigue en la base local (`git cat-file -t` dice commit) y el reflog todavía lo nombra, pero no es alcanzable desde HEAD. Un push de `v3` no lo envía.

En los diez commits `origin/v3..HEAD`, `docs/qa/E8/acciones.md` existe desde `d51a911` hasta `15494f4` (siete versiones). En las siete el patrón de G8 da 0, la cuenta da 0 y `--directory` da 0. `git grep` de la cuenta en cada commit del rango: 0 archivos. El diff `origin/v3...HEAD` agrega 1415 líneas: patrón de G8 = 0, cuenta = 0, `--directory` = 0.

No queda crítico.

### H-2 cerrado

Esas siete versiones ya no dicen «La red fue PyPI y». El preámbulo dice que la red fue PyPI para uv y las dependencias, y la descarga de CPython de python-build-standalone que hace `uv python install`. La celda de resultado del mismo comando repite python-build-standalone (dos veces en cada versión). El `uv sync` no lleva `--directory`. No hay fila de `git push`. El diff del rango no agrega URL ni un push.

`scripts/qa_gate.py` cambia en `658b68b`, mensaje con ADR-011 y ADR-004. El diff sigue siendo una sola condición en `_environment_gap`: `No suitable Python runtime found`.

No queda importante. La descarga de CPython sigue fuera de la lista literal de la sección 14.1.3, pero el hallazgo era la bitácora que la presentaba como solo PyPI. Esa frase ya no está en la rama, y no hay otro host ni una subida.

No se editó producto. No se tocaron `VEREDICTO.md`, `hallazgos.md` ni `qa-revisor.md`.

### Comandos de esta pasada

- `git rev-parse HEAD` (`15494f4`); `git status -sb` (`ahead 10`, sin push); `git merge-base --is-ancestor origin/v3 HEAD` (0); `git rev-list --left-right --count origin/v3...HEAD` (`0 10`); `git log --oneline origin/v3..HEAD`; `git diff --name-status origin/v3..HEAD`
- `git merge-base --is-ancestor` de `d279d8e`, `67d306e`, `ef5fc85`, `b8ae699` y `71b42f3` contra HEAD (todos 1); `git branch -a --contains` y `git tag --contains` de esos commits (vacío); `git cat-file -t` (commit)
- Recorrido de las siete versiones de `docs/qa/E8/acciones.md` en el rango: G8 = 0, cuenta = 0, `--directory` = 0, `python-build-standalone` = 2, sin la frase «La red fue PyPI y», sin `git push`
- `git grep -l` de la cuenta en cada commit del rango: 0. Diff `origin/v3...HEAD`: 1415 líneas agregadas, G8 = 0, cuenta = 0, `--directory` = 0, URL = 0
- `git log origin/v3..HEAD -- scripts/qa_gate.py` (`658b68b`, cita ADR-011); `git show -U1 658b68b -- scripts/qa_gate.py`
- `git reflog --date=iso -20`: el último es `reset: moving to 15494f4`; 0 push y 0 force. Lectura de `docs/qa/E8/acciones.md` en HEAD
