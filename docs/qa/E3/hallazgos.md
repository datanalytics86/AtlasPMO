# Hallazgos E3 — ciclo 3

Revisión de QC-6 sobre `docs/qa/E3/gate.md`, `docs/qa/E3/gate.json` (exit_code 1, test_count 201, coverage_percent 89.4), `docs/qa/E3/ciclo3.md`, `docs/qa/E3/ciclo2.md` y `docs/qa/E3/perf.md`. HEAD `98a6d28f39dc42a8e276c202fb79833b308caafe` (`test(qa): gate E3 ciclo 3, salida 1 (B-12)`). `740c7f6` solo agrega `ciclo3.md`. Entre `436e1fc` y `98a6d28` no hay diff en `src/` ni en `tests/`. El contraste de código del ciclo 2 queda vigente por ese diff vacío: esta revisión no releyó el producto. No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó código de producto, `docs/ESTADO.md`, el gate, umbrales, skips ni oráculos. Este archivo reemplaza los hallazgos del ciclo 2. El texto de ese ciclo queda en `b46bfb9`.

Este es el rechazo 3 de 3. No se autoriza un cuarto ciclo ni bajar umbrales (ADR-014). ADR-013 no abre otro ciclo de esta etapa. El orquestador cambia el estado después. Esta revisión no marca la etapa bloqueada.

La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass. APROBADO no cabe. No se reabren E0, E1 ni E2.

## Contraste

`docs/qa/E3/gate.md` sale 1. Pass: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. Fail: G4 y G13. Ese archivo no se reescribió en este ciclo: su último commit es `436e1fc`. Las cifras completas están en `gate.json`.

G4, las mismas seis cifras del ciclo 1, del ciclo 2 y del gate de E2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.4. En `gate.json` el modelo sigue en 100.0 / 100.0. El resto sigue en líneas 89.7 y ramas 76.4. El TOTAL de la tabla es 86 % (4093, 432, 1588, 326). «201 passed, 3 deselected in 18.47s» es la duración de esa suite. En el ciclo 2 eran 22.46 s. El reloj no mueve las seis cifras que están bajo 8.1.

G6 en `gate.json`: 3 passed in 3.83 s. En el ciclo 2 eran 3.80 s. G10: 42 requisitos de E3 citan un archivo de test que existe. El verde de la suite lo mide G3. G12: tests 201 frente a 175. `"benchmarks": {}`.

