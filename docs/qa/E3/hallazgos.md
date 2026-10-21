# Hallazgos E3 — ciclo 1

Revisión de QC-6 sobre `docs/qa/E3/gate.md`, `docs/qa/E3/gate.json` (exit_code 1, test_count 200, coverage_percent 89.4), `docs/qa/E3/perf.md` y `docs/qa/E3/QC1_contrato.md`. Contraste con el megaprompt, secciones 6 (M1 y M2), 8.1, 8.4, 10.2 (fila E3) y 11, y con `tests/test_e3_paths.py`, el docstring de `tests/test_e3_dcma.py` y la aproximación de vínculos driving en `src/atlaspmo/analysis/paths/mode_a.py`. HEAD `51d281f9e4aca9548be8a2e0bbb8eb736f26c3d5` (`test(qa): gate E3 ciclo 1, salida 1 (B-12)`). No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó código de producto, `docs/ESTADO.md`, el gate, umbrales, skips ni oráculos.

Este es el rechazo 1 de 3. No se marca la etapa como RECHAZADA-BLOQUEADA. Eso lo hace el orquestador solo después del tercer RECHAZADO. El rechazo devuelve a QC-3. No se bajan umbrales.

La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass. APROBADO no cabe.

## Contraste

`docs/qa/E3/gate.md` sale 1. Pass: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. Fail: G4 y G13.

G4, las mismas seis cifras que el gate de E2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.4, frente a 88.9 en E2. En `gate.json` el modelo sigue en 100.0 / 100.0. El resto subió a líneas 89.7 y ramas 76.4 (en E2, 88.9 / 74.7). El TOTAL de la tabla es 86 % (4070, 431, 1580, 324). «200 passed, 3 deselected in 18.00s» es la duración de esa suite. Esas alzas del total y del resto no mueven las seis cifras bajo 8.1.

G6 en `gate.json`: 3 passed in 3.57 s. G10: 42 requisitos de E3 citan un archivo de test que existe. El verde de la suite lo mide G3. G12: tests 200 frente a 175. `"benchmarks": {}`.

