# Hallazgos E4 — ciclo 2

Revisión de QC-6 sobre `docs/qa/E4/gate.md`, `docs/qa/E4/gate.json` (exit_code 1, test_count 205, coverage_percent 89.5), `docs/qa/E4/ciclo2.md` y `docs/qa/E4/perf.md`. HEAD `bec5c9b21c7709caa4c8fba117ffbd66a207dc53` (`test(qa): gate E4 ciclo 2, salida 1 (B-07)`). Entre `6163ea294f652edb4ad821fccba442125b665ab3` y este HEAD no hay diff en `src/`, `tests/` ni `scripts/`. `gate.md` y `perf.md` no cambian. `gate.json` solo cambia dos relojes. El contraste de código del ciclo 1 queda vigente por ese diff vacío: esta revisión no releyó el producto. No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó código de producto, `docs/ESTADO.md`, el gate, umbrales, skips ni oráculos. Este archivo reemplaza los hallazgos del ciclo 1. El texto de ese ciclo queda en `ab66a973a0e3057a4ee1af837842073a4f750a87`.

Este es el rechazo 2 de 3. La etapa no queda bloqueada. No se baja ningún umbral. No se copia un kill score. El orquestador no cierra la etapa con esta corrida. La detención de 8.4 ocurre tras el tercer rechazo consecutivo. Este es el segundo.

La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass. El cierre no cabe. No se reabren E0, E1, E2 ni E3.

## Contraste

`docs/qa/E4/gate.md` sale 1. Pass: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. Fail: G4 y G13. Las cifras completas están en `gate.json`. El archivo `gate.md` es el del ciclo 1.

G4, las mismas seis cifras de paquete que el ciclo 1, que E3 y que E2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.5. En `gate.json` el modelo sigue en 100.0 / 100.0. El resto está en líneas 89.8 y ramas 76.8. El TOTAL de la tabla es 86 % (4102, 431, 1594, 324). «205 passed, 4 deselected in 19.00s» es la duración de esta suite. En el ciclo 1 eran 19.64 s. El reloj no mueve las seis cifras que están bajo 8.1.

G6 en `gate.json`: 4 passed in 3.90 s. En el ciclo 1 eran 4.01 s. G10: 13 requisitos de E4 citan un archivo de test que existe. El verde de la suite lo mide G3. G12: tests 205 frente a 201. `"benchmarks": {}`.

