# Hallazgos E2 — ciclo 1

Revisión de QC-6 sobre `docs/qa/E2/gate.md`, `docs/qa/E2/gate.json` (exit_code 1, test_count 174, coverage_percent 88.9), `docs/qa/E2/perf.md`, `docs/qa/E2/QC1_contrato.md`, `docs/qa/E2/logica-red.md`, el filtro de `src/atlaspmo/analysis/logic/redundant.py`, `tests/perf/test_redundancy.py`, `tests/perf/test_scale.py`, `tests/test_e2_joint.py`, `tests/test_e2_clean.py`, `tests/test_e2_guards.py`, `tests/test_e2_chain.py`, `tests/test_phase2.py`, `tests/oracle/span.py`, las filas E2 de `docs/qa/TRAZABILIDAD.md`, el encabezado de `docs/ESTADO.md`, ADR-004, ADR-013 y ADR-014 en `docs/DECISIONES.md`, las secciones 7 (punto 3), 8.1, 8.3, 8.4, 8.5, 10.2 y 11 de `docs/MEGAPROMPT_v2.md`, y los puntos 2 y 3 de `docs/VALIDACIONES_PENDIENTES.md`. HEAD `c8281a9` (`test(qa): gate E2 ciclo 1, salida 1 (B-02)`). El filtro está en `8bcd892`, integrado por `440b23b`. El contrato está en `d5395cf`, anterior al filtro. No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó código de producto ni `docs/ESTADO.md`.

Ciclo 1 de 3. Quedan dos ciclos. No se autoriza bajar umbrales (ADR-014). No se marca la etapa bloqueada: el orquestador lo hace solo tras el tercer rechazo (ADR-013). Esta revisión no cambia ese estado.

La regla de cierre exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass.

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta.

La confirmación de 30 000 actividades no se corrió. `docs/qa/E2/perf.md` proyecta decenas de horas y dice que no cumple los 3 minutos. Esa proyección no es una medición de 30 000. Por eso no se anota como crítico de tiempo superado: no hay cifra medida por encima de la meta. Tampoco es un pass. Va en I-17, como importante.

Lo que sí está medido y queda bajo la aserción de su test, no bajo la meta de 3 minutos: el filtro de candidatos, 0.345 s. La lectura de 30 000 quedó medida en E1 (0.197 s, bajo 15 s). Ninguna de las dos es la confirmación.

## Importante

Abiertos. Bloquean el cierre.

No se cierran, y E2 queda condicional a ellos: I-3, I-11, I-12, I-13 e I-14 parcial. E0 y E1 siguen RECHAZADA-BLOQUEADA.

De este ciclo, también abiertos: I-15, I-16, I-17 e I-18.

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. E0 está RECHAZADA-BLOQUEADA. `docs/qa/E2/QC1_contrato.md` condiciona los resultados de E2 a ese hallazgo. No se releyó el script ni la carpeta. No se cierra I-3.

### I-11 — G4 de E1, sigue abierto

Estado: abierto. No es el fail de este gate y no se reescribe con las cifras de E2. En el ciclo 3 de E1 el control seguía bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 87.3 y ramas 73.6, cobertura_total 88.8. E1 está RECHAZADA-BLOQUEADA. No se cierra I-11. La lectura de este gate es I-15.

### I-12 — G13 de E1, sigue abierto y no es este gate

Estado: abierto. No se copia su cifra como resultado de E2.

`docs/qa/E1/sabotaje.md` sigue en `2ed6b43`, con kill_score 54.0. `redundant.py` cambió después, en `8bcd892`. No hay corrida nueva. `check_g13` solo lee `docs/qa/E2/sabotaje.md`. Ese archivo no está. El 54.0 no es el kill score de este gate, no se marca pass y no cierra I-12. La lectura de este gate es I-16.

### I-13 — QC-1 de E1 tardío, sigue abierto

Estado: abierto como desviación de proceso de E1. No se cierra y no se traslada al contrato de E2.