G13: «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E3/sabotaje.md`. No hay kill score de esta etapa. No se copia el de E1.

`docs/qa/E3/perf.md`. Equipo: Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise. Fecha 2026-10-21. Red de `gen_scale`, 30 000 actividades, `series=False`. No se usó un XER real. `evaluate` de calidad, sin baseline: 0.261 s. El test `tests/perf/test_quality.py` exige menos de 10 s y cronometra solo `evaluate`. 0.261 s está bajo ese tope. No incluye el CPM. CPLI, dentro de esa llamada, queda `no_evaluable` si la red no trae un término crítico usable. El documento no presenta eso como un pass de la definición de CPLI, solo del tiempo. Los otros criterios de la sección 11 no se miden ahí. La confirmación de redundancia de 30 000 sigue sin medirse.

`docs/qa/E3/QC1_contrato.md`, escrito antes del código nuevo de E3, deja los resultados condicionales a I-3 y a E0 y E1 RECHAZADA-BLOQUEADA, y a E2 si también queda bloqueada. E2 está RECHAZADA-BLOQUEADA. El contrato dice que QC-2 sigue incompleto fuera del caso de CPLI de ADR-017. El caso de 24 h y 16 h está. El oráculo no cubre feriado ni SS. BEI está y no es doble firma. El contrato decía que las bandas de modo A seguían fijas y que la cadena driving no estaba implementada.

Eso de las bandas ya no es el código. `PathsConfig.band_edges` vale `(0, 10, 20, 44)`. `tests/test_e3_paths.py` mueve el mismo par de holguras con cortes `(0, 5)` y, con el corte por defecto, las deja en el balde `0-10`. El mismo archivo, `test_mode_a_does_not_trace_a_driving_chain`, afirma que el modo A no marca la cadena driving. La aproximación en `mode_a.py` es: «Los vínculos driving no se marcan en modo A: no hay un campo citado de holgura libre del vínculo.» Bandas configurables no son la cadena driving, ni la continuidad, ni multiple float paths.

El docstring de `tests/test_e3_dcma.py` dice que los asserts siguen al código, que no son un oráculo de P6 con doble firma, y que no cubren SS solapado, feriado ni firma de baseline. `tests/test_e3_gao.py` deja `gao_06` y `gao_08` en estado `manual`, con el texto «Requiere revisión manual.» y valor `None`. `tests/test_e3_extra.py` y `tests/test_e3_profiles.py` afirman lo que el código hace en redes a mano. El docstring de extra dice que una WBS requerida no está implementada y no se trata como pass.

No se leyeron datos reales. No se bajaron umbrales.

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta.

El único tiempo de DCMA de esta etapa es 0.261 s, bajo 10 s. No es un crítico de rendimiento. El límite de esa medición —sin CPM, con CPLI `no_evaluable`, sin probar la definición— no la convierte en un pass de CPLI ni en una cifra por encima de 10 s. La definición no cumplida queda en I-21.

G13 no está medido. Sin informe no hay kill score que comparar con 8.3. No se inventa uno. No medido no es pass y no es un crítico de un score que esta evidencia no trae. Queda en I-20.

La confirmación de 30 000 sigue sin corrida (I-17, heredado). Sin una cifra medida de esa confirmación por encima de 3 minutos no se abre un crítico de tiempo nuevo.

## Importante

Abiertos. Bloquean el cierre.

No se cierran, y E3 queda condicional a ellos: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17 e I-18 parcial. E0, E1 y E2 siguen RECHAZADA-BLOQUEADA, cada una tras su tercer rechazo, sin cuarto ciclo.

De este ciclo, también abiertos: I-19, I-20, I-21, I-22, I-23 e I-24.

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. No se releyó el script ni la carpeta. No se cierra I-3. `docs/qa/E3/QC1_contrato.md` condiciona E3 a ese hallazgo.

### I-11 — G4 de E1, sigue abierto

No es el fail de este gate. No se reescribe con las cifras de E3. E1 está sin cuarto ciclo. No se cierra I-11. La lectura de este gate es I-19.

### I-12 — G13 de E1, sigue abierto y no es este gate

No se copia su kill score como resultado de E3. No hay corrida nueva de ese informe. No se cierra I-12. La lectura de este gate es I-20.

### I-13 — QC-1 de E1 tardío, sigue abierto

Desviación de proceso de E1. El contrato de E3, anterior al código nuevo, no cumple 8.4 de E1. No se reescribe esa historia. No se cierra I-13.

### I-14 — QC-2 parcial, sigue abierto

`tests/oracle/span.py` sigue en un solo caso de CPLI (ADR-017): 24 h de largo y 16 h de holgura. Este ciclo lo usa en `tests/test_e3_cpli.py` y no agrega SS solapado ni feriado. No cubre lo que I-14 dejó fuera. No se cierra I-14. La doble firma que falta en el resto de E3 va en I-21.

### I-15 — G4 de E2, sigue abierto

No es el fail de este gate. Las seis cifras coinciden con las de E3 y no se reescriben como si E2 hubiera mejorado. E2 está sin cuarto ciclo. No se cierra I-15. La lectura de este gate es I-19.

### I-16 — G13 de E2, sigue abierto y no es este gate

E2 no tiene `sabotaje.md` ni kill score propio. No se cierra I-16. No se usa el score de E1 para cerrarlo. La lectura de este gate es I-20.

### I-17 — La confirmación de 30 000 no cumple por proyección, sigue abierto

No es un criterio de la fila E3 y no se midió en `docs/qa/E3/perf.md`. Sigue sin una corrida de 30 000. No es un crítico de tiempo. No se cierra I-17. El 0.261 s de `evaluate` no es esa confirmación.

### I-18 — QC-2 de redundancia, parcial, sigue abierto

ADR-018 sigue en un solo camino. Este ciclo no agregó otro caso de redundancia. No se cierra I-18.

### I-19 — G4 de E3 incumple 8.1

Estado: abierto. El gate lo deja en fail. No se marca pass. No se baja el umbral. Las seis cifras de paquetes no se movieron respecto del gate de E2.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. La línea base de la sección 10.2 no aplica a E3. Perdona G4 solo en E0.

Siguen bajo el umbral, iguales al gate de E2:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

El modelo en 100.0 / 100.0 no está en el texto de fail y no cierra el hallazgo. El resto, líneas 89.7, está sobre el 80 % y no compensa. Las ramas 76.4 del resto no están en el texto de fail. cobertura_total 89.4 y el TOTAL 86 % de la tabla (4070, 431, 1580, 324) no dejan el control en pass. «200 passed, 3 deselected in 18.00s» es la duración de esa suite, no un cumplimiento de 8.1. El alza de cobertura_total, de 88.9 a 89.4, está en el resto, no en calendarios, motor ni lógica.

### I-20 — G13 de E3 no está medido

Estado: abierto. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa.

`docs/qa/E3/sabotaje.md` no existe. El detalle de G13 es «no medido: falta el informe de qa-sabotaje». Sin informe no hay cifra que comparar con 8.3. No medido no es pass. No se inventa un kill score. No se usa el kill score de E1 como score de este gate. No se usa el «no medido» de E2 para declarar este control cumplido.

### I-21 — Falta la doble firma de las métricas de E3

Estado: abierto. No es un crítico: esta evidencia no trae un número de CPLI o de BEI distinto del que el caso a mano afirma. El criterio igual no está cumplido.

La fila E3 de 10.2 pide DCMA y chequeos de calidad sobre 30 000 bajo 10 s, y todas las métricas contra esperados con doble firma. 8.4, QC-2, pide esperados por otro método y doble firma. El verde de G3 no es ese método. G10 en verde solo comprueba que el archivo citado existe. No comprueba doble firma.

Lo que hay, y no alcanza:

- CPLI: un caso de 24 h + 16 h (ADR-017). `tests/test_e3_cpli.py` espera `(24 + 16) / 24`. `tests/fixtures/synthetic/cases/cpli.yaml` trae `verificado_por: tests/oracle/span.py`. El contrato y el docstring de `tests/test_e3_dcma.py` dicen que no hay SS solapado ni feriado. B-10, en 10.1, pide esos dos casos además de la doble firma. Sigue abierto como aceptación de la brecha. No se cierra I-14.
- BEI: `tests/test_e3_bei.py` cuenta una completada antes de tiempo. El contrato dice que no es doble firma. B-11, en 10.1, pide el numerador de todas las completadas. El test afirma lo que el código hace. No hay segunda firma.
- `tests/test_e3_dcma.py`, `test_e3_gao.py`, `test_e3_extra.py` y `test_e3_profiles.py` afirman lo que el código hace en redes a mano. El docstring de DCMA lo dice: no son un oráculo de P6 con doble firma.
- GAO 6 y GAO 8 quedan en estado `manual`, con el mensaje «Requiere revisión manual.» M1 permite listar lo no automatizable así. Ese estado lo escribe el código y lo afirma el test. No es una revisión humana hecha.

QC-2 sigue incompleto fuera del caso CPLI de ADR-017. No se inventa un oráculo de P6. No se leyó `data/real/`.

El 0.261 s no cierra este hallazgo. `perf.md` dice que en esa red CPLI queda `no_evaluable` y que el tiempo no prueba la definición.

### I-22 — El modo A no marca la cadena driving

Estado: abierto. Desviación de M2 y de B-12 (10.1). La aproximación está registrada: no es silenciosa. El requisito igual no está cumplido.

M2 pide vínculos driving (holgura libre del vínculo = 0) y el trazado de la cadena driving hacia cualquier hito elegido. B-12 pide ese trazado, multiple float paths propios y la continuidad; las bandas configurables son solo una parte de la aceptación.

`tests/test_e3_paths.py` cubre las bandas. El corte por defecto del código es `(0, 10, 20, 44)`. El test de cortes custom no afirma la cadena. `test_mode_a_does_not_trace_a_driving_chain` exige que el texto de aproximaciones contenga «driving no se marcan». La frase en `src/atlaspmo/analysis/paths/mode_a.py` es: «Los vínculos driving no se marcan en modo A: no hay un campo citado de holgura libre del vínculo.»

R-032 cita ese mismo archivo para «cadena driving, float paths y bandas configurables». G10 queda en pass porque el archivo existe. El test documenta la ausencia. No prueba el trazado.

`src/atlaspmo/engine/cpm.py` recorre predecesoras driving en `_longest_ids` hasta el término del proyecto. Eso no es el trazado hacia cualquier hito de M2, no lo expone el modo A y el test de E3 afirma que el modo A no marca esos vínculos. No se usa para cerrar I-22.

`docs/qa/E3/QC1_contrato.md` decía que las bandas seguían fijas. El código ya las recibe. Esa corrección parcial no cierra la cadena driving ni B-12.

### I-23 — Continuidad de la ruta y multiple float paths no están implementados

Estado: abierto. Desviación de M2 y de B-12. No hay un test que los afirme como hechos.

M2 pide multiple float paths calculados por el motor, sin depender de que P6 los haya corrido, y la continuidad de la ruta crítica desde la fecha de corte hasta el término, sin quiebres injustificados.

`PathsModeB` recalcula con el motor y corre el CP Test: atrasa 8 horas la primera actividad crítica ordenada por `task_code`. No verifica continuidad ni calcula multiple float paths. El modo A copia `float_path` o `int_path` si la columna está, y si no, anota que no hay columna de ruta guardada. Copiar una columna guardada no es multiple float paths del motor. `tests/test_e3_paths.py` no cubre esa copia ni la continuidad.

R-331 cita `tests/test_e3_paths.py` para la continuidad, «de la fecha de corte al término». Ese archivo no tiene un assert de continuidad. G10 no lo detecta: solo exige que el archivo exista. Es un test que no prueba lo que la fila dice. No se marca el requisito como cumplido.

### I-24 — La WBS requerida de R-326 no está implementada

Estado: abierto. No se trata como pass, y tampoco está hecha.

M1 pide actividades sin los códigos o la WBS requeridos. R-326 cita `tests/test_e3_extra.py`. El docstring de ese archivo dice: «A required WBS is not implemented and is not treated as a pass.» El test de códigos deja `missing_codes` en `no_evaluable` si el perfil no exige códigos, y en `no_cumple` si se exige uno. No hay un chequeo de WBS requerida en `src/atlaspmo/analysis/quality/`. G10 queda en pass porque el archivo existe. No prueba la WBS. No es un resultado numérico incorrecto: no hay una cifra de WBS que esta evidencia dé por buena.

## Menor

No bloquean. No autorizan el cierre.

### M-15 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest`.

