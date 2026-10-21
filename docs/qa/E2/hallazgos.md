# Hallazgos E2 — ciclo 2

Revisión de QC-6 sobre `docs/qa/E2/gate.md`, `docs/qa/E2/gate.json` (exit_code 1, test_count 175, coverage_percent 88.9), `docs/qa/E2/perf.md`, `docs/qa/E2/QC1_contrato.md`, `docs/qa/E2/logica-red.md`, `tests/oracle/pathlen.py`, `tests/test_e2_oracle.py`, el diff `e41a452..HEAD`, las filas E2 de `docs/qa/TRAZABILIDAD.md` no recontadas en este ciclo, el encabezado de `docs/ESTADO.md`, ADR-004, ADR-013, ADR-014 y ADR-018 en `docs/DECISIONES.md`, las secciones 7 (punto 3), 8.1, 8.3, 8.4, 8.5, 10.2 y 11 de `docs/MEGAPROMPT_v2.md`, y los puntos 2 y 3 de `docs/VALIDACIONES_PENDIENTES.md`. HEAD `d494694` (`test(qa): gate E2 ciclo 2, salida 1 (B-02)`). El oráculo está en `2182e71`. El veredicto del ciclo 1 queda en `e41a452`, sobre el gate `c8281a9`. El filtro sigue en `8bcd892`, integrado por `440b23b`. El contrato sigue en `d5395cf`, anterior al filtro y al oráculo. No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó código de producto ni `docs/ESTADO.md`.

Ciclo 2 de 3. Queda un ciclo. No se autoriza bajar umbrales (ADR-014). No se marca la etapa bloqueada: el orquestador lo hace solo tras el tercer rechazo (ADR-013). Esta revisión no cambia ese estado.

La regla de cierre exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass.

## Qué cambió en este ciclo

Desde `e41a452` el árbol toca `docs/DECISIONES.md`, `docs/ESTADO.md`, `docs/qa/E2/gate.json`, `docs/qa/E2/gate.md`, `tests/oracle/pathlen.py` y `tests/test_e2_oracle.py`. No toca `src/`, `docs/qa/E2/perf.md`, `docs/qa/E2/QC1_contrato.md`, `docs/qa/E2/logica-red.md` ni los tests de confirmación, limpieza y protecciones.

El gate pasó de test_count 174 a 175. cobertura_total sigue en 88.9. Las seis cifras de G4 son las mismas. G13 sigue en «no medido: falta el informe de qa-sabotaje». G6 pasó de «2 passed in 1.93s» a «2 passed in 1.83s». G12 dice «tests 175 frente a 173». En el detalle de G4, la línea de la suite pasó de «174 passed, 2 deselected in 18.47s» a «175 passed, 2 deselected in 24.38s». Esos 24.38 s son la suite del control, no la confirmación de 30 000.

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta.

La confirmación de 30 000 actividades no se corrió. `docs/qa/E2/perf.md` no cambió: proyecta decenas de horas y dice que no cumple los 3 minutos. Esa proyección no es una medición de 30 000. Por eso no se anota como crítico de tiempo superado: no hay cifra medida de 30 000 por encima de la meta. Tampoco es un pass. Va en I-17, como importante.

Lo que sí está medido y queda bajo la aserción de su test, no bajo la meta de 3 minutos: el filtro de candidatos, 0.345 s. La lectura de 30 000 quedó medida en E1 (0.197 s, bajo 15 s). Ninguna de las dos es la confirmación.

## Importante

Abiertos. Bloquean el cierre.

No se cierran, y E2 queda condicional a ellos: I-3, I-11, I-12, I-13 e I-14 parcial. E0 y E1 siguen sin cuarto ciclo, tras su tercer rechazo.

De este ciclo, también abiertos: I-15, I-16, I-17 e I-18. I-18 queda parcial y no se cierra.

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. E0 está tras su tercer rechazo, sin cuarto ciclo. `docs/qa/E2/QC1_contrato.md` condiciona los resultados de E2 a ese hallazgo. No se releyó el script ni la carpeta. No se cierra I-3.

### I-11 — G4 de E1, sigue abierto

Estado: abierto. No es el fail de este gate y no se reescribe con las cifras de E2. En el ciclo 3 de E1 el control seguía bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 87.3 y ramas 73.6, cobertura_total 88.8. E1 está sin cuarto ciclo. No se cierra I-11. La lectura de este gate es I-15.

### I-12 — G13 de E1, sigue abierto y no es este gate

Estado: abierto. No se copia su cifra como resultado de E2.

