# Hallazgos E0 — ciclo 3

Revisión de QC-6 sobre `docs/qa/E0/gate.json` (exit_code 0, test_count 137), el código de `scripts/qa_gate.py`, `scripts/run_conformance.py`, `scripts/hooks/pre_commit_g8.py`, `scripts/hooks/reject_schedules.py`, `.pre-commit-config.yaml`, `tests/test_qa_gate.py`, `tests/test_conformance_stub.py`, `tests/test_pre_commit_g8.py`, `tests/test_reject_schedules.py` y las filas de `docs/qa/TRAZABILIDAD.md`. No se reejecutó la suite: la corrida es la del gate. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

## Crítico

No hay hallazgos críticos.

## Importante

Abierto. Bloquea el cierre.

### I-3 — R-198 sigue sin probar que el script no abre el golden

Lo que el ciclo 2 pedía y sí quedó en `docs/qa/TRAZABILIDAD.md`:

- M1: R-320 a R-329 (no evaluable, lag mayor que la sucesora, SF de calidad, convergencia, calendario distinto, LOE impropio, códigos o WBS, densidad, tres perfiles, índice 0 a 100).
- M2: R-330 (modo A y modo B) y R-331 (continuidad).
- M5: R-340 a R-344 (triangular, uniforme y BetaPERT; Iman-Conover; eventos; P50, P80, P90, criticidad, SSI, crucialidad y Spearman; convergencia).
- Sección 7: R-350, R-351 y R-352. R-350 dice explícitamente que SYNTH sigue en el generador viejo y no está en verde. `scripts/gen_synthetic.py` todavía declara la tabla `SYNTH`. Eso no se reabre: la fila lo deja fuera de verde a propósito.
- Hooks: R-312 y R-313.

Esas filas de etapa futura citan archivos que no existen (`tests/test_e3_dcma.py`, `tests/test_e3_extra.py`, `tests/test_e3_profiles.py`, `tests/test_e3_paths.py`, `tests/test_e4_outputs.py`, `tests/test_e1_synthetic.py`, `tests/test_e1_scale_shape.py`). No están en verde y no son fallo de E0. G10 solo mira las 22 filas de E0 y cada una cita un `tests/*.py` que sí existe. R-330, R-340, R-341, R-342 y R-352 citan tests que ya están en el árbol; eso tampoco pone la fila en verde.

Los casos pequeños con esperado en YAML ya los recorre `tests/test_phase1.py::test_hand_calculated_metrics` sobre `tests/fixtures/synthetic/cases/*.yaml`. R-193 cita ese test para extremos abiertos. R-351 no repite restricciones, dos a tres predecesoras ni cadena larga. No reabro el hallazgo por ese recorte: la fila de la red de escala existe y apunta a un test de E1 que aún no está.

Lo que no quedó: R-198 es fila de E0 y el test citado no prueba el requisito. La fila dice «con ATLASPMO_GOLDEN_DIR definido el script no abre esa carpeta» y el oráculo dice «bytes del archivo de prueba sin leer». Apunta a `tests/test_conformance_stub.py::test_stub_exits_and_leaves_files_untouched`. Ese test hace tres cosas: fija la variable en un temporal, escribe `secret.xer` con los bytes `SECRET`, y tras `main()` comprueba que esos bytes siguen iguales y que la salida no contiene la cadena `secret`.

Leer no cambia los bytes. Un `main()` que abra el temporal, lea cada `.xer` y no escriba ni imprima `secret` sigue en verde. Imprimir el contenido `SECRET` tampoco falla: la comparación distingue mayúsculas. Hoy `scripts/run_conformance.py` no usa la ruta: si la variable está definida, imprime una frase fija y sale 0. El código actual no abre la carpeta. El test no fija ese comportamiento. Es el mismo tipo de defecto que R-198 tenía en el ciclo 2.

## Cerrados en este ciclo

### I-6 — G5 falla si el perfil `qa` trae menos de 500 ejemplos

`check_g5` lee `tests/property/*.py` y `_qa_examples` saca el entero de `register_profile('qa', … max_examples=N)`. Si no hay número o es menor que 500, el control falla. `tests/test_qa_gate.py::test_g5_fails_when_the_qa_profile_has_too_few_examples` escribe `settings.register_profile('qa', max_examples=1)` con los cinco invariantes y espera fail. El caso que pasa sigue usando `max_examples=500`. Hoy G5 está en linea_base porque no existe `tests/property`. El agujero del ciclo 2, en el que un perfil de un ejemplo pasaba, ya no está en ese camino.

### I-7 — G7 exige una fila por test omitido

`check_g7` arma `ruta::función` por cada `skip`, `skipif` o `xfail` y falla si esa cadena no está en `docs/qa/skips.toml` con un motivo aceptado. `test_g7_fails_when_the_listed_skip_is_a_different_test` deja un skip en `tests/test_demo.py::test_a` y una fila de `tests/test_other.py::test_a` con motivo `dependencia_opcional`: el control falla. El caso pareado pasa cuando la fila nombra el mismo test. Hoy el pass del gate es honesto: no hay marcas y `skips.toml` no tiene filas.

### I-8 — G8 mira XML de cronograma

