# Estado

## v3 — en curso

Base `8a268ca0c4f626df84ae6992c7bee5bab7597577` (`8a268ca`), rama `v3` desde `origin/claude/beautiful-goodall-m0q2zj`. Árbol limpio en ese commit al arrancar. La especificación que manda es `docs/MEGAPROMPT_v3.md`.

Arranque de la sección 15 medido en `docs/qa/E7/inicio.md`. Equipo: Intel64 Family 6 Model 170 Stepping 4, 31,4 GB, Windows-11-10.0.26200-SP0.

| Etapa | Estado |
|---|---|
| E7 | Ciclo 2, gate en verde (237 tests, cobertura 91,3, G1–G12 pass, G13 info). El empaquetado ya no ensancha el crítico ni las conductoras cuando el real trae segundos; el rechazo del ciclo 1 está en `docs/qa/E7/hallazgos.md`. Veredicto del revisor pendiente. `cpm_30k` 0,237 s y `dcma_30k` 1,494 s siguen activas (tiempos del ciclo 1; el gate del ciclo 2 volvió a pasarlas). |
| E8 | pendiente |
| E9 | pendiente |
| E10 | pendiente |

Línea base de referencia en este equipo: lectura 0,655 s; CPM 9,892 s; DCMA 10,127 s; redundancia y Monte Carlo más de 30 min.

## v2 — reporte final

Base `b131428` (fase 5) más el megaprompt en `108f11a`. Rama `v2`. E0 a E6 quedaron RECHAZADA-BLOQUEADA. Ninguna es APROBADO. No hay cuarto ciclo en ninguna. El reporte es condicional a I-3 y a esos bloqueos. Equipo de las mediciones: Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise (`docs/qa/E1/perf.md`).

### Por etapa

| Etapa | Veredicto | Ciclos | Gate final | Último commit del cierre |
|---|---|---|---|---|
| E0 | RECHAZADA-BLOQUEADA | 3 | salida 0. Pass G1, G2, G3, G7, G8, G9, G11, G12. linea_base: G4, G5, G6, G10, G13. 137 tests | `9bcf40a` |
| E1 | RECHAZADA-BLOQUEADA | 3 | salida 1. 173 tests. Cobertura 88.8. Fail G4 y G13 (kill_score 54.0) | `19f34bd` |
| E2 | RECHAZADA-BLOQUEADA | 3 | salida 1. 175 tests. Cobertura 88.9. Fail G4. G13 no medido | `8f8f2cf` |
| E3 | RECHAZADA-BLOQUEADA | 3 | salida 1. 201 tests. Cobertura 89.4. Fail G4. G13 no medido | `2ff0eac` |
| E4 | RECHAZADA-BLOQUEADA | 3 | salida 1. 205 tests. Cobertura 89.5. Fail G4. G13 no medido | `a8e5106` |
| E5 | RECHAZADA-BLOQUEADA | 3 | salida 1. 212 tests. Cobertura 89.8. Fail G4. G13 no medido | `b1b3dea` |
| E6 | RECHAZADA-BLOQUEADA | 3 | salida 1. 216 tests. Cobertura 89.8. Fail G4 y G13 | `6fea288`, sobre el gate `7de4564` |

E0 a E4 ya estaban en `origin/v2` antes de este tramo. E5 se empujó en `0f8461d..b1b3dea`. E6 se empuja con este cierre.

Gate G1–G13 del último gate, el de E6 ciclo 3 (`docs/qa/E6/gate.json`): pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 216. cobertura_total 89.8. Modelo 100.0 / 100.0. Calendars 85.2 / 70.9. Engine 89.4 / 79.5. Logic 88.6 / 75.3. Resto líneas 90.2. G13: no medido, falta el informe. G6: 4 passed. Ese verde no es la sección 11.

### Brechas