`docs/qa/E1/sabotaje.md` sigue en `2ed6b43`, con kill_score 54.0. `redundant.py` cambió después, en `8bcd892`. No hay corrida nueva. `check_g13` solo lee `docs/qa/E2/sabotaje.md`. Ese archivo no está. El 54.0 no es el kill score de este gate, no se marca pass y no cierra I-12. La lectura de este gate es I-16.

### I-13 — QC-1 de E1 tardío, sigue abierto

Estado: abierto como desviación de proceso de E1. No se cierra y no se traslada al contrato de E2.

El contrato de E1 se escribió después de `366209b` y `3ddbddd`. El de E2 no: `d5395cf` es anterior a `8bcd892`, y `docs/qa/E2/QC1_contrato.md` dice que se escribió antes del código. Tener el contrato de E2 a tiempo no cumple 8.4 de E1. No se reescribe esa historia. El oráculo de `2182e71` es posterior a ese contrato y no reabre ni cierra I-13.

### I-14 — QC-2 parcial, sigue abierto

Estado: parcial. Sigue abierto como importante. No se cierra.

`tests/oracle/span.py` sigue cubriendo un solo caso de CPLI (ADR-017): 24 h de largo y 16 h de holgura. El único YAML con `verificado_por` sigue siendo `tests/fixtures/synthetic/cases/cpli.yaml`. El ciclo 2 agregó `tests/oracle/pathlen.py`. Eso no es un segundo método para lo que I-14 dejó fuera: restricciones obligatorias, longest path, hito de inicio ni BEI. El caso de redundancia va en I-18 y tampoco cierra este hallazgo.

### I-15 — G4 de E2 incumple 8.1

Estado: abierto. El gate lo deja en fail. No se marca pass. No se autoriza bajar el umbral. Este ciclo no movió las cifras.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. G4 falla si eso no se cumple. ADR-014 precisa lo mismo. La línea base de la sección 10.2 no aplica a E2.

`docs/qa/E2/gate.md` y el texto de fail de `gate.json` nombran solo esto, igual que en el ciclo 1:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

Frente al ciclo 1 de E2 no hay alza. Frente al ciclo 3 de E1, calendars y engine no se movieron y logic sigue en 88.6 / 75.3, por encima de 87.3 / 73.6 y debajo del umbral. El oráculo no está en esos paquetes. Sumar un test no cierra el control.

El modelo no está en el texto de fail. El detalle dice model líneas 100.0 y ramas 100.0. Eso no cierra el hallazgo.

El mismo detalle añade resto líneas 88.9 % y ramas 74.7 %. Las líneas del resto no son el fail: 88.9 está sobre el 80 % de 8.1. Las ramas 74.7 del resto están en el detalle y no están en el texto de fail. ADR-014 no fija umbral de ramas para el resto. No se abre un hallazgo por esa cifra y no se usa para compensar.

La cobertura_total que cita el control es 88.9, la misma del ciclo 1. La tabla pegada en el detalle cierra con TOTAL 85 % (4055, 450, 1576, 333), también igual. Ni 88.9 ni 85 dejan el control en pass. 85 no es el número de G4. «175 passed, 2 deselected in 24.38s» es la duración de esa suite, no un cumplimiento de 8.1.

### I-16 — G13 de E2 no está medido

Estado: abierto. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa. El ciclo 2 no agregó el informe.

`docs/qa/E2/sabotaje.md` no existe. El detalle de G13 es exactamente «no medido: falta el informe de qa-sabotaje». 8.3 y ADR-014 exigen alcance completo y, en los módulos de la etapa, al menos 85 % en `engine`, `calendars` y `analysis/logic`, o 70 % en el resto. Sin informe no hay cifra que comparar. No medido no es pass.

No se reutiliza el informe de E1. `redundant.py` cambió en `8bcd892`, después de `2ed6b43`, y este ciclo no lo volvió a medir. El 54.0, el 60.2, el 45.5 y el 52.0 de `docs/qa/E1/sabotaje.md` no son esta corrida. Citar el 54.0 como score de E2 sería afirmar una mutación que no se hizo.

### I-17 — La confirmación de 30 000 no cumple por proyección

Estado: abierto. No es un crítico de tiempo. No es un pass. Este ciclo no la corrió.

La sección 11 pide redundancia con confirmación bajo 3 minutos. El criterio propio de E2 en 10.2 es el mismo: redundancia de 30 000 bajo 3 minutos. 8.5 lista como crítico un criterio de la sección 11 incumplido. Esta evidencia no trae esa corrida. La proyección no es una medición de 30 000 ni una cifra de 30 000 por encima de la meta. Sin esa cifra medida, no hay crítico. El criterio igual no está cumplido. «No medido» nunca equivale a cumplido (sección 11). Queda importante. ADR-018 repite que la confirmación de 30 000 actividades no cabe en 3 minutos con un CPM por candidato. Esa frase no es una corrida nueva.