G13: «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E3/sabotaje.md`. No hay kill score de esta etapa. `docs/qa/E3/ciclo3.md` dice que no se copia el 54.0 de E1, porque el código de lógica cambió en E2 y esa cifra no llega a 85. No se inventa otro score. No se rehace la mutación.

`docs/qa/E3/ciclo3.md` dice que no hay una corrección correcta, en esta corrida, que deje G4 o G13 en verde. No se agregan tests vacíos. No se bajan umbrales. No se lee un golden ni un XER real. La cadena driving del ciclo 2 queda. Siguen sin implementarse los multiple float paths, la continuidad desde la fecha de corte hasta el término, la doble firma fuera del CPLI de 24 h + 16 h, el caso con SS solapado, el caso con feriado y la WBS requerida de R-326.

`docs/qa/E3/perf.md` no cambia de cifra. Equipo: Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise. Fecha 2026-10-21. Red de `gen_scale`, 30 000 actividades, `series=False`. No se usó un XER real. `evaluate` de calidad, sin baseline: 0.261 s. El test `tests/perf/test_quality.py` exige menos de 10 s y cronometra solo `evaluate`. 0.261 s está bajo ese tope. No incluye el CPM. CPLI, dentro de esa llamada, queda `no_evaluable` si la red no trae un término crítico usable. El documento no presenta eso como un pass de la definición de CPLI, solo del tiempo. G6 no prueba CPLI. Los otros criterios de la sección 11 no se miden ahí. La confirmación de redundancia de 30 000 sigue sin medirse.

`docs/qa/E3/ciclo2.md` sigue describiendo la única cadena que hay. La primera corrida del test `test_the_longer_predecessor_is_the_driving_one` falló con `KeyError: 'driving_codes'`. El motor ya guardaba `driving_preds` y no los devolvía. El modo B arma `driving_codes` y `driving_chain`. En la red a mano, SHORT dura 8 h y no es driving; LONG dura 16 h y sí lo es; ambas son FS hacia JOIN. La cadena de JOIN es LONG y JOIN. No es un float path de P6 y no hay doble firma. Este ciclo no tocó ese test ni `src/`. No se reejecutó el test. El pass de G3 es el de la suite registrada, no una corrida nueva de esta revisión.

Esa publicación sigue siendo la corrección parcial del ciclo 2. No es un float path de P6. No es doble firma. No cierra B-12. Multiple float paths y la continuidad siguen sin implementarse. El modo A sigue sin marcar driving, según el contraste del ciclo 2, que este diff no altera.

`docs/qa/E3/QC1_contrato.md`, escrito antes del código nuevo de E3, deja los resultados condicionales a I-3 y a E0 y E1 RECHAZADA-BLOQUEADA, y a E2 si también queda bloqueada. E2 está RECHAZADA-BLOQUEADA. El contrato dice que QC-2 sigue incompleto fuera del caso de CPLI de ADR-017. El caso de 24 h y 16 h está. El oráculo no cubre feriado ni SS. BEI está y no es doble firma. El contrato decía que las bandas de modo A seguían fijas y que la cadena driving no estaba implementada. Las bandas ya no están fijas desde el ciclo 1. La cadena del modo B se publicó en el ciclo 2, en el caso a mano, y el ciclo 3 no la amplió. Ninguna de las dos correcciones cierra el contrato ni B-12.

No se leyeron datos reales. No se bajaron umbrales.

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta.

El único tiempo de DCMA de esta etapa es 0.261 s, bajo 10 s. No es un crítico de rendimiento. El límite de esa medición —sin CPM, con CPLI `no_evaluable`, sin probar la definición— no la convierte en un pass de CPLI ni en una cifra por encima de 10 s. La definición no cumplida queda en I-21. G6 en verde no cambia esa lectura.

G13 no está medido. Sin informe no hay kill score que comparar con 8.3. El 54.0 de E1 no es el score de este gate: `ciclo3.md` dice que no se copia, porque el código de lógica cambió en E2 y esa cifra no llega a 85. No se inventa otro. No medido no es pass y no es un crítico de un score que esta evidencia no trae. Queda en I-20.

La confirmación de 30 000 sigue sin corrida (I-17, heredado). Sin una cifra medida de esa confirmación por encima de 3 minutos no se abre un crítico de tiempo nuevo.

La cadena driving del ciclo 2 no se trata como un número incorrecto. El test y la aproximación del ciclo 2 dicen qué afirman y qué no es. Este ciclo no la cambia. La brecha que queda es de spec, no un crítico. Va en I-22.

## Importante

Abiertos. Bloquean el cierre. Ninguno se cierra en este ciclo. No se abre un importante nuevo: no hubo cambio de producto.

No se cierran, no se reabren, y E3 queda condicional a ellos: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17 e I-18 parcial. E0, E1 y E2 siguen RECHAZADA-BLOQUEADA, cada una tras su tercer rechazo, sin cuarto ciclo. Esta revisión no les cambia el estado.

De E3, también abiertos: I-19, I-20, I-21, I-22, I-23 e I-24. I-22 queda como la corrección parcial del ciclo 2. No se cierra.

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. No se releyó el script ni la carpeta. No se cierra I-3. No se reabre E0. `docs/qa/E3/QC1_contrato.md` condiciona E3 a ese hallazgo.

### I-11 — G4 de E1, sigue abierto

No es el fail de este gate. No se reescribe con las cifras de E3. E1 está sin cuarto ciclo. No se cierra I-11. No se reabre E1. La lectura de este gate es I-19.

### I-12 — G13 de E1, sigue abierto y no es este gate

No se copia su kill score como resultado de E3. No hay corrida nueva de ese informe. No se cierra I-12. La lectura de este gate es I-20.

### I-13 — QC-1 de E1 tardío, sigue abierto

Desviación de proceso de E1. El contrato de E3, anterior al código nuevo, no cumple 8.4 de E1. No se reescribe esa historia. No se cierra I-13.

### I-14 — QC-2 parcial, sigue abierto

`tests/oracle/span.py` sigue en un solo caso de CPLI (ADR-017): 24 h de largo y 16 h de holgura. Este ciclo no agrega SS solapado ni feriado. No cubre lo que I-14 dejó fuera. No se cierra I-14. La doble firma que falta en el resto de E3 va en I-21.

### I-15 — G4 de E2, sigue abierto

No es el fail de este gate. Las seis cifras coinciden con las de E3 y no se reescriben como si E2 hubiera mejorado. E2 está sin cuarto ciclo. No se cierra I-15. No se reabre E2. La lectura de este gate es I-19.

### I-16 — G13 de E2, sigue abierto y no es este gate

E2 no tiene `sabotaje.md` ni kill score propio. No se cierra I-16. No se usa el score de E1 para cerrarlo. La lectura de este gate es I-20.

### I-17 — La confirmación de 30 000 no cumple por proyección, sigue abierto

No es un criterio de la fila E3 y no se midió en `docs/qa/E3/perf.md`. Sigue sin una corrida de 30 000. No es un crítico de tiempo. No se cierra I-17. El 0.261 s de `evaluate` no es esa confirmación.

### I-18 — QC-2 de redundancia, parcial, sigue abierto

ADR-018 sigue en un solo camino. Este ciclo no agregó otro caso de redundancia. No se cierra I-18.

### I-19 — G4 de E3 incumple 8.1

Estado: abierto. El gate lo deja en fail. No se marca pass. No se baja el umbral. Las seis cifras de paquetes no se movieron respecto del ciclo 1, del ciclo 2 ni del gate de E2.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. La línea base de la sección 10.2 no aplica a E3. Perdona G4 solo en E0.

Siguen bajo el umbral:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

El modelo en 100.0 / 100.0 no está en el texto de fail y no cierra el hallazgo. El resto, líneas 89.7, está sobre el 80 % y no compensa. Las ramas 76.4 del resto no están en el texto de fail. cobertura_total 89.4 y el TOTAL 86 % de la tabla (4093, 432, 1588, 326) no dejan el control en pass. «201 passed, 3 deselected in 18.47s» es la duración de esa suite, no un cumplimiento de 8.1. En el ciclo 2 eran 22.46 s. El reloj distinto no mueve el fail.

### I-20 — G13 de E3 no está medido

Estado: abierto. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa.

`docs/qa/E3/sabotaje.md` no existe. El detalle de G13 es «no medido: falta el informe de qa-sabotaje». Sin informe no hay cifra de esta etapa que comparar con 8.3. No medido no es pass. No se inventa un kill score. No se usa el 54.0 de E1 como score de este gate: `ciclo3.md` dice que el código de lógica cambió en E2 y que esa cifra no llega a 85. Copiarlo sería falso. No se usa el «no medido» de E2 para declarar este control cumplido. No se rehace la mutación.

### I-21 — Falta la doble firma de las métricas de E3

Estado: abierto. No es un crítico: esta evidencia no trae un número de CPLI o de BEI distinto del que el caso a mano afirma. El criterio igual no está cumplido. Este ciclo no agregó un caso.

La fila E3 de 10.2 pide DCMA y chequeos de calidad sobre 30 000 bajo 10 s, y todas las métricas contra esperados con doble firma. 8.4, QC-2, pide esperados por otro método y doble firma. El verde de G3 no es ese método. G10 en verde solo comprueba que el archivo citado existe. No comprueba doble firma.

Lo que hay, y no alcanza:

- CPLI: un caso de 24 h + 16 h (ADR-017). No hay caso de SS solapado ni feriado. B-10, en 10.1, pide esos dos casos además de la doble firma. Sigue abierto como aceptación de la brecha. No se cierra I-14. El contraste del ciclo 2 ya dejó que el `PR_SS` con lag -8 de `tests/test_e3_dcma.py` no es ese caso. Este ciclo no lo cambia: `tests/` no tiene diff.
- BEI: el contrato dice que `tests/test_e3_bei.py` no es doble firma. Este ciclo no agregó otro método.
- Los tests de DCMA, GAO, extra y perfiles, según el contraste del ciclo 2, afirman lo que el código hace en redes a mano. No son un oráculo de P6 con doble firma. No se releyeron: el árbol de tests no cambió.
- La cadena driving del ciclo 2 tampoco es doble firma. El test afirma la red a mano. No cierra este hallazgo.
- GAO 6 y GAO 8, en el contraste del ciclo 2, quedan en estado `manual`. M1 permite listar lo no automatizable así. Ese estado no es una revisión humana hecha. Este ciclo no la hizo.

QC-2 sigue incompleto fuera del caso CPLI de ADR-017. No se inventa un oráculo de P6. No se leyó `data/real/`.

El 0.261 s no cierra este hallazgo. `perf.md` dice que en esa red CPLI queda `no_evaluable` y que el tiempo no prueba la definición.

### I-22 — La cadena driving del modo B sigue siendo una corrección parcial

Estado: abierto. La corrección parcial es la del ciclo 2. Este ciclo no la amplió y no cambia producto. No cierra B-12 ni la doble firma. Desviación de M2 que sigue abierta en lo que el caso no cubre.

M2 pide vínculos driving (holgura libre del vínculo = 0) y el trazado de la cadena driving hacia cualquier hito elegido. B-12 pide ese trazado, multiple float paths propios y la continuidad. Las bandas configurables son solo una parte de la aceptación y ya estaban en el ciclo 1.

Qué quedó en el ciclo 2, y no alcanza:

- `docs/qa/E3/ciclo2.md` registra el fallo inicial `KeyError: 'driving_codes'` y la publicación posterior.
- El modo B arma la columna `driving_codes` y la tabla `driving_chain`, desde el término del proyecto o desde `milestone_code`.
- `test_the_longer_predecessor_is_the_driving_one` afirma, en la red SHORT 8 h y LONG 16 h hacia JOIN, que solo LONG es driving y que la cadena es LONG y JOIN.
- La aproximación del ciclo 2 deja escrito que no es un float path de P6.

Qué sigue fuera, y este ciclo no lo toca:

- El modo A no marca driving. No es una aproximación silenciosa, según el contraste del ciclo 2. El requisito de M2 igual no queda cumplido en ese modo.
- El caso es una red a mano. No es doble firma. No cierra I-21.
- No es multiple float paths ni la continuidad desde la fecha de corte. Eso queda en I-23.

R-032 cita `tests/test_e3_paths.py`. G10 queda en pass porque el archivo existe. El test prueba un caso. No prueba el resto de B-12. No se marca B-12 cerrado.

### I-23 — Continuidad de la ruta y multiple float paths no están implementados

Estado: abierto. Desviación de M2 y de B-12. No hay un test que los afirme como hechos. Este ciclo no los implementa. `ciclo3.md` lo deja escrito.

M2 pide multiple float paths calculados por el motor, sin depender de que P6 los haya corrido, y la continuidad de la ruta crítica desde la fecha de corte hasta el término, sin quiebres injustificados.

El contraste del ciclo 2, vigente porque `src/` y `tests/` no cambiaron, deja esas dos frases en las aproximaciones del modo B: no se calculan los multiple float paths y no se verifica la continuidad desde la fecha de corte hasta el término. La cadena de LONG y JOIN no los sustituye. Copiar `float_path` o `int_path` si la columna está no es multiple float paths del motor. `tests/test_e3_paths.py` no afirma la continuidad ni float paths propios.

R-331 cita `tests/test_e3_paths.py` para la continuidad, de la fecha de corte al término. Ese archivo no afirma la continuidad. G10 no lo detecta: solo exige que el archivo exista. Es un test que no prueba lo que la fila dice. No se marca el requisito como cumplido.

### I-24 — La WBS requerida de R-326 no está implementada

Estado: abierto. No se trata como pass, y tampoco está hecha. Sigue sin implementarse la mitad de WBS de R-326. Este ciclo no la agrega. `ciclo3.md` lo deja escrito.

M1 pide actividades sin los códigos o la WBS requeridos. R-326 cita `tests/test_e3_extra.py`. El contraste del ciclo 2 cita el docstring: una WBS requerida no está implementada y no se trata como pass. El árbol de tests no cambió. G10 queda en pass porque el archivo existe. No prueba la WBS. No es un resultado numérico incorrecto: no hay una cifra de WBS que esta evidencia dé por buena.

## Menor

No bloquean. No autorizan el cierre.

### M-15 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest`.

