# Hallazgos E1 — ciclo 1

Revisión de QC-6 sobre `docs/qa/E1/gate.md`, `docs/qa/E1/gate.json` (exit_code 1, test_count 165), `docs/qa/E1/sabotaje.md`, `docs/qa/E1/QC1_contrato.md`, `docs/qa/E1/perf.md`, las primeras 20 líneas de `docs/ESTADO.md` y las secciones 8.1, 8.3, 8.5 y 11 de `docs/MEGAPROMPT_v2.md`. HEAD `b0c5039` (`test(qa): gate E1 ciclo 1, salida 1 (B-17)`). No se reejecutó la suite ni la mutación. No se leyó el código de producto en esta pasada. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

La regla de cierre exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de E0 no aplica: la sección 10.2 la limita a E0.

## Crítico

No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta. La lectura de 30k está bajo 15 s. Lo que `perf.md` deja sin medir no se anota aquí como crítico de tiempo superado: no hay cifra. Tampoco es un pass. Va en «No medido».

## Importante

Abiertos. Bloquean el cierre. No se cierran en este ciclo.

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. E0 está RECHAZADA-BLOQUEADA. `docs/qa/E1/QC1_contrato.md` condiciona E1 a ese hallazgo y dice que el script actual no abre la carpeta y que esta etapa no la abre. No se releyó el script ni la carpeta. No se cierra I-3.

### I-11 — G4 incumple 8.1

Estado: abierto. El gate lo deja en fail.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. G4 falla si eso no se cumple.

`docs/qa/E1/gate.md` marca G4 en fail:

- calendars líneas 81.6 < 90; ramas 63.9 < 85
- engine líneas 86.0 < 90; ramas 74.8 < 85
- logic líneas 87.3 < 90; ramas 73.6 < 85
- model ramas 62.5 < 85

El mismo detalle, en `gate.json`, añade model líneas 98.3 % y resto líneas 88.8 % y ramas 74.5 %. Esas dos cifras de líneas no son el fail. La cobertura_total que cita el control es 87.8. La tabla pegada en el detalle cierra con TOTAL 84 % (4003, 487, 1550, 355). Ni 87.8 ni 84 dejan el control en pass.

`docs/ESTADO.md` todavía dice, antes de este gate, un total de líneas 88.0 y que no es un pass de G4. La cifra de esta revisión es la del gate: 87.8, con los paquetes de arriba en fail. No se usa 88.0 para cerrar nada.

### I-12 — G13 bajo 70 y bajo 85 en engine, calendars y logic

Estado: abierto. El gate lo deja en fail.

8.3: en los módulos de la etapa el kill score falla si es menor que 85 % en `engine`, `calendars` y `analysis/logic`, o menor que 70 % en el resto. G13 en `gate.md`: kill_score 54.0 < 70; engine 60.2 < 85; calendars 45.5 < 85; logic 52.0 < 85.

`docs/qa/E1/sabotaje.md`, alcance completo:

- kill_score 54.0; killed 161; survived 137; invalid 4
- engine 60.2 (killed 62, survived 41, invalid 1)
- calendars 45.5 (killed 45, survived 54, invalid 1)
- logic 52.0 (killed 39, survived 36, invalid 2)
- io 71.4 (killed 15, survived 6, invalid 0)

io 71.4 no está en el texto de fail. No se abre un hallazgo contra io y no se usa para compensar el 54.0 ni los tres módulos bajo 85. La corrida es la de los mutantes de `cpm.py`, `worktime.py`, `redundant.py`, `clean.py` y `validate.py`. Cada mutante corrió el subconjunto de tests de su módulo, no la suite entera. Un mutante que no termina en 20 s cuenta como killed. El informe no separa cuántos murieron por tiempo. Con esa regla, que favorece el score, el resultado igual está bajo el umbral.

### I-13 — QC-1 tardío

Estado: abierto como desviación de proceso del ciclo 1. No se convierte en cumplimiento.

La sección 8.4 exige el contrato antes de escribir código. `docs/qa/E1/QC1_contrato.md` dice que se escribió después del código de xer-io y motor-cpm, ya integrados en `366209b` y `3ddbddd`, y que queda registrado como desviación. `docs/ESTADO.md` dice lo mismo: QC-1 es posterior al código. No se reescribe esa historia. Tener el archivo ahora no hace que 8.4 se haya cumplido a tiempo.

8.5: desviación de la spec. Bloquea el cierre de este ciclo.

### I-14 — QC-2 no está

Estado: abierto. El mismo contrato dice que no lo declara.