`docs/qa/E2/perf.md`, sin cambios en este ciclo, en este equipo, el 2026-10-21, red de `gen_scale` con `series=False`, sin XER real:

| Medición | Cifra | Qué es |
|---|---|---|
| Filtro de candidatos, 30 000 actividades | 0.345 s | 24 998 candidatos sobre 69 996 vínculos. Un grafo y un recorrido por origen. No es la confirmación. |
| `classify_links`, 100 actividades | 3.25 s | 81 candidatos y 121 corridas del CPM. No es 30 000. |
| `classify_links`, 400 actividades | 58.1 s | 331 candidatos. El filtro de esa red tardó 0.003 s. Está bajo 3 minutos y no es 30 000. |
| Confirmación de 30 000 | no corrida | La proyección del informe queda en decenas de horas. |

El informe arma la proyección así: en 100 actividades el CPM salió a unos 0.027 s; a 30 000, la cifra vieja del motor era del orden de 8 s; con cerca de 1.5 CPM por candidato, y del orden de 25 000 candidatos, el resultado no cabe en 3 minutos. Esa cuenta no se ejecutó. No se usa aquí como tiempo medido de 30 000.

`tests/perf/test_redundancy.py` no está en el diff de este ciclo. Cronometra solo `_candidate_ids` y exige menos de 15 s. El propio test dice que la confirmación no se afirma ahí. G6 en pass no cubre este criterio: el detalle es «2 passed in 1.83s». En `tests/perf` el ciclo 1 ya dejó ese archivo y `tests/perf/test_scale.py`, que exige la lectura bajo 15 s. 1.83 s es la duración de esa corrida de pytest, no el tiempo de la confirmación. `docs/qa/E2/logica-red.md` no se actualizó: el test de filtro pasó en 1.42 s, incluido escribir el archivo, y la confirmación de 30 000 no se corrió.

R-020 y R-302 citan `tests/perf/test_redundancy.py`. G10 solo comprueba que el archivo existe. No dan por cumplidos los 3 minutos.

### I-18 — QC-2 de redundancia queda parcial

Estado: parcial. Sigue abierto como importante. No se cierra.

El ciclo 2, en `2182e71` y ADR-018, agregó un solo caso. `tests/oracle/pathlen.py` define `alternate_is_long_enough`: suma las duraciones y devuelve si el total es mayor o igual que el lag. No importa `src/atlaspmo`. `tests/test_e2_oracle.py` solo importa ese módulo y afirma tres resultados de (8, 8): el lag 0 queda cubierto, el lag 16 queda cubierto y el lag 17 no. ADR-018 nombra el caso como el camino A–B–C de 8 h + 8 h frente a un vínculo directo con lag 0. El ADR dice que no confirma el CPM ni los demás vínculos, y que QC-2 de E2 sigue incompleto fuera de ese caso.

Eso no cierra el control.

QC-2 pide esperados recalculados por otro método, en `tests/oracle/` o a mano, sin importar `src/atlaspmo`, y doble firma en el YAML (`calculado_por`, `verificado_por`, `metodo`). El punto 3 de la sección 7 dice lo mismo. 8.4 no permite saltar el control.

Lo que este caso no hace:

- No carga un cronograma, no llama al CPM y no clasifica un vínculo.
- No firma un YAML de redundancia. El único YAML con `verificado_por` sigue siendo `tests/fixtures/synthetic/cases/cpli.yaml`.
- No cubre el resto de la etapa: confirmación conjunta, delta cero, cadena que no se confirma, hito, vínculo externo ni SS+FF.
- No mueve G4, ni G13, ni la confirmación de 30 000.

`docs/qa/E2/QC1_contrato.md` no se actualizó. Sigue en `d5395cf` y sigue diciendo que QC-2 de los casos nuevos de redundancia no está en el contrato, y que los esperados de los tests ya verdes salen del CPM del propio caso, no de un segundo método en `tests/oracle/`.

La lectura del ciclo 1 sobre esos tests sigue vigente. `tests/test_e2_joint.py`, `tests/test_e2_clean.py`, `tests/test_e2_guards.py` y `tests/test_e2_chain.py` no están en el diff `e41a452..HEAD`. Su esperado sale del propio motor. El verde de G3 no es el segundo método. No se da por cumplido el criterio de E2 que pide el XER limpio con delta cero contra un esperado independiente.

## B-03 y B-04 no se relajaron

No es un hallazgo de regresión. El ciclo 2 no los toca.

`redundant.py`, `tests/test_e2_joint.py`, `tests/test_e2_clean.py` y `tests/test_e2_guards.py` no están en el diff desde `e41a452`. `2182e71` solo agrega el ADR, el oráculo y su test. La lectura del ciclo 1 sigue: si el grafo tiene ciclo, `_candidate_ids` no entrega candidatos. Eso es más conservador. No se encontró, en este diff, un cambio que afloje la confirmación conjunta ni las protecciones.