| ID | Estado | Evidencia |
|---|---|---|
| B-01 | abierta | La pantalla carga, ejecuta, exporta, muestra el visor si hay tabla CPM, corre un lote y guarda métricas. No es el e2e de la fila E5. E5 bloqueada. I-32, I-33, I-34 |
| B-02 | abierta | El filtro de 30 000 midió 0.345 s. La confirmación no se corrió. En 400 actividades tardó 58.1 s. E2 bloqueada |
| B-03 | cerrada en la suite | `3ecec3c`. El conjunto se confirma y un delta distinto de cero no se entrega. G3 de E6 pasó |
| B-04 | cerrada en la suite | El mismo corte. Sigue sin lista de usuario contrastada con un cronograma real |
| B-05 | cerrada en la suite | Cadena de 60 000 en `tests/test_e1_cycles.py`. G3 pasó |
| B-06 | cerrada en la suite | Horizonte de 20 años en `tests/test_e1_calendar.py`. G3 pasó |
| B-07 | abierta | Un CPM de 30 000 midió 9.401 s. Monte Carlo 30 000 por 1 000 no se corrió. El tornado no recorta al cono. numba no está cargado |
| B-08 | abierta, `[VALIDAR]` | El código impone la fecha obligatoria. P6 no lo confirmó. ADR-006 y el checklist |
| B-09 | abierta, `[VALIDAR]` | Longest path existe. La comparación con P6 no |
| B-10 | abierta | Hay un oráculo de un tramo (ADR-017). Faltan el solape SS y el feriado con otra firma |
| B-11 | abierta | El numerador de BEI cuenta cierres tempranos en el corte `af56826`. No hay doble firma |
| B-12 | abierta | Bandas configurables y cadena driving del motor. No hay multiple float paths ni continuidad desde la fecha de corte. El modo A no marca driving |
| B-13 | abierta | `fact_timephased` guarda la duración remanente en el balde `corte`. No hay histograma, sobreasignación ni curva por periodo. El PV sigue lineal |
| B-14 | abierta | Hay `gen_scale.py`. No están todos los bordes de la sección 7 ni esperados con doble firma |
| B-15 | cerrada en G5 | Invariantes a–e con perfil qa. G5 de E6 en pass |
| B-16 | abierta | G6 pasa y no sustituye la sección 11. I-37 |
| B-17 | abierta | `python -m pytest` pasa. `uv run pytest` no arranca (ADR-004). M-31 |
| B-18 | cerrada en G1 | ruff check y format en pass |
| B-19 | cerrada en el árbol | Trazabilidad, 13 agentes y `MEGAPROMPT_v2.md`. E0 igual quedó bloqueada por I-3 |
| B-20 | cerrada en la suite | Bytes cp1252 indefinidos se leen (`1ebebd5`). G3 pasó |
| B-21 | abierta, `[VALIDAR]` | El hito de las 16:00 queda para P6 |
| B-22 | abierta | v2 usa commits chicos y G11 y G12 pasan. La historia de fase-1 a fase-5 no se reescribió |
| B-23 | abierta | Sigue en la historia de fase-1 a fase-5. No se reescribe. Lo decide Nicolás |

### Pruebas

Comando de G3: `py -3.12 -m uv run python -m pytest`. En el gate de E6: 216 passed, 4 deselected. `uv run pytest` no se usa (ADR-004).

Cobertura del mismo gate: total 89.8. Modelo 100 / 100. Calendars 85.2 / 70.9. Engine 89.4 / 79.5. Logic 88.6 / 75.3. Resto, líneas 90.2. Esas tres parejas están bajo 8.1.

Kill score: el único informe completo está en `docs/qa/E1/sabotaje.md` (54.0; engine 60.2; calendars 45.5; logic 52.0). `redundant.py` cambió después. E2 a E6 no lo reejecutaron. G13 de E6 es no medido. 54.0 no es el score de E6.

Benchmarks contra la sección 11:

| Criterio | Meta | Resultado |
|---|---|---|
| Lectura de 30 000 | < 15 s | medido, 0.197 s (`docs/qa/E1/perf.md`) |
| DCMA y chequeos | < 10 s | `evaluate` midió 0.261 s (`docs/qa/E3/perf.md`). En esa red CPLI queda `no_evaluable`. El tiempo no incluye el CPM |
| Redundancia con confirmación | < 3 min | no corrida en 30 000. Filtro 0.345 s. En 400 actividades, 58.1 s (`docs/qa/E2/perf.md`). La proyección no cumple |
| Monte Carlo 30 000 por 1 000 | < 5 min | no corrido. Un CPM midió 9.401 s. La proyección de unas 2,6 h no es una medición y no cumple (`docs/qa/E4/perf.md`) |
| Conformidad contra P6 | ≥ 99,5 % y 100 % explicado | no corrido. El script no abre la carpeta golden |
| XER limpio en P6 | delta cero al reprogramar | no corrido en P6. La suite no entrega un archivo si el delta interno no es cero |
| Round-trip | byte a byte | la suite lo cubre en sintéticos. Un real no se reimportó |
| Instalación | sin administrador | no se pidió un instalador de administrador |
| Pruebas en verde | unitarias, propiedades, conformidad, rendimiento | G3, G5 y G6 pasan. La conformidad de la sección 11 y parte del rendimiento no están medidos |