El contrato de E1 se escribió después de `366209b` y `3ddbddd`. El de E2 no: `d5395cf` es anterior a `8bcd892`, y `docs/qa/E2/QC1_contrato.md` dice que se escribió antes del código. Tener el contrato de E2 a tiempo no cumple 8.4 de E1. No se reescribe esa historia.

### I-14 — QC-2 parcial, sigue abierto

Estado: parcial. Sigue abierto como importante. No se cierra.

`tests/oracle/span.py` sigue siendo el único módulo de `tests/oracle/`. Cubre un caso de CPLI (ADR-017): 24 h de largo y 16 h de holgura. El único YAML con `verificado_por` sigue siendo `tests/fixtures/synthetic/cases/cpli.yaml`. No hay segundo método para redundancia. El vacío de QC-2 en los casos de esta etapa es I-18. No cierra lo que I-14 dejó fuera.

### I-15 — G4 de E2 incumple 8.1

Estado: abierto. El gate lo deja en fail. No se marca pass. No se autoriza bajar el umbral.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. G4 falla si eso no se cumple. ADR-014 precisa lo mismo. La línea base de la sección 10.2 no aplica a E2.

`docs/qa/E2/gate.md` y el texto de fail de `gate.json` nombran solo esto:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

Frente al ciclo 3 de E1, calendars y engine no se movieron. Logic subió de 87.3 / 73.6 a 88.6 / 75.3. Ninguna de las seis cifras llega al umbral. El alza no cierra el control.

El modelo no está en el texto de fail. El detalle dice model líneas 100.0 y ramas 100.0. Eso no cierra el hallazgo.

El mismo detalle añade resto líneas 88.9 % y ramas 74.7 %. Las líneas del resto no son el fail: 88.9 está sobre el 80 % de 8.1. Las ramas 74.7 del resto están en el detalle y no están en el texto de fail. ADR-014 no fija umbral de ramas para el resto. No se abre un hallazgo por esa cifra y no se usa para compensar.

La cobertura_total que cita el control es 88.9. La tabla pegada en el detalle cierra con TOTAL 85 % (4055, 450, 1576, 333). Ni 88.9 ni 85 dejan el control en pass. 85 no es el número de G4.

### I-16 — G13 de E2 no está medido

Estado: abierto. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa.

`docs/qa/E2/sabotaje.md` no existe. El detalle de G13 es exactamente «no medido: falta el informe de qa-sabotaje». 8.3 y ADR-014 exigen alcance completo y, en los módulos de la etapa, al menos 85 % en `engine`, `calendars` y `analysis/logic`, o 70 % en el resto. Sin informe no hay cifra que comparar. No medido no es pass.

No se reutiliza el informe de E1. `redundant.py` cambió en `8bcd892`, después de `2ed6b43`. El 54.0, el 60.2, el 45.5 y el 52.0 de `docs/qa/E1/sabotaje.md` no son esta corrida. Citarlos como G13 de E2 sería afirmar una mutación que no se hizo.

### I-17 — La confirmación de 30 000 no cumple por proyección

Estado: abierto. No es un crítico de tiempo. No es un pass.

La sección 11 pide redundancia con confirmación bajo 3 minutos. El criterio propio de E2 en 10.2 es el mismo: redundancia de 30 000 bajo 3 minutos. 8.5 lista como crítico un criterio de la sección 11 incumplido. Esta evidencia no trae esa corrida. La proyección no es una medición de 30 000. Sin cifra medida por encima de la meta, no hay crítico. El criterio igual no está cumplido. «No medido» nunca equivale a cumplido (sección 11). Queda importante.

`docs/qa/E2/perf.md`, en este equipo, el 2026-10-21, red de `gen_scale` con `series=False`, sin XER real:

| Medición | Cifra | Qué es |
|---|---|---|
| Filtro de candidatos, 30 000 actividades | 0.345 s | 24 998 candidatos sobre 69 996 vínculos. Un grafo y un recorrido por origen. No es la confirmación. |
| `classify_links`, 100 actividades | 3.25 s | 81 candidatos y 121 corridas del CPM. No es 30 000. |
| `classify_links`, 400 actividades | 58.1 s | 331 candidatos. El filtro de esa red tardó 0.003 s. Está bajo 3 minutos y no es 30 000. |
| Confirmación de 30 000 | no corrida | La proyección del informe queda en decenas de horas. |