8.4 no permite saltar QC-2: esperados con doble firma, recalculados por otro método. La sección 7 pide la segunda cuenta en `tests/oracle/`, sin importar `src/atlaspmo`, y la doble firma en el YAML. El contrato dice que los esperados de los casos nuevos salen del calendario y del CPM, no de un segundo cálculo en `tests/oracle/`. No hay doble firma independiente. No se da el oráculo por independiente.

## Abierto y no es conformidad con P6

No se cierra. No es un pass del criterio de conformidad de la sección 11. El contrato lo dice: no hay `p6_verified`. La sección 10.2 manda la validación manual a `docs/VALIDACIONES_PENDIENTES.md` y no detiene la ejecución por ella. Por eso no se reclasifica como resultado numérico incorrecto: esta evidencia no trae un número de P6. Tampoco autoriza a llamarlo conformidad.

| Brecha | Requisito | Qué dice el contrato | Qué queda abierto |
|---|---|---|---|
| B-08 | R-012, R-163 | implementado, [VALIDAR] con `p6_verified` | restricciones. `VALIDACIONES_PENDIENTES.md` pide confirmar `CS_MANDSTART` y `CS_MANDFIN` |
| B-09 | R-013, R-165 | implementado, [VALIDAR] | longest path. No hay contraste con P6 |
| B-21 | R-015, R-164 | implementado, [VALIDAR] | hito de inicio. `VALIDACIONES_PENDIENTES.md` pide confirmar si el que cae a las 16:00 pasa al inicio laboral siguiente |

G10 en pass solo comprueba que el archivo de test citado existe. No convierte esas filas en conformidad.

El contrato tampoco declara la UDF como marca de hito contractual: no hay columna verificada; el camino que declara es la lista de códigos. No se da por cumplido ese punto. B-04 es alcance de E2.

## No medido — no es pass

La sección 11 dice que «no medido» nunca equivale a cumplido. `docs/qa/E1/perf.md` mide una sola fila y deja el resto sin cifra. G6 en pass no cubre lo no medido. El test `tests/perf/test_scale.py` exige menos de 15 s y cronometra solo `read_xer`. El 0.64 s del detalle de G6 es la duración de esa corrida de pytest, no el tiempo de lectura.

Medición que sí está, en esta máquina, el 2026-10-21, fuera de la aserción del test. No se versionó el XER.

| Dato | Valor |
|---|---|
| CPU | Intel Core Ultra 9 185H |
| RAM | 31.4 GB |
| SO | Windows 11 Enterprise |
| Archivo | `gen_scale.py`, 30 000 actividades, `series=False` |
| Tamaño | 4 218 499 bytes |
| `read_xer` | 0.197 s |

0.197 s está bajo 15 s. Cumple esa fila y ninguna otra.

| Criterio de la sección 11 | Meta | Estado en esta etapa |
|---|---|---|
| Lectura de un XER de 30k | < 15 s | medido, 0.197 s, bajo la meta |
| DCMA + chequeos de calidad | < 10 s | no medido; no es pass. La fila es de E3 |
| Redundancia con confirmación | < 3 min | no medido; no es pass. El contrato lo dice. La fila es de E2. También dice que el algoritmo de 30k no está |
| Monte Carlo, 1 000 iteraciones, 30k | < 5 min | no medido; no es pass. La fila es de E4 |
| Conformidad CPM vs. P6 | ≥ 99,5 % en reales; 100 % en `p6_verified`; 100 % de diferencias explicadas | no medido; no hay `p6_verified`; no es pass |

No se baja de etapa el trabajo de E2, E3 o E4. No se sube tampoco: estas cuatro filas no quedan cumplidas.

## Menor

No bloquean.

### M-7 — ESTADO.md habla de un gate de E1 que ya existe

La línea de cobertura 88.0 dice «todavía sin gate de E1». El gate está en `docs/qa/E1/gate.json` con cobertura_total 87.8 y salida 1. No cambia I-11.

### M-8 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest` en este equipo.

### M-9 — G12 no compara tiempos

Pass: tests 165 frente a 137. `gate.json` trae `"benchmarks": {}`. No hay comparación de benchmark contra la etapa anterior. No es un fail de G12 y no acredita tiempos de la sección 11.

## Gate

Exit code 1. test_count 165. No es APROBADO.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-8 |
| G4 | fail | I-11. No cerrado |
| G5 | pass | invariantes a-e con perfil qa. No se releyeron los tests. El contrato atribuye 500 ejemplos al perfil `qa` del round-trip (R-016) |
| G6 | pass | un test, 0.64 s. Solo la lectura. El resto de la sección 11 no es pass |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 36 requisitos citan un archivo que existe. No es conformidad ni cierra [VALIDAR] |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | 165 frente a 137. Ver M-9 |
| G13 | fail | I-12. No cerrado |