### Hallazgos

No hay críticos en el veredicto de E6. Importantes abiertos: I-3; I-11 a I-14 (E1); I-15 a I-18 (E2); I-19 a I-24 (E3); I-25 a I-29 (E4); I-30 a I-34 (E5); I-35 (G4), I-36 (G13 no medido) e I-37 (sección 11 no medida). Menores de E6: M-31 a M-36. M-36 decía que el checklist no estaba en los ciclos. Este reporte lo copia abajo. No convierte la etapa en APROBADO.

### Supuestos `[VALIDAR]`

- B-08, fecha obligatoria sobre la lógica: ADR-006, y el caso sigue para P6.
- B-09, longest path frente a holgura: el mismo grupo de decisiones de motor.
- B-21, hito que cae a las 16:00: ADR-006.
- Un tramo de CPLI: ADR-017. No es la doble firma de B-10.
- Un camino alterno de redundancia: ADR-018. No es la confirmación de 30 000.

### Para Nicolás

El checklist de `docs/VALIDACIONES_PENDIENTES.md`, en este orden:

1. Denegar en `~/.grok/config.toml` la ruta absoluta de la carpeta golden. Esta sesión no la escribe.
2. Mantener los golden cifrados y desmontados, y no definir `ATLASPMO_GOLDEN_DIR` en la terminal de Grok.
3. Importar los sintéticos en P6, reprogramar, reexportar, sanear y dejarlos en `tests/fixtures/p6_verified/`.
4. Confirmar `CS_MANDSTART` y `CS_MANDFIN`.
5. Confirmar el hito de inicio que cae a las 16:00.
6. Correr la conformidad con el golden y pegar solo la salida anonimizada.
7. Reimportar un XER limpio, reprogramar y comprobar delta cero.
8. Abrir `powerbi/AtlasPMO.pbip` en Power BI Desktop y refrescar.
9. Para `.mpp`: Java en el PATH y `uv sync --extra mpp`.
10. Decidir si se reescribe la historia de B-23. Esta rama no lo hace.

### Para la v3 del megaprompt

- La sección 0.3 pide detenerse al tercer rechazo. Esta corrida, por la regla explícita de Nicolás y ADR-013, continúa y marca RECHAZADA-BLOQUEADA. Conviene decir cuál de las dos manda.
- G4 heredado impide cerrar E1 a E6 aunque el corte de la etapa no toque calendarios, motor ni lógica. Conviene un umbral por etapa, o decir que la cobertura heredada no se reabre.
- G6 en verde no es la sección 11. G10 comprueba que el archivo citado existe. Conviene separar “el archivo está” de “el requisito se cumple”.
- La doble firma no cabe en un solo autor. Conviene un estado `pendiente de segunda firma` que no sea ni pass ni un bloqueo de tres ciclos.
- `uv run pytest` falla en este equipo (ADR-004). El gate ya usa `python -m pytest`. Conviene que el megaprompt nombre ese comando.
- B-10 en el megaprompt es CPLI y B-11 es BEI. El contrato de E3 los rotuló al revés. Conviene no reusar el contrato viejo como fuente.

### Bitácora

- E6 quedó RECHAZADA-BLOQUEADA. No es APROBADO. No hay cuarto ciclo. Gate ciclo 3: 216 tests, cobertura 89.8, fail G4 y G13. Abiertos I-35, I-36 e I-37. Los resultados quedan condicionales a I-3 y a los bloqueos de E0 a E5. Monte Carlo 30 000 por 1 000 no se corrió. Un CPM de 30 000 midió 9.401 s.
- Gate E6 ciclo 2: iguales cifras que el ciclo 1. test_count 216. cobertura_total 89.8. Fail G4 y G13. Nota en `docs/qa/E6/ciclo2.md`.
- Gate E6 ciclo 1: pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 216. cobertura_total 89.8. Calendars 85.2/70.9, engine 89.4/79.5, logic 88.6/75.3. G13 no medido. El 99,5 % no está medido.
- Gate E5 ciclo 3: pass G1, G2, G3, G5, G6, G7, G8, G9, G10, G11, G12. Fail G4 y G13. test_count 212. cobertura_total 89.8. Calendars 85.2/70.9, engine 89.4/79.5, logic 88.6/75.3. G13 no medido. Nota en `docs/qa/E5/ciclo3.md`.
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
