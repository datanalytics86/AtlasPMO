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
- Reiniciar Grok en la raíz del repositorio y abrir `/agents`.
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

## Fase 2 — en `fase-2`

Encima de la fase 1. Sin push.

### Entregado

- Parser de `clndr_data` limitado a la forma publicada y reloj laboral.
- CPM con FS/SS/FF/SF, lags positivos y negativos, tres tratamientos de avance, hitos, restricciones citadas, LOE y WBS después del pase.
- Modo B, prueba DCMA 12, redundancia con confirmación, limpieza que solo borra `TASKPRED`, Gantt de Plotly y `scripts/run_conformance.py`.

### Evidencia (2026-10-20)

- `py -3.12 -m uv run python -m pytest -q` — 59 passed in 1.95s.
- `py -3.12 -m uv run python -m ruff check .` — All checks passed.
- `py -3.12 -m uv run python -m mypy src` — Success: no issues found in 42 source files.
- La conformidad 100 % del caso a mano está en `test_conformance_is_exact_when_stored_dates_match` (`ratio == 1`). No se midió contra P6.
- `plotly` 7.1.0 quedó instalado desde wheel. El Gantt se prueba por la cantidad de barras, no dentro del navegador: la UI sigue sin cargar un archivo.

### Abierto

- `p6_verified` no está. El script lo omite.
- `ATLASPMO_GOLDEN_DIR` no se abre ni se listan sus nombres. El 99,5 % y el delta cero dentro de P6 quedan para la iteración con Nicolás.
- No se midió el criterio de redundancia bajo 3 minutos de la sección 11.

## Fase 3 — en `fase-3`

Encima de la fase 2. Sin push.

### Entregado

- Monte Carlo en Python puro, con semilla en el manifiesto. Distribuciones triangular, BetaPERT y uniforme. Iman-Conover solo si hay correlación y algún rango con ancho.
- Tornado por atraso de horas, criticidad, y SSI, crucialidad y Spearman cuando hay varianza.
- EVM y Earned Schedule con los campos ya cargados. El tope de recurso queda `no_evaluable`.

### Evidencia (2026-10-20)

- `py -3.12 -m uv run python -m pytest -q --tb=line` — 73 passed in 3.61s.
- `py -3.12 -m uv run python -m ruff check .` — All checks passed.
- `py -3.12 -m uv run python -m mypy src` — Success: no issues found in 48 source files.
- La invariante de varianza cero está en `test_zero_variance_reproduces_the_cpm`: cinco iteraciones terminan el mismo miércoles 16:00 que el CPM, y la criticidad es 1 en las dos actividades de la cadena.
- El EVM a mano está en `test_hand_evm_and_earned_schedule`: PV 50, EV 50, AC 40, SPI 1, CPI 1,25, ES 8 h, AT 8 h, SPI(t) 1, IEAC(t) 16. No se contrastó con P6.
- numba no se cargó. No se midió el criterio de 30 000 actividades por 1 000 iteraciones bajo 5 minutos.

### Abierto

- El EVM contra un caso real y el tiempo de Monte Carlo de la sección 11 quedan para la iteración con Nicolás.

## Fase 4 — en `fase-4`

Encima de la fase 3. Sin push.

### Entregado

- Lector MSPDI con fixture `tests/fixtures/synthetic/mspdi/chain.xml`.
- Comparación de updates por `task_code`, lote con ranking en Excel, biblioteca DuckDB y Parquet en esquema estrella.
- PBIP mínimo en `powerbi/`, con parámetro `ParquetFolder`.
- Extra `[mpp]` declarado. No se ejecuta: no hay Java.

### Evidencia (2026-10-20)

- `py -3.12 -m uv run python -m pytest -q --tb=short` — 81 passed in 2.43s.
- `py -3.12 -m uv run python -m ruff check .` — All checks passed.
- `py -3.12 -m uv run python -m mypy src` — Success: no issues found in 56 source files.
- `duckdb` 1.5.6 quedó instalado desde el wheel `cp312-win_amd64`. `mpxj` no queda en el entorno por defecto.
- El PBIP no se abrió en Power BI Desktop.

### Abierto

- Nicolás abre el PBIP y refresca el modelo.
- La lectura `.mpp` espera Java y el extra `[mpp]`.

## Fase 5 — en `fase-5`

Encima de la fase 4. Sin push. Sin merge. Sin pull request.

### Entregado

- `docs/MANUAL_USUARIO.md` y el paso de instalación del `README.md`, con los comandos que arrancan en este equipo.
- Las aproximaciones que la revisión encontró fuera del resultado ahora quedan en `ModuleResult.approximations`. Ver ADR-009.
- No se tocó el rendimiento. No se cargó numba.

### Evidencia (2026-10-20)

- `py -3.12 -m uv run python -m pytest -q --tb=short` — 84 passed in 2.40s.
- `py -3.12 -m uv run python -m ruff check .` — All checks passed.
- `py -3.12 -m uv run python -m mypy src` — Success: no issues found in 56 source files.
- La interfaz no cambió. Sigue sin cargar un archivo. `test_ui` entra en las 84 pruebas y no abre un navegador.

### Sección 11, sin medidas nuevas

| Criterio | Qué hay |
|---|---|
| Lectura de 30 000 actividades | El test exige menos de 15 s solo sobre `read_xer`. El tiempo interno no se imprimió. La fase 1 no lo volvió a medir. |
| DCMA + chequeos bajo 10 s | No medido. |
| Redundancia bajo 3 min | No medido. |
| Monte Carlo 30 000 × 1 000 bajo 5 min | No medido. numba no se cargó. |
| Conformidad CPM ≥ 99,5 % en reales | No corrido. `ATLASPMO_GOLDEN_DIR` no se abre. |
| Conformidad 100 % en `p6_verified` | No hay `p6_verified`. El caso a mano da ratio 1. No es una medida de P6. |
| XER limpio importa en P6 y, al reprogramar, delta cero | No ejecutado. El checklist está en el manual. |
| Round-trip XER | Cubierto por los tests de la fase 1 en fixtures sintéticos. |
| Instalación sin administrador | `py -3.12 -m uv sync --group dev`. No pide permisos de administrador. |
| Pruebas en verde | 84 passed. No hay una batería de rendimiento aparte. |

### Qué queda para Nicolás

- Importar los sintéticos en P6 y devolver los `p6_verified`.
- Contrastar M1, el CPM y el EVM con un cronograma real, fuera del repositorio.
- Seguir el checklist de reimportación del manual. Esta corrida no lo hizo.
- Abrir `powerbi/AtlasPMO.pbip` en Power BI Desktop y refrescar. Aquí no se abrió.
- Si quiere `.mpp`, hace falta Java en el PATH y `uv sync --extra mpp`. El entorno por defecto no trae `mpxj`.
- No hay push de `fase-1` a `fase-5`.