La UDF como marca de hito contractual no se da por cumplida. El contrato no cambió: no hay columna verificada; el camino es la lista de códigos. B-04, en la spec, también nombra la UDF. Sin columna verificada no se declara ese camino.

## Abierto y no es conformidad con P6

No se cierra. No es un pass del criterio de conformidad de la sección 11. El contrato de E2 no cambió y dice que no hay contraste con P6. El diff del ciclo no agrega un export bajo `tests/fixtures/p6_verified/`. La sección 10.2 manda la validación manual a `docs/VALIDACIONES_PENDIENTES.md` y no detiene la ejecución por ella. Por eso no se reclasifica como resultado numérico incorrecto: esta evidencia no trae un número de P6. Tampoco autoriza a llamarlo conformidad.

Siguen en [VALIDAR], como en el contrato de E1. No son alcance que este ciclo haya cerrado:

| Brecha | Qué pide la validación | Dónde sigue abierto |
|---|---|---|
| B-08 | Semántica de `CS_MANDSTART` y `CS_MANDFIN` | `docs/qa/E1/QC1_contrato.md`; punto 2 de `docs/VALIDACIONES_PENDIENTES.md` |
| B-09 | Longest path contra P6 | `docs/qa/E1/QC1_contrato.md` |
| B-21 | Hito de inicio que cae a las 16:00 | `docs/qa/E1/QC1_contrato.md`; punto 3 de `docs/VALIDACIONES_PENDIENTES.md` |

G10 en pass no convierte esas filas en conformidad.

## Menor

No bloquean. No autorizan el cierre.

### M-11 — G3 no corrió `uv run pytest`

El detalle de `gate.json` dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. `docs/qa/E2/gate.md` resume el pass como «python -m pytest exit 0». El pass no afirma el comando `uv run pytest` en este equipo.

### M-12 — G6 no es la confirmación de 30 000

Pass por `tests/perf`: 2 passed in 1.83 s. En el ciclo 1 eran 1.93 s. Un test exige la lectura bajo 15 s. El otro exige el filtro de candidatos bajo 15 s. Ninguno exige los 3 minutos de la sección 11. No es un fail de G6, según lo que el control ejecuta hoy, y no acredita I-17.

### M-13 — G12 no compara tiempos

Pass: tests 175 frente a 173. En el ciclo 1 eran 174 frente a 173. El test nuevo es el del oráculo. `gate.json` trae `"benchmarks": {}`. No hay comparación de benchmark contra la etapa anterior. No es un fail de G12 y no acredita tiempos de la sección 11. La cobertura_total sigue en 88.9, 0.1 puntos sobre 88.8 de E1, igual que en el ciclo 1. No se usa para declarar G4 en pass. No es una baja de más de 0.5.

### M-14 — `gate.md` corta el detalle

La línea de G4 en `docs/qa/E2/gate.md` se corta en «engine lineas 89.». La de G6 se queda en la barra de progreso. Las cifras completas, incluido el modelo en 100/100, el resto en 88.9 / 74.7, logic en 88.6 / 75.3 y el «2 passed in 1.83s», están en `gate.json`. No cambia I-15 ni el fail.

### M-15 — el contrato cita de más en `tests/test_e2_guards.py`

Sin cambios desde el ciclo 1. El archivo afirma el hito contractual y el vínculo externo. SS+FF está en `tests/test_phase2.py` y no se tocó en este ciclo. No se encontró, en el diff, un test de `_events_stay_covered`. No es una relajación. No sube a importante: el bloqueo de este ciclo ya está en I-15, I-16, I-17 e I-18, y en los heredados.

## Gate

Exit code 1. test_count 175. Cobertura citada por el control: 88.9. Rechazo 2 de 3. Queda un ciclo. No se autoriza bajar umbrales. No se marca la etapa bloqueada. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-11 |
| G4 | fail | I-15. No es pass. Igual que el ciclo 1: calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a-e con perfil qa. Este ciclo no tocó `tests/property/` |
| G6 | pass | 2 passed in 1.83 s. Lectura y filtro. La confirmación de 30 000 no es pass. Ver M-12 e I-17 |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 12 requisitos citan un archivo que existe. No es la meta de 3 minutos, no es QC-2 y no cierra [VALIDAR] |
| G11 | pass | cambios protegidos citan un ADR. El oráculo entra en `2182e71`, que cita ADR-018 |
| G12 | pass | 175 frente a 173. Ver M-13 |
| G13 | fail | I-16. No medido. No es pass. No se usa el 54.0 de E1 |
