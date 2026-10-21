# Hallazgos E2 — ciclo 3

Revisión de QC-6 sobre `docs/qa/E2/gate.md`, `docs/qa/E2/gate.json` (exit_code 1, test_count 175, coverage_percent 88.9), `docs/qa/E2/ciclo3.md` y `docs/qa/E2/perf.md`. HEAD `21cfe63` (`test(qa): gate E2 ciclo 3, salida 1 (B-02)`). El atajo está en `fbfff7b` y no se integró. El veredicto del ciclo 2 queda en `339cafd`, sobre el gate `d494694`. El oráculo de un camino sigue en `2182e71` (ADR-018). No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó código de producto ni `docs/ESTADO.md`.

Este es el rechazo 3 de 3. No se autoriza un cuarto ciclo ni bajar umbrales (ADR-014). ADR-013 no abre otro ciclo de esta etapa. El orquestador cambia el estado después. Esta revisión no marca la etapa bloqueada.

La regla de cierre exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass.

## Contraste

`docs/qa/E2/gate.md` sale 1. Pass: G1, G2, G3 y G5 a G12. Fail: G4 y G13. G4, igual que el ciclo 2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 88.9. En `gate.json` esas seis cifras no se movieron, ni el modelo en 100.0 / 100.0, ni el resto en 88.9 / 74.7, ni el TOTAL 85 % (4055, 450, 1576, 333). Cambió el reloj de la suite de cobertura: 18.18 s frente a 24.38 s. G6 pasó de 1.83 s a 1.84 s. Esos relojes no son la confirmación de 30 000.

`docs/qa/E2/ciclo3.md` no cambia código. Fuera del repositorio se probó aceptar un vínculo por la holgura del CPM ya calculado, sin otro CPM. En una red de 100 actividades de `gen_scale`, 41 vínculos que esa cuenta daba por holgados no quedaron `redundante_confirmado` al volver a correr el motor. Integrarlo habría confirmado vínculos que mueven fechas u holgura, o habría caído al mismo bisect. No se integró. No acelera la confirmación de 30 000. No toca G4 ni G13. No baja umbrales. `21cfe63` no toca `src/`.

`docs/qa/E2/perf.md` no cambió. En este equipo, el 2026-10-21, red de `gen_scale` con `series=False`, sin XER real:

| Medición | Cifra | Qué es |
|---|---|---|
| Filtro de candidatos, 30 000 actividades | 0.345 s | 24 998 candidatos. No es la confirmación. |
| `classify_links`, 100 actividades | 3.25 s | 81 candidatos y 121 corridas del CPM. No es 30 000. |
| `classify_links`, 400 actividades | 58.1 s | 331 candidatos. Bajo 3 minutos y no es 30 000. |
| Confirmación de 30 000 | no corrida | La proyección queda en decenas de horas. No es una medición. |

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta.

La confirmación de 30 000 no se corrió. La proyección de `perf.md` no cumple los 3 minutos y no es una cifra de 30 000. Sin esa cifra medida no hay crítico de tiempo. El criterio igual no está cumplido. «No medido» no equivale a cumplido. Queda en I-17.

Lo medido y bajo la aserción de su test, no bajo la meta de 3 minutos: el filtro, 0.345 s. La lectura de 30 000 quedó medida en E1 (0.197 s, bajo 15 s). Ninguna de las dos es la confirmación.

## Importante

Abiertos. Bloquean el cierre.

No se cierran, y E2 queda condicional a ellos: I-3, I-11, I-12, I-13 e I-14 parcial. E0 y E1 siguen bloqueadas, cada una tras su tercer rechazo, sin cuarto ciclo.

De este ciclo, también abiertos: I-15, I-16, I-17 e I-18. I-18 queda parcial y no se cierra.

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. No se releyó el script ni la carpeta. No se cierra I-3.

### I-11 — G4 de E1, sigue abierto

No es el fail de este gate. No se reescribe con las cifras de E2. E1 está sin cuarto ciclo. No se cierra I-11. La lectura de este gate es I-15.

### I-12 — G13 de E1, sigue abierto y no es este gate

No se copia su kill score como resultado de E2. No hay corrida nueva de ese informe. No se cierra I-12. La lectura de este gate es I-16.

### I-13 — QC-1 de E1 tardío, sigue abierto

Desviación de proceso de E1. El contrato de E2, anterior al código, no cumple 8.4 de E1. No se reescribe esa historia. El oráculo de `2182e71` no la cierra. No se cierra I-13.

### I-14 — QC-2 parcial, sigue abierto

`tests/oracle/span.py` sigue en un solo caso de CPLI (ADR-017). El ciclo 3 no tocó ese oráculo ni el YAML. No cubre lo que I-14 dejó fuera. No se cierra I-14. El caso de redundancia va en I-18.

### I-15 — G4 de E2 incumple 8.1

Estado: abierto. El gate lo deja en fail. No se marca pass. No se baja el umbral. Este ciclo no movió las cifras.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. ADR-014 precisa lo mismo. La línea base de la sección 10.2 no aplica a E2.

Siguen bajo el umbral, igual que el ciclo 2:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