G13: «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E4/sabotaje.md`. No hay kill score de esta etapa. No se inventa uno. No se copia el de E1. No se rehace la mutación.

`docs/qa/E4/ciclo2.md` no integra una corrección. No se corren 1 000 CPM de 30 000 actividades. No se recorta el tornado al cono. G4 y G13 no se tocan. No se bajan umbrales. No se copia un kill score. La curva por periodo, el histograma y la sobreasignación siguen sin implementarse. `fact_timephased` queda en el balde corte. numba no se carga: no hay evidencia de una wheel que deje el resultado bajo 5 minutos, y no se afirma que la haya.

`docs/qa/E4/perf.md` no cambió. Equipo: Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise. Fecha 2026-10-21. Red de `gen_scale`, 30 000 actividades, `series=False`. No se usó un XER real. Un CPM, una sola llamada a `schedule_cpm`, midió 9.401 s. No es Monte Carlo. Monte Carlo de 30 000 por 1 000 no se corrió. La proyección 1 000 × 9.401 s son unas 2,6 h. El documento dice que no es una medición y que no cumple 5 minutos. El tornado de 30 000 no se corrió. Hoy es un CPM completo por actividad y no se proyecta como cumplimiento. numba no está cargado. El tornado no recorta al cono.

La lectura del ciclo 1, vigente porque el código no cambió: `tests/perf/test_montecarlo.py` cronometra 4 iteraciones de dos actividades y exige menos de 30 s. Ese verde no es el criterio de la sección 11. G6 en verde tampoco lo es. `_tornado` reprograma el cronograma completo por actividad y no recorta al cono de sucesoras. `fact_timephased` guarda la duración remanente en el balde corte. No es una curva por periodo. El invariante e ya estaba en `tests/property/test_invariant_e.py`. R-042 apunta a ese archivo. No es doble firma. `tests/test_e4_outputs.py` no es una firma de P6. QC-2 sigue incompleto. No se inventa un oráculo de P6 ni un tiempo de 30 000 por 1 000.

`docs/qa/E4/QC1_contrato.md` deja los resultados condicionales a I-3 y a los bloqueos de E0, E1, E2 y E3. Esta revisión no les cambia el estado. El contrato no está en el diff de este ciclo.

No se leyeron datos reales. No se bajaron umbrales.

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta.

No hay crítico de un tiempo de 1 000 iteraciones, porque no se midió. Las 1 000 iteraciones de 30 000 actividades no se corrieron. La proyección de unas 2,6 h no es una medición y no cumple 5 minutos. El único tiempo de esta etapa en `perf.md` es un CPM de 9.401 s. No es Monte Carlo y no está por encima de 5 minutos. El criterio igual no está cumplido. Va en I-29. G6 en verde no cambia esa lectura.

8.5 nombra un criterio de la sección 11 incumplido entre lo crítico. La sección 11 dice que no medido nunca equivale a cumplido. G6 falla si un criterio medible de la etapa supera su meta. Aquí no hay una superación medida. No se abre un crítico de un tiempo que esta evidencia no trae.

El tornado de 30 000 no se corrió. No hay una cifra medida de ese tornado por encima de una meta. La brecha es de spec: sigue siendo un CPM completo por actividad, y el ciclo 2 no integra el cono. Va en I-27.

G13 no está medido. Sin informe no hay kill score que comparar con 8.3. No se inventa un score y no se copia el de E1. No medido no es un pase y no es un crítico de un score que esta evidencia no trae. Va en I-26.

La curva del balde «corte» no se trata como un número incorrecto. El ciclo 2 la deja donde estaba. La brecha que queda es de spec, no un crítico. Va en I-28.

## Importante

Abiertos. Bloquean el cierre. Ninguno se cierra en este ciclo. No se abre un importante nuevo: no hubo cambio de producto.

No se cierran, no se reabren, y E4 queda condicional a ellos: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17 e I-18 parcial. De E3, también abiertos: I-19 (G4), I-20 (G13), I-21 (doble firma), I-22 (driving parcial), I-23 (float paths y continuidad) e I-24 (WBS). E0, E1, E2 y E3 siguen bloqueadas, cada una tras su tercer rechazo, sin cuarto ciclo. Esta revisión no les cambia el estado. Los resultados de E4 quedan condicionales a I-3 y a esos bloqueos.

De E4, siguen abiertos: I-25 (G4), I-26 (G13), I-27 (el cono), I-28 (la curva por periodo) e I-29 (los 5 minutos).

### I-3 — Heredado de E0, sigue abierto

R-198 no prueba que `scripts/run_conformance.py` no abra `ATLASPMO_GOLDEN_DIR`. No se releyó el script ni la carpeta. No se cierra I-3. No se reabre E0. El contrato de E4 condiciona la etapa a ese hallazgo.

### I-11 — G4 de E1, sigue abierto

No es el fail de este gate. No se reescribe con las cifras de E4. E1 está sin cuarto ciclo. No se cierra I-11. No se reabre E1. La lectura de este gate es I-25.

### I-12 — G13 de E1, sigue abierto y no es este gate

No se copia su kill score como resultado de E4. No hay corrida nueva de ese informe. No se cierra I-12. La lectura de este gate es I-26.

### I-13 — QC-1 de E1 tardío, sigue abierto

Desviación de proceso de E1. El contrato de E4 no cumple 8.4 de E1. No se reescribe esa historia. No se cierra I-13.

### I-14 — QC-2 parcial, sigue abierto

`tests/oracle/span.py` sigue en un solo caso de CPLI (ADR-017): 24 h de largo y 16 h de holgura. Esta revisión no agrega SS solapado ni feriado. No hay diff de producto. No se cierra I-14. La doble firma que falta en E3 sigue en I-21. La de E4 no se da por hecha: el invariante e y las salidas de varianza cero no son doble firma.

### I-15 — G4 de E2, sigue abierto

No es el fail de este gate. Las seis cifras de paquete coinciden con las de E4 y no se reescriben como si E2 hubiera mejorado. E2 está sin cuarto ciclo. No se cierra I-15. No se reabre E2. La lectura de este gate es I-25.

### I-16 — G13 de E2, sigue abierto y no es este gate

E2 no tiene `sabotaje.md` ni kill score propio. No se cierra I-16. No se usa el score de E1 para cerrarlo. La lectura de este gate es I-26.

### I-17 — La confirmación de 30 000 no cumple por proyección, sigue abierto

No es el criterio de Monte Carlo y no se midió de nuevo. Sigue sin una corrida de confirmación de 30 000. No es un crítico de tiempo. No se cierra I-17. Los 9.401 s de un CPM no son esa confirmación.

### I-18 — QC-2 de redundancia, parcial, sigue abierto

ADR-018 sigue en un solo camino. Esta revisión no agregó otro caso de redundancia. No se cierra I-18.

### I-19 — G4 de E3, sigue abierto y no es la lectura nueva

Las seis cifras de paquete coinciden con las de este gate. La cobertura_total de E3 era 89.4, no el 89.5 de esta corrida. No se reescribe I-19 con la cifra de E4. E3 está sin cuarto ciclo. No se cierra I-19. No se reabre E3. La lectura de este gate es I-25.

### I-20 — G13 de E3, sigue abierto y no es este gate

E3 no tiene `sabotaje.md`. No se cierra I-20. No se copia un score para declararlo medido. La lectura de este gate es I-26.

### I-21 — Doble firma de E3, sigue abierta

No es un hallazgo nuevo de E4. El invariante e y las salidas de varianza cero no cierran la doble firma de las métricas de E3. No se cierra I-21.

### I-22 — Cadena driving parcial de E3, sigue abierta

La cadena del modo B no se revisó de nuevo como cierre. Sigue parcial. No es doble firma. No se cierra I-22. No se reabre E3.

### I-23 — Float paths y continuidad de E3, siguen abiertos

Multiple float paths y la continuidad desde la fecha de corte siguen sin implementarse en lo que E3 dejó abierto. Esta revisión no los cierra. No se cierra I-23.

### I-24 — WBS requerida de E3, sigue abierta

La WBS requerida de R-326 sigue sin implementarse. Esta revisión no la agrega. No se cierra I-24.

### I-25 — G4 de E4 incumple 8.1

Estado: abierto. Sigue importante. El gate lo deja en fail, igual que el ciclo 1. No se marca pass. No se baja el umbral. `ciclo2.md` no lo toca. Las seis cifras de paquete son las mismas.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. La línea base de la sección 10.2 no aplica a E4. Perdona G4 solo en E0.

Siguen bajo el umbral:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

El modelo en 100.0 / 100.0 no está en el texto de fail y no cierra el hallazgo. El resto, líneas 89.8, está sobre el 80 % y no compensa. Las ramas 76.8 del resto no están en el texto de fail. cobertura_total 89.5 y el TOTAL 86 % de la tabla (4102, 431, 1594, 324) no dejan el control en pass. «205 passed, 4 deselected in 19.00s» es la duración de esta suite, no un cumplimiento de 8.1. El paso de 19.64 s a 19.00 s no mueve las cifras.

### I-26 — G13 de E4 no está medido

Estado: abierto. Sigue importante. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa.

`docs/qa/E4/sabotaje.md` no existe. El detalle de G13 es «no medido: falta el informe de qa-sabotaje». Sin informe no hay cifra de esta etapa que comparar con 8.3. No medido no es un pase. No se inventa un kill score. No se usa el de E1 como score de este gate. No se usa el «no medido» de E2 ni el de E3 para declarar este control cumplido. No se rehace la mutación. `ciclo2.md` dice que no se copia un kill score.

### I-27 — El tornado no recorta al cono

Estado: abierto. Sigue importante. Desviación de M5, de B-07 y de R-041 / R-168. No es una aproximación silenciosa: la frase ya estaba en las aproximaciones. El requisito igual no está cumplido.

M5 pide que el atraso determinístico recalcule solo el cono de sucesoras afectado. B-07 pide que el tornado recalcule solo el cono afectado. R-041 y R-168 piden el cono y el conteo de actividades recalculadas.

`ciclo2.md` no lo integra. Dice que un cono mal definido reprogramaría una red distinta y podría mover el término por haber borrado actividades. No integrar ese recorte no cumple el requisito y no crea un resultado numérico incorrecto: no hay un cono integrado que medir. No se abre un crítico por un cambio que no entró.

Qué había en el ciclo 1, y sigue, porque no hay diff en `src/` ni en `tests/`:

- `_tornado` recorre las actividades y, por cada una, llama a `schedule_cpm` con la duración remanente atrasada.
- La nota dice que reprograma el cronograma completo por cada actividad y que no recorta al cono de sucesoras.
- `tests/test_e4_tornado.py` afirma esa nota. No afirma un recorte ni un conteo de recalculadas menor que la red.
- El tornado de 30 000 no se corrió. No se proyecta como cumplimiento.

G10 queda en pass porque el archivo de test existe. El test no prueba el cono. No se marca B-07 cerrado. No es doble firma.

### I-28 — No hay curva por periodo

Estado: abierto. Sigue importante. Desviación de M6 y de B-13. No es una aproximación silenciosa: las notas lo dicen. El requisito igual no está cumplido. No es un resultado numérico que el test dé por curva.

M6 pide distribución temporal por día, semana o mes, histogramas, sobreasignación, curvas S de baseline, plan y real, y EVM a la fecha de corte. B-13 pide esas funciones, `fact_timephased` poblado y los supuestos como aproximación. R-043 y R-169 citan `tests/test_e4_spreads.py`. La fila E4 de 10.2 pide además EVM y curvas S contra esperados con doble firma.

`ciclo2.md` lo deja igual: la curva por periodo, el histograma y la sobreasignación siguen sin implementarse. `fact_timephased` queda en el balde corte.

Qué había en el ciclo 1, y sigue, porque no hay diff de producto:

- `spread_hours` es la duración remanente. `write_star` la guarda en el balde `corte`.
- El test espera las horas remanentes de A y de B en ese único balde, y afirma que no es una curva por periodo.
- La tabla `scurve` tiene un solo punto, en la fecha de corte.
- El PV sigue siendo lineal. La nota dice que no hay curva de recurso.
- El límite de recurso queda no evaluable. No hay histograma ni sobreasignación.
- Lo que el test afirma es lo que el código escribe. No es un esperado independiente. No es doble firma.

G10 queda en pass porque el archivo existe. No prueba la distribución por periodo. No se marca B-13 cerrado. QC-2 sigue incompleto. No se inventa un oráculo de P6.

### I-29 — La meta de 5 minutos no está cumplida

Estado: abierto. Sigue importante. Desviación de la sección 11, de la fila E4 de 10.2 y de B-07 / R-040 / R-303. No es un crítico: no hay una corrida de 1 000 iteraciones medida por encima de 5 minutos. No hay crítico de un tiempo de 1 000 iteraciones, porque no se midió.

La sección 11 pide Monte Carlo de 1 000 iteraciones y 30 000 actividades bajo 5 minutos, medido con `gen_scale.py`. «No medido» nunca equivale a cumplido. G6 falla si un criterio medible de la etapa supera su meta. Un pass de G6 no convierte lo no medido en cumplido.

Qué está medido, y no es la meta:

- Un CPM de 30 000 actividades, `series=False`, en este equipo el 2026-10-21: 9.401 s. Es una llamada a `schedule_cpm`. No es Monte Carlo. No está por encima de 5 minutos. `ciclo2.md` repite esa cifra y no corre las 1 000.
- `tests/perf/test_montecarlo.py` corre 4 iteraciones de dos actividades y exige menos de 30 s. El docstring dice que no es el criterio de 30 000 por 1 000. G6 registra 4 passed in 3.90 s. En el ciclo 1 eran 4.01 s. El reloj no es la meta.

Qué no está medido:

- Monte Carlo de 30 000 por 1 000 no se corrió. La proyección 1 000 × 9.401 s son unas 2,6 h. No es una medición y no cumple 5 minutos. No se anota como crítico de tiempo superado.
- El tornado de 30 000 no se corrió. El recorte que falta está en I-27.
- numba no está cargado. `ciclo2.md` no afirma una wheel que deje el resultado bajo 5 minutos. No es, por sí solo, la cifra de 5 minutos. Tampoco es una vía que esta evidencia muestre cumpliendo la sección 11.

No se marca el criterio como pase. No se inventa el tiempo de 30 000 por 1 000.

## Menor

No bloquean. No autorizan el cierre.

### M-20 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest`. Igual que el ciclo 1.

