# Hallazgos E0 — ciclo 2

Revisión de QC-6 sobre `docs/qa/E0/gate.json` (exit_code 0, test_count 127), el código de `scripts/qa_gate.py`, `scripts/qa_sabotage.py`, `scripts/hooks/pre_push.py`, `.grok/config.toml`, `tests/test_qa_gate.py`, `tests/test_qa_sabotage.py`, `tests/test_pre_push.py`, `tests/test_e0_install.py` y las filas de `docs/qa/TRAZABILIDAD.md`. No se reejecutó la suite: la corrida es la del gate. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

## Crítico

No hay hallazgos críticos.

## Importante

Abiertos. Cada uno bloquea el cierre.

### I-3 — La trazabilidad de las secciones 2, 6 y 7 sigue incompleta, y R-198 no prueba su requisito

Lo que el ciclo 1 pedía y sí quedó: fila de formato XER (R-105, R-110 a R-121), una fila por métrica DCMA (R-130 a R-143) y una fila por caso borde de la sección 7 (R-190 a R-195, más R-116 para restricciones, R-114 y R-164 para LOE, WBS e hitos, R-119 para multiproyecto y R-120 para baseline). R-002 y R-063 ahora apuntan a un test que hace lo que dicen; ver el cierre más abajo. Una fila de etapa futura puede citar un test que todavía no existe: eso no es verde y no es fallo de E0.

Siguen sin R-xxx requisitos que la sección 10.2 pide en esta tabla:

- Sección 6, M1: «No evaluable» con motivo si falta baseline o fecha objetivo. Chequeos adicionales sin fila: lag mayor que la duración de la sucesora, vínculos SF como hallazgo de calidad (R-113 solo cubre el código `PR_SF` en el motor), puntos de convergencia, calendario distinto al dominante, LOE con lógica impropia, actividades sin códigos o WBS requeridos, densidad de lógica. Perfiles `dcma_estricto`, `corporativo` y `contratista`, e índice compuesto de 0 a 100.
- Sección 6, M2: modo A frente a modo B, y continuidad de la ruta crítica. R-032 nombra cadena driving, float paths y bandas, no estos dos.
- Sección 6, M5: distribuciones triangular, BetaPERT y uniforme; correlación Iman-Conover; eventos de riesgo; salidas P50, P80, P90, criticidad, SSI, crucialidad, Spearman y efecto de convergencia. R-168 solo dice tornado por cono y Monte Carlo con semilla.
- Sección 7: `scripts/gen_synthetic.py` sin tablas inventadas. R-006 solo mira `gen_scale`. El generador viejo sigue declarando la tabla `SYNTH` en `scripts/gen_synthetic.py`. También faltan los casos pequeños con esperado a mano, la red realista del generador de escala (WBS, feriados, mezcla de vínculos, avance, dos a tres predecesoras, cadena larga) más allá de los nombres de tabla, y que `sanitize_fixture.py` anonimice `ERMHDR` antes de versionar `p6_verified`.
- Sección 2: los hooks pre-commit y pre-push que rechazan xer, mpp, XML de cronograma, `data/real/`, `.env` y rutas de perfil. R-003 es G8 sobre un xer; R-310 es el destino del push. No hay fila del hook.

R-198 es fila de E0 y el test citado no prueba el requisito. Dice «la sesión no lee el golden real» y apunta a `tests/test_qa_gate.py::test_project_config_denies_real_data_and_dotenv`. Ese test solo busca en `.grok/config.toml` las cadenas `Read/Edit/Grep(**/data/real/**)` y `(**/.env)`. No menciona `ATLASPMO_GOLDEN_DIR` ni comprueba que nadie lea esa ruta. Es el mismo defecto que R-002 y R-063 tenían en el ciclo 1.

### I-6 — G5 no falla si el perfil `qa` tiene menos de 500 ejemplos

La sección 8.3 hace fallar G5 si falta un invariante a–e o si corre con menos de 500 ejemplos en el perfil `qa`. `check_g5` no corre hypothesis: lee el texto de `tests/property/*.py`. La condición de los 500 es un AND:

```python
if "max_examples=500" not in blob and 'register_profile("qa"' not in blob:
```