El informe arma la proyección así: en 100 actividades el CPM salió a unos 0.027 s; a 30 000, la cifra vieja del motor era del orden de 8 s; con cerca de 1.5 CPM por candidato, y del orden de 25 000 candidatos, el resultado no cabe en 3 minutos. Esa cuenta no se ejecutó. No se usa aquí como tiempo medido de 30 000.

`tests/perf/test_redundancy.py` cronometra solo `_candidate_ids` y exige menos de 15 s. El propio test dice que la confirmación no se afirma ahí, porque una corrida completa no termina dentro del gate. G6 en pass no cubre este criterio: el detalle es «2 passed in 1.93s». En `tests/perf` solo están ese archivo y `tests/perf/test_scale.py`, que exige la lectura bajo 15 s. 1.93 s es la duración de esa corrida de pytest, no el tiempo de la confirmación. `docs/qa/E2/logica-red.md` separa lo mismo: el test de filtro pasó en 1.42 s, incluido escribir el archivo, y la confirmación de 30 000 no se corrió.

R-020 y R-302 citan `tests/perf/test_redundancy.py`. G10 solo comprueba que el archivo existe. No dan por cumplidos los 3 minutos.

### I-18 — QC-2 de redundancia no está

Estado: abierto. Desviación de la sección 8.4. No se inventa un oráculo de P6 para cerrarlo.

QC-2 pide esperados recalculados por otro método, en `tests/oracle/` o a mano, sin importar `src/atlaspmo`, y doble firma en el YAML (`calculado_por`, `verificado_por`, `metodo`). El punto 3 de la sección 7 dice lo mismo. 8.4 no permite saltar el control.

`docs/qa/E2/QC1_contrato.md` lo deja escrito: QC-2 de los casos nuevos de redundancia no está en el contrato. Los esperados de los tests ya verdes salen del CPM del propio caso, no de un segundo método en `tests/oracle/`.

Lo que se contrastó:

- `tests/test_e2_joint.py` llama a `classify_links` y a `clean_document`. Afirma un solo `redundante_confirmado` y el mismo `project_finish`. El esperado sale del CPM del caso.
- `tests/test_e2_clean.py` parchea `classify_links` para forzar un vínculo confirmado y afirma que, si el CPM se mueve, `removed == 0` y los bytes no cambian. Compara el motor consigo mismo.
- `tests/test_e2_chain.py`, agregado en `8bcd892`, afirma que una cadena FS de cuatro no queda confirmada. También sale de `classify_links`.
- `tests/oracle/` sigue teniendo solo `span.py`. No calcula redundancia. No hay otro YAML de redundancia con `verificado_por`.

Eso no cumple QC-2. No se da por cumplido el criterio de E2 que pide el XER limpio con delta cero contra un esperado independiente. Los tests de bytes y de delta cero siguen en verde (G3). Verde no es el segundo método.

## B-03 y B-04 no se relajaron

No es un hallazgo de regresión. Queda registrado para que el ciclo siguiente no lo reabra como si el filtro hubiera aflojado las protecciones.

`tests/test_e2_joint.py`, `tests/test_e2_clean.py` y `tests/test_e2_guards.py` no tienen diff desde `3ecec3c` hasta este HEAD. `tests/test_phase2.py` tampoco. El commit del filtro, `8bcd892`, toca `redundant.py`, `tests/perf/test_redundancy.py`, `tests/test_e2_chain.py` y las notas de `docs/qa/E2/`. No toca esos tres tests.