### M-16 — G6 en verde no es la definición de CPLI

Pass: 3 passed in 3.57 s. Cronometra `evaluate` bajo 10 s. El 0.261 s está en `perf.md`, no en el detalle de G6. No incluye el CPM. En esa red CPLI queda `no_evaluable`. No es un fail de G6 y no acredita I-21.

### M-17 — G12 no compara tiempos

Pass: tests 200 frente a 175. `"benchmarks": {}`. cobertura_total 89.4 no declara G4 en pass. El alza frente a 88.9 no es una regresión de G12.

### M-18 — `gate.md` corta el detalle

La línea de G4 se corta en «engine lineas 89.». La de G6 se queda en la barra. Las cifras completas están en `gate.json`, incluido el reloj de 18.00 s y el de G6, 3.57 s. No cambia I-19 ni el fail.

### M-19 — El contrato no usa los id de 10.1

`docs/qa/E3/QC1_contrato.md` llama B-11 al CPLI, B-12 al BEI y B-13 a las bandas. La sección 10.1 llama B-10 al CPLI, B-11 al BEI y B-12 a M2. El contrato además dice que las bandas seguían fijas; el código ya las recibe. No cambia las cifras. No cierra I-21, I-22 ni I-23. No es un crítico.

## Gate

Exit code 1. test_count 200. Cobertura citada por el control: 89.4. Rechazo 1 de 3. No se marca la etapa bloqueada. No se bajan umbrales. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-15 |
| G4 | fail | I-19. Igual que E2 en las seis cifras: calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. cobertura_total 89.4. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a-e con perfil qa |
| G6 | pass | 3 passed in 3.57 s. `evaluate` en 0.261 s, bajo 10 s. No incluye el CPM ni prueba CPLI. Ver M-16. No es un crítico |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 42 requisitos citan un archivo que existe. No es doble firma, no es la cadena driving, no es la continuidad y no cierra R-326 |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | 200 frente a 175. Ver M-17 |
| G13 | fail | I-20. No medido. No se copia el kill score de E1 |