Con `register_profile("qa", max_examples=1)` y los cinco nombres de invariante, las dos partes no se cumplen a la vez y G5 devuelve pass. El caso que pasa (`test_g5_passes_when_the_five_invariants_use_the_qa_profile`) incluye `max_examples=500`, así que no ve el agujero. El caso que falla solo cubre la carpeta ausente. Hoy G5 está en linea_base porque no existe `tests/property`; el control que E0 entrega igual aceptaría un perfil de un ejemplo.

### I-7 — G7 no exige que cada skip esté en la lista

La sección 8.3 hace fallar G7 si un `skip`, `skipif` o `xfail` no está en `docs/qa/skips.toml` con un motivo aceptado. `check_g7` solo falla por marcas en tests cuando la tabla está vacía. Si `skips.toml` tiene una fila con motivo aceptado, cualquier skip extra en `tests/` pasa. `test_g7_fails_when_a_skip_is_not_listed` cubre el toml vacío, no este caso. Hoy el pass es honesto: no hay marcas y el toml no tiene filas. El control no implementa la regla para cuando sí las haya.

### I-8 — G8 no mira XML de cronograma

La sección 8.3 hace fallar G8 si hay `.xer`, `.mpp` o XML de cronograma fuera de `tests/fixtures/`. `check_g8` solo trata los sufijos `.xer` y `.mpp`. No hay `xml` en `scripts/qa_gate.py`. El test que falla usa `notes.xer`. En este árbol los XML de cronograma están bajo `tests/fixtures/`; esta corrida no esconde un archivo. El control marcado pass no vería uno fuera de fixtures. El hook `scripts/hooks/reject_schedules.py` sí reconoce marcadores P6 y MSPDI, pero el gate no lo usa.

### I-9 — G12 no compara cobertura ni benchmarks

La sección 8.3 hace fallar G12 si baja la cantidad de tests, si la cobertura cae más de 0,5 puntos o si un benchmark empeora más de 20 % respecto de la etapa anterior. `check_g12` solo compara el «N passed» de una pytest nueva con `test_count` del `gate.json` anterior. No lee cobertura ni benchmarks. En E0 el pass es honesto: no hay etapa anterior. Los tests cubren esa rama y la caída del conteo, no las otras dos condiciones.

### I-10 — El pre-commit no corre G8

La sección 14.2 pide hooks pre-commit y pre-push con G8. El pre-push sí llama a `check_g8` y, además, exige `origin` y `refs/heads/v2` (I-4 cerrado). `.pre-commit-config.yaml` en pre-commit solo ejecuta `scripts/hooks/reject_schedules.py`, que rechaza xer, mpp y XML con marcador de cronograma. No rechaza `.env`, `data/real/` ni una ruta de perfil. Un commit local de esos archivos no lo frena este hook; lo vería el pre-push o el gate si el archivo queda versionado.

## Cerrados en este ciclo

### I-1 — Cada control tiene un caso que pasa y uno que falla

`tests/test_qa_gate.py` llama al control real en los dos sentidos:

- G1 `test_g1_fails_on_an_unused_import`, `test_g1_passes_a_clean_tree` (`ruff check` y `ruff format --check`).
- G2 `test_g2_fails_on_a_bad_return`, `test_g2_passes_a_typed_module`.
- G3 `test_g3_fails_when_pytest_fails`, `test_g3_passes_when_pytest_passes_and_uv_is_unavailable` (el pass cita ADR-004).
- G4 `test_g4_fails_when_pytest_fails`, `test_g4_passes_when_the_json_meets_the_threshold`. El umbral de la sección 8.1 lo aplica `judge_coverage` (90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `logic`; 80 % de líneas en el resto): `test_judge_coverage_fails_under_the_engine_line` y `test_judge_coverage_passes_when_thresholds_hold`.
- G5 a G13: un fail y un pass cada uno. G13 además falla con `alcance: muestra` y con kill score bajo el umbral, y solo pasa con `alcance: completo` en el umbral.

### I-2 — Hay herramienta de mutación, y G13 no está en pass

`scripts/qa_sabotage.py` cambia un operador o un `return`, corre pytest y restaura el archivo. `tests/test_qa_sabotage.py::test_sample_kills_a_return_and_keeps_an_equivalent_comparison` usa `return n > 0`: el mutante `>=` sigue cumpliendo el test (vivo) y `return None` lo rompe (muerto). El informe dice `alcance: muestra`. No existe `docs/qa/E0/sabotaje.md`. G13 en linea_base con «no medido: falta el informe de qa-sabotaje» es honesto. No se exige kill score de todo `src` para cerrar E0.