El contrato dice que la confirmación conjunta (`_confirm`, `_join`, `_unchanged`, `_events_stay_covered`) no se reemplaza. El cambio de B-02 es el filtro. En `_candidate_ids`, si `_event_topo` no ordena el grafo completo, devuelve el conjunto vacío. `_event_topo` devuelve vacío cuando el orden no cubre todos los nodos. Si el grafo tiene ciclo, no hay candidatos. El cálculo es sobre un DAG. Eso es más conservador que rearmar el orden sin el arco. No se encontró un test que fije ese vacío; no se trata como relajación de B-03 ni de B-04.

`tests/test_e2_guards.py` afirma dos cosas: un hito no queda protegido salvo que su código esté en la lista, y un vínculo con otro `pred_proj_id` queda protegido. SS+FF sigue afirmado en `tests/test_phase2.py::test_ss_ff_pair_is_protected`, sin cambios. No se vio un test que llame a `_events_stay_covered`. El contrato agrupa extremos abiertos y SS+FF en `tests/test_e2_guards.py`. Esa cita está corrida. No se usa para decir que este ciclo relajó B-04. Va en M-15.

La UDF como marca de hito contractual no se da por cumplida. El contrato lo dice: no hay columna verificada; el camino es la lista de códigos. B-04, en la spec, también nombra la UDF. Sin columna verificada no se declara ese camino.

## Abierto y no es conformidad con P6

No se cierra. No es un pass del criterio de conformidad de la sección 11. El contrato de E2 dice que no hay contraste con P6. El listado de `tests/fixtures/p6_verified/` no muestra un export. La sección 10.2 manda la validación manual a `docs/VALIDACIONES_PENDIENTES.md` y no detiene la ejecución por ella. Por eso no se reclasifica como resultado numérico incorrecto: esta evidencia no trae un número de P6. Tampoco autoriza a llamarlo conformidad.

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

Pass por `tests/perf`: 2 passed in 1.93 s. Un test exige la lectura bajo 15 s. El otro exige el filtro de candidatos bajo 15 s. Ninguno exige los 3 minutos de la sección 11. No es un fail de G6, según lo que el control ejecuta hoy, y no acredita I-17.

### M-13 — G12 no compara tiempos

Pass: tests 174 frente a 173. `gate.json` trae `"benchmarks": {}`. No hay comparación de benchmark contra la etapa anterior. No es un fail de G12 y no acredita tiempos de la sección 11. La cobertura_total 88.9 frente a 88.8 de E1 no se usa para declarar G4 en pass. La subida es de 0.1 puntos, no una baja de más de 0.5.

### M-14 — `gate.md` corta el detalle

La línea de G4 en `docs/qa/E2/gate.md` se corta en «engine lineas 89.». La de G6 se queda en la barra de progreso. Las cifras completas, incluido el modelo en 100/100, el resto en 88.9 / 74.7, logic en 88.6 / 75.3 y el «2 passed in 1.93s», están en `gate.json`. No cambia I-15 ni el fail.

### M-15 — el contrato cita de más en `tests/test_e2_guards.py`

El archivo afirma el hito contractual y el vínculo externo. SS+FF está en `tests/test_phase2.py` y no se tocó en este ciclo. No se encontró un test de `_events_stay_covered`. No es una relajación. No sube a importante: el bloqueo de este ciclo ya está en I-15, I-16, I-17 e I-18, y en los heredados.

## Gate

Exit code 1. test_count 174. Cobertura citada por el control: 88.9. Rechazo 1 de 3. Quedan dos ciclos. No se autoriza bajar umbrales. No se marca la etapa bloqueada. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-11 |
| G4 | fail | I-15. No es pass. Calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a-e con perfil qa. No se releyeron los ejemplos. El contrato atribuye b, c y d a `tests/property/test_logic.py` |
| G6 | pass | 2 passed in 1.93 s. Lectura y filtro. La confirmación de 30 000 no es pass. Ver M-12 e I-17 |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 12 requisitos citan un archivo que existe. No es la meta de 3 minutos, no es QC-2 y no cierra [VALIDAR] |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | 174 frente a 173. Ver M-13 |
| G13 | fail | I-16. No medido. No es pass. No se usa el 54.0 de E1 |