### M-21 — G6 en verde no es la meta de 5 minutos

Pass: 4 passed in 3.90 s. En el ciclo 1 eran 4.01 s. El test de perf cronometra 4 iteraciones de dos actividades. El 9.401 s está en `perf.md`, no en el detalle de G6. No es un fail de G6, no es un crítico de rendimiento y no acredita I-29. El reloj más corto no cumple los 5 minutos.

### M-22 — G12 no compara tiempos

Pass: tests 205 frente a 201. `"benchmarks": {}`. cobertura_total 89.5 no declara G4 en pass. No acredita la meta de 5 minutos. Las seis cifras de I-25 no se mueven. El cambio de 19.64 s a 19.00 s no es un benchmark de G12.

### M-23 — `gate.md` corta el detalle

`gate.md` no cambió respecto del ciclo 1. La línea de G4 se corta en «engine ramas 79.». La de G6 se queda en la barra. Las cifras completas están en `gate.json`, incluido el reloj de 19.00 s, el resto en 89.8 / 76.8 y G6 en 3.90 s. No cambia I-25 ni el fail.

### M-24 — La cita corregida del invariante no es doble firma

La lectura del ciclo 1 sigue, porque `docs/qa/TRAZABILIDAD.md` no está en el diff: R-042 cita `tests/property/test_invariant_e.py`. El archivo ya estaba. La corrección de la cita no es doble firma, no es un oráculo independiente y no cierra I-29, I-27 ni B-07. El contrato no se reescribió. No cambia las cifras.

## Gate

Exit code 1. test_count 205. Cobertura citada por el control: 89.5. El gate repite el ciclo 1 en los controles y en las seis cifras. Rechazo 2 de 3. La etapa no queda bloqueada. No se bajan umbrales. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-20 |
| G4 | fail | I-25. Mismas seis cifras: calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. cobertura_total 89.5. Suite en 19.00 s. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a–e con perfil qa. El invariante e no es doble firma. Ver M-24 |
| G6 | pass | 4 passed in 3.90 s. No es 30 000 por 1 000. Ver M-21 e I-29. No es un crítico |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 13 requisitos citan un archivo que existe. No es el cono, no es la curva por periodo y no es la meta de 5 minutos |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | 205 frente a 201. Ver M-22 |
| G13 | fail | I-26. No medido. No se inventa un score y no se copia el de E1 |