### I-4 — El pre-push exige el remoto `origin`

`scripts/hooks/pre_push.py` rechaza si el remoto no es `origin` (`PRE_COMMIT_REMOTE_NAME` o `argv[1]`) y si algún ref no es `refs/heads/v2` ni `v2`. `tests/test_pre_push.py` cubre remoto ajeno, otra rama, G8 en fallo y la aceptación de `origin` más `refs/heads/v2`.

### I-5 — La config niega `.env`

`.grok/config.toml` niega Read, Edit y Grep sobre `**/data/real/**`, `**/.env` y `**/.env.*`. `test_project_config_denies_real_data_and_dotenv` afirma las dos primeras para las tres herramientas.

### R-002 y R-063

- R-002 cita `test_g1_passes_a_clean_tree`, que ejecuta `check_g1`: `ruff check .` y `ruff format --check .`.
- R-063 y R-307 citan `tests/test_e0_install.py::test_dev_tools_import_and_the_install_was_recorded`. Importa `hypothesis`, `pytest_benchmark` y `pytest_cov`, y exige en `docs/qa/E0/acciones.md` las cadenas `uv sync --group dev` y `sin administrador`. Esa fila de la bitácora está.

### M-2 — `docs/ESTADO.md` ya no está en QC-3

Dice ciclo 2, control QC-6. Cerrado.

## Menor

No bloquean.

### M-1 — No quedó la salida en rojo previa al arreglo de B-17

Igual que en el ciclo 1. En `docs/qa/E0/` no está la salida de colección con `No module named 'scripts'`. Hoy `pyproject.toml` tiene `pythonpath = [".", "src"]` y `tests/test_phase2.py` importa `scripts.run_conformance`. No cambia el resultado del gate.

### M-3 — R-310 cita solo el rechazo del remoto ajeno

El requisito dice «solo acepta origin y refs/heads/v2». La fila apunta a `test_pre_push_rejects_a_foreign_remote`, que prueba el remoto. La rama y el caso que acepta están en `test_pre_push_rejects_another_branch` y `test_pre_push_accepts_origin_v2`, en el mismo archivo. El código hace las dos cosas. No es un test de otro tema; la cita no nombra los tres.

## Línea base — no cumplida

G4, G5, G6 y G13 están en `linea_base`. No son pass. La excepción de la sección 10.2 permite ese estado en E0 y, por sí sola, no rechaza la etapa. G10 ya no está en linea_base: pasó porque los archivos citados por E0 existen (ADR-014). Eso no declara verdes los tests de etapas futuras.

| Control | Estado en `gate.json` | Qué muestra el detalle |
|---|---|---|
| G4 | linea_base | Umbral de la sección 8.1 aplicado y no alcanzado: calendars ramas 81,0; engine líneas 83,5 y ramas 72,4; logic líneas 76,1 y ramas 60,6; model ramas 62,5. El recorte dice `127 passed`. |
| G5 | linea_base | No existe `tests/property`. |
| G6 | linea_base | No medido: no hay `tests/perf`. |
| G13 | linea_base | No medido: falta el informe de qa-sabotaje. La herramienta y su muestra están; no hay corrida `alcance: completo`. |

## Gate bloqueante

En verde, y no alcanza para aprobar mientras I-3 e I-6 a I-10 sigan abiertos.

- Exit code: 0. test_count: 127, tomado del «127 passed» de la corrida de cobertura que quedó en el detalle de G4.
- Pass: G1, G2, G3, G7, G8, G9, G10, G11, G12.
- G11: desde `108f11a` hay cambios en `scripts/qa_gate.py`; el historial de esos commits cita ADR-011 y ADR-014. El pass «cambios protegidos citan un ADR» coincide con ese log.
- G12 en pass es «sin etapa anterior», no una comparación de cobertura.
- G3 no ejecutó `uv run pytest`. El detalle dice `python -m pytest exit 0` y la frase de ADR-004. No se declara cumplido el comando `uv run pytest` en este equipo.