### M-16 — G6 en verde no es la definición de CPLI

Pass: 3 passed in 3.83 s. En el ciclo 2 eran 3.80 s. Cronometra el perfil de rendimiento. El 0.261 s está en `perf.md`, no en el detalle de G6. No incluye el CPM. En esa red CPLI queda `no_evaluable`. No es un fail de G6, no es un crítico de rendimiento y no acredita I-21.

### M-17 — G12 no compara tiempos

Pass: tests 201 frente a 175. `"benchmarks": {}`. cobertura_total 89.4 no declara G4 en pass. El ciclo 3 no agrega tests. Las seis cifras de I-19 no se mueven.

### M-18 — `gate.md` no se reescribió y corta el detalle

El archivo sigue en el commit `436e1fc`. La línea de G4 se corta en «engine lineas 89.». La de G6 se queda en la barra. Las cifras completas están en `gate.json` de `98a6d28`, incluido el reloj de 18.47 s y el de G6, 3.83 s. No cambia I-19 ni el fail.

### M-19 — El contrato no usa los id de 10.1 y quedó atrás del ciclo 2

`docs/qa/E3/QC1_contrato.md` llama B-11 al CPLI, B-12 al BEI y B-13 a las bandas. La sección 10.1 llama B-10 al CPLI, B-11 al BEI y B-12 a M2. El contrato además dice que las bandas seguían fijas y que la cadena driving no estaba implementada. El código ya recibe las bandas desde el ciclo 1, y el modo B publicó una cadena en la red SHORT / LONG / JOIN en el ciclo 2. El ciclo 3 no corrige el contrato ni amplía la cadena. No cambia las cifras. No cierra I-21, I-22 ni I-23. No es un crítico.

## Gate

Exit code 1. test_count 201. Cobertura citada por el control: 89.4. Rechazo 3 de 3. No se autoriza un cuarto ciclo. Esta revisión no marca la etapa bloqueada. El orquestador cambia el estado después. No se bajan umbrales. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-15 |
| G4 | fail | I-19. Igual que el ciclo 1, el ciclo 2 y E2 en las seis cifras: calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. cobertura_total 89.4. Suite en 18.47 s. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a-e con perfil qa |
| G6 | pass | 3 passed in 3.83 s. `evaluate` en 0.261 s, bajo 10 s. No incluye el CPM ni prueba CPLI. Ver M-16. No es un crítico |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 42 requisitos citan un archivo que existe. No es doble firma, no cierra B-12, no es la continuidad y no cierra R-326 |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | 201 frente a 175. Ver M-17 |
| G13 | fail | I-20. No medido. No se inventa un score y no se copia el 54.0 de E1 |