El atajo de `ciclo3.md` no se integró y no es un test de cobertura. El modelo en 100.0 / 100.0 no está en el texto de fail y no cierra el hallazgo. El resto, líneas 88.9, está sobre el 80 % y no compensa. Las ramas 74.7 del resto no están en el texto de fail. cobertura_total 88.9 y el TOTAL 85 % de la tabla no dejan el control en pass. «175 passed, 2 deselected in 18.18s» es la duración de esa suite, no un cumplimiento de 8.1.

### I-16 — G13 de E2 no está medido

Estado: abierto. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa.

`docs/qa/E2/sabotaje.md` no existe. El detalle de G13 es «no medido: falta el informe de qa-sabotaje». `ciclo3.md` dice que G13 no se toca. Sin informe no hay cifra que comparar con 8.3 ni con ADR-014. No medido no es pass. No se usa el kill score de E1 como score de este gate.

### I-17 — La confirmación de 30 000 no cumple por proyección

Estado: abierto. No es un crítico de tiempo. No es un pass. Este ciclo no la corrió.

La sección 11 y el criterio de E2 en 10.2 piden la confirmación de redundancia de 30 000 bajo 3 minutos. Esta evidencia no trae esa corrida. La proyección no es una medición ni una cifra de 30 000 por encima de la meta. Sin esa cifra no hay crítico. El criterio no está cumplido.

`ciclo3.md` no entrega esa corrida. El atajo, en 100 actividades, ya dejó 41 vínculos fuera de `redundante_confirmado`. No se integró. No hay, en esta corrida, una corrección que baje la confirmación de 30 000 bajo 3 minutos sin acelerar el CPM o sin relajar el delta cero.

G6 en pass no cubre el criterio. El detalle es «2 passed in 1.84s»: lectura y filtro. `tests/perf/test_redundancy.py` exige el filtro bajo 15 s y no afirma la confirmación. R-020 y R-302, y el pass de G10, solo exigen que el archivo exista.

### I-18 — QC-2 de redundancia queda parcial

Estado: parcial. Sigue abierto como importante. No se cierra.

ADR-018 y `tests/oracle/pathlen.py` siguen en un solo camino: 8 h + 8 h frente a un lag. No importa `src/atlaspmo`. No carga un cronograma, no llama al CPM y no firma un YAML de redundancia. El ciclo 3 no agregó otro caso. El atajo no integrado no es un segundo método.

QC-2 pide esperados por otro método, en `tests/oracle/` o a mano, y doble firma en el YAML. El verde de G3 no es ese método. El único YAML con `verificado_por` sigue siendo el de CPLI.

## B-03 y B-04 no se relajaron

No es un hallazgo de regresión. `21cfe63` y `fbfff7b` no tocan `redundant.py` ni los tests de confirmación, limpieza y protecciones. El atajo quedó fuera del repositorio.

## Abierto y no es conformidad con P6

No se cierra. No hay contraste con P6 en la evidencia de este ciclo. La sección 10.2 manda esa validación a `docs/VALIDACIONES_PENDIENTES.md` y no detiene la ejecución por ella. No es un resultado numérico incorrecto: esta evidencia no trae un número de P6. Tampoco es conformidad.

Siguen en [VALIDAR]: B-08 (`CS_MANDSTART` y `CS_MANDFIN`), B-09 (longest path contra P6) y B-21 (hito de inicio a las 16:00). G10 en pass no convierte esas filas en conformidad.

## Menor

No bloquean. No autorizan el cierre.

### M-11 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest`.

### M-12 — G6 no es la confirmación de 30 000

Pass: 2 passed in 1.84 s. En el ciclo 2 eran 1.83 s. Lectura bajo 15 s y filtro bajo 15 s. No exige los 3 minutos. No es un fail de G6 y no acredita I-17.

### M-13 — G12 no compara tiempos

Pass: tests 175 frente a 173, igual que el ciclo 2. `"benchmarks": {}`. cobertura_total 88.9 no declara G4 en pass.

### M-14 — `gate.md` corta el detalle

La línea de G4 se corta en «engine lineas 89.». La de G6 se queda en la barra. Las cifras completas están en `gate.json`, incluido el reloj de 18.18 s. No cambia I-15 ni el fail.

## Gate

Exit code 1. test_count 175. Cobertura citada por el control: 88.9. Rechazo 3 de 3. No se autoriza un cuarto ciclo. No se bajan umbrales. No se marca la etapa bloqueada. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-11 |
| G4 | fail | I-15. Igual que el ciclo 2: calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a-e con perfil qa |
| G6 | pass | 2 passed in 1.84 s. Lectura y filtro. No es la confirmación de 30 000. Ver M-12 e I-17 |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 12 requisitos citan un archivo que existe. No es la meta de 3 minutos, no es QC-2 y no cierra [VALIDAR] |
| G11 | pass | cambios protegidos citan un ADR. El oráculo sigue en `2182e71`, ADR-018 |
| G12 | pass | 175 frente a 173. Ver M-13 |
| G13 | fail | I-16. No medido. No se copia el kill score de E1 |
