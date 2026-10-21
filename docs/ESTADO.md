# Estado

## v2 — en curso

Base de la iteración: `b131428` (fase 5), más el megaprompt en `108f11a`. Rama `v2`. Brechas B-01 a B-23. Etapas E0 a E6.

- Etapa actual: E5, ciclo 3 en código, gate todavía no corrido. El ciclo 2 quedó RECHAZADO (rechazo 2 de 3). La pantalla manda el perfil a Calidad, separa resultados y exportaciones, ofrece el ranking del lote y guarda métricas en una biblioteca DuckDB. No hay avance parcial. El baseline no se asocia. La prueba de localhost sigue leyendo el archivo. No es APROBADO. Siguiente control: gate del ciclo 3. Siguen abiertos I-30, I-31, I-32, I-33 e I-34. E4 quedó RECHAZADA-BLOQUEADA. Los resultados de E5 son condicionales a I-3 y a los bloqueos de E0 a E4. Monte Carlo 30 000 por 1 000 no se corrió. Un CPM de 30 000 midió 9.401 s.
- Gate E5 ciclo 2: pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 210. cobertura_total 89.7. Calendars 85.2/70.9, engine 89.4/79.5, logic 88.6/75.3. G13 no medido. G12 compara 210 contra 205 de E4. Nota en `docs/qa/E5/ciclo2.md`.
- Gate E5 ciclo 1: pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 208. cobertura_total 89.6. Calendars 85.2/70.9, engine 89.4/79.5, logic 88.6/75.3. G13 no medido. La UI cargaba `minimal.xer` en AppTest, ejecutaba calidad, mostraba aproximaciones y ofrecía Excel. El baseline no se asociaba. La prueba de localhost lee `.streamlit/config.toml` y no abre un socket. Los resultados de E4 son condicionales a I-3 y a los bloqueos de E0, E1, E2 y E3. El filtro de 30k es 0.345 s. La confirmación de 30k no se midió y la proyección no cumple 3 minutos.
- Gate E4 ciclo 3: iguales cifras que el ciclo 1. Nota en `docs/qa/E4/ciclo3.md`. Pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 205. cobertura_total 89.5. Calendars 85.2/70.9, engine 89.4/79.5, logic 88.6/75.3. G13 no medido. Un CPM de 30 000 midió 9.401 s. Monte Carlo 30 000 por 1 000 no se corrió; la proyección no cumple 5 minutos. `fact_timephased` tiene el balde corte con la duración remanente. No es una curva por periodo. El tornado sigue siendo un CPM completo por actividad. Nota en `docs/qa/E4/ciclo2.md`.
- Gate E1 ciclo 2: pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 167. cobertura_total 87.9. Modelo líneas 100.0 y ramas 100.0. Siguen bajo 8.1: calendars líneas 81.6 y ramas 63.9, engine líneas 86.0 y ramas 74.8, logic líneas 87.3 y ramas 73.6. G13 sin reejecutar mutación: kill_score 54.0, engine 60.2, calendars 45.5, logic 52.0. G3 es `python -m pytest`; `uv run pytest` no arranca (ADR-004).
- E1 ciclos: 1 RECHAZADO (`797f559`), 2 RECHAZADO (`1773c0d`), 3 bloqueado. No hay cuarto ciclo.
- Corrección del ciclo 2, ya en `734efc9`: oráculo de un caso de CPLI en `tests/oracle/span.py` (ADR-017) y ramas de `Schedule.calendar_for` y `select`. No cierra calendarios, motor, lógica ni G13. QC-2 sigue incompleto fuera de ese caso.
- E0 ciclos: 1 RECHAZADO (`0f26968`), 2 RECHAZADO (`ecc1e56`), 3 bloqueado (`9bcf40a`). No hay cuarto ciclo (ADR-013).
- Hallazgo abierto de E0: I-3. R-198 no prueba que el script no abra `ATLASPMO_GOLDEN_DIR`. El script no la abre. Evidencia: `docs/qa/E0/hallazgos.md`, `docs/qa/E0/VEREDICTO.md`.
- Gate E0: salida 0. Pass: G1, G2, G3, G7, G8, G9, G10, G11, G12. linea_base, no cumplidos: G4, G5, G6, G13. test_count 137. Push en `f64ef03`.
- E1 integrado en local: `366209b` (xer-io) y `3ddbddd` (motor-cpm). QC-1 está en `docs/qa/E1/QC1_contrato.md` y es posterior al código (I-13).
- Lectura 30k realista: 0.197 s en `docs/qa/E1/perf.md`. Por debajo de 15 s. El resto de la sección 11 no está medido.
- B-23 queda en la historia de fase-1 a fase-5. No se reescribe.
- Ciclo 3, gate sobre `1e4c8bc`: salida 1. test_count 173. cobertura_total 88.8. Calendars líneas 85.2 y ramas 70.9. Engine líneas 89.4 y ramas 79.5. Logic líneas 87.3 y ramas 73.6. G13 sin reejecutar: kill_score 54.0, engine 60.2, calendars 45.5, logic 52.0. Sigue en fail. No es APROBADO.
- Filtro de 30 000: 0.345 s, 24 998 candidatos. Confirmación de 30 000: no corrida. En 400 actividades la confirmación tardó 58.1 s. La proyección no cumple 3 minutos. Evidencia: `docs/qa/E2/perf.md`.
- E2 ciclos: 1 RECHAZADO (`e41a452`), 2 RECHAZADO (`339cafd`), 3 bloqueado. No hay cuarto ciclo.
- Gate E3 ciclo 3: igual que el ciclo 2. Pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 201. cobertura_total 89.4. Calendars líneas 85.2 y ramas 70.9. Engine líneas 89.4 y ramas 79.5. Logic líneas 88.6 y ramas 75.3. G13: no medido, falta el informe de qa-sabotaje. No se copia el kill score de E1. La nota está en `docs/qa/E3/ciclo3.md`.
- Ciclo 2, en `docs/qa/E3/ciclo2.md`: el modo B publica la cadena driving que el motor ya calculaba. El test falló primero con `KeyError: driving_codes`. Multiple float paths y la continuidad desde la fecha de corte siguen sin implementarse. El ciclo 1 del gate tenía 200 tests.
- DCMA `evaluate` en 30 000 actividades no serie: 0.261 s, en `docs/qa/E3/perf.md`. Está bajo 10 s. En esa red CPLI queda `no_evaluable`. El tiempo no es un pase de la definición.
- Bandas de holgura configurables en modo A, con el corte por defecto 0, 10, 20 y 44. Cadena driving, multiple float paths y continuidad: no implementado. QC-2 sigue incompleto fuera del caso CPLI de ADR-017. No hay doble firma.
- Contrato en `docs/qa/E3/QC1_contrato.md`. Pruebas a mano en `tests/test_e3_dcma.py`, `tests/test_e3_gao.py`, `tests/test_e3_extra.py` y `tests/test_e3_profiles.py`.

### Hecho de la v1

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