`check_g8` trata `.xml` versionado fuera de `tests/fixtures/` si los bytes traen `APIBusinessObjects` o `http://schemas.microsoft.com/project`. `test_g8_fails_on_schedule_xml` usa el marcador P6 y espera fail. `test_g8_allows_plain_xml` usa `<note/>` y espera pass. En este árbol los XML de cronograma están bajo `tests/fixtures/`. El pass de esta corrida no esconde uno fuera de fixtures.

### I-9 — G12 compara cobertura y benchmarks cuando los dos números existen

`check_g12` falla si `coverage_percent` de la etapa anterior menos la actual es mayor que 0,5, y si un benchmark actual supera en más de 20 % al anterior, solo cuando ambos valores están. `test_g12_fails_when_coverage_drops` baja de 90 a 80. `test_g12_fails_when_a_benchmark_slows_more_than_twenty_percent` pasa `read_30k` de 10 a 13. En E0 `_previous_gate` devuelve vacío: el pass «sin etapa anterior; no hay regresion que medir» es honesto. No es una comparación de cobertura.

### I-10 — El pre-commit corre G8 y el hook de archivos frena `.env` y `data/real`

`.pre-commit-config.yaml` tiene el hook `commit-g8`, que llama a `scripts/hooks/pre_commit_g8.py`. Ese script corre `check_g8` y sale 1 si el estado no es pass. `tests/test_pre_commit_g8.py::test_pre_commit_rejects_when_g8_fails` fija un G8 en fallo y espera 1. `scripts/hooks/reject_schedules.py` rechaza un nombre `.env` o `.env.*` y cualquier ruta `data/real`. `tests/test_reject_schedules.py::test_env_and_real_data_are_rejected` cubre `.env`, `notes/.env.local` y `data/real/plan.xer`. Las rutas de perfil las sigue viendo G8, que este hook ya ejecuta.

## Menor

No bloquean.

### M-1 — No quedó la salida en rojo previa al arreglo de B-17

Igual que en los ciclos 1 y 2. En `docs/qa/E0/` no está la salida de colección con `No module named 'scripts'`. Hoy `pyproject.toml` tiene `pythonpath = [".", "src"]` y `tests/test_phase2.py` importa `scripts.run_conformance`. No cambia el resultado del gate.

### M-3 — Cerrado

R-310 ahora cita `test_pre_push_rejects_a_foreign_remote`, `test_pre_push_rejects_another_branch` y `test_pre_push_accepts_origin_v2`.

### M-4 — El respaldo de G5 puede contar otro `max_examples`

Si `register_profile('qa')` no trae `max_examples` en la misma llamada, `_qa_examples` usa el primer `max_examples=N` del archivo siempre que aparezca la cadena `qa`. Un 500 de otro perfil alcanzaría. El caso que el ciclo 2 pedía, `max_examples=1` dentro del perfil `qa`, sí falla.

### M-5 — El comando del gate no alimenta benchmarks

`run_gate` le pasa a `check_g12` solo la cobertura de G4. `write_report` guarda `"benchmarks": {}`. La comparación de tiempos corre si alguien llama a la función con los dos diccionarios, que es lo que hace el test. En E0 no hay etapa anterior ni tiempos: el pass no depende de esa rama.

### M-6 — `ecc1e56` toca el gate y no cita un ADR propio

Ese commit cambia `scripts/qa_gate.py`. El mensaje no trae `ADR-`. G11 igual da pass: busca `ADR-` en todo el log desde `108f11a`, y ahí ya están ADR-011 y ADR-014. No es un relajo de umbral. El pass coincide con ese log acumulado, igual que en el ciclo 2.

## Línea base — no cumplida

G4, G5, G6 y G13 están en `linea_base`. No son pass. La excepción de la sección 10.2 permite ese estado en E0 y, por sí sola, no rechaza la etapa. G10 pasó porque los 22 archivos citados por E0 existen. Eso no declara verdes los tests de etapas futuras ni las filas que aún no tienen archivo.

| Control | Estado en `gate.json` | Qué muestra el detalle |
|---|---|---|
| G4 | linea_base | Umbral de la sección 8.1 aplicado y no alcanzado: calendars ramas 81,0; engine líneas 83,5 y ramas 72,4; logic líneas 76,1 y ramas 60,6; model ramas 62,5. Cobertura total 87,5. El recorte dice `137 passed`. |
| G5 | linea_base | No existe `tests/property`. |
| G6 | linea_base | No medido: no hay `tests/perf`. |
| G13 | linea_base | No medido: falta el informe de qa-sabotaje. La herramienta y su muestra están; no hay corrida `alcance: completo`. |

## Gate bloqueante

En verde, y no alcanza para aprobar mientras I-3 siga abierto.

- Exit code: 0. test_count: 137, tomado del «137 passed» de la corrida de cobertura que quedó en el detalle de G4.
- Pass: G1, G2, G3, G7, G8, G9, G10, G11, G12.
- G3 no ejecutó `uv run pytest`. El detalle dice `python -m pytest exit 0` y la frase de ADR-004. No se declara cumplido el comando `uv run pytest` en este equipo.
- G11: el log desde `108f11a` cita ADR-011 y ADR-014. Ver M-6.
- G12 en pass es «sin etapa anterior», no una comparación de cobertura.
