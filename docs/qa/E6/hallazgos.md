# Hallazgos E6 — ciclo 1

Revisión de QC-6 sobre `docs/qa/E6/gate.md`, `docs/qa/E6/gate.json` (exit_code 1, test_count 216, coverage_percent 89.8), `docs/qa/E6/QC1_contrato.md`, `tests/test_e6_trends.py`, `tests/test_e6_skips.py`, `tests/test_e6_conformance.py` y el cambio de `docs/MANUAL_USUARIO.md` en `e47f8c1`. Contraste con las secciones 8, 10.2 y 11 de `docs/MEGAPROMPT_v2.md`. HEAD `d75593cdd1c58b02a4c7fb08028d33a0fcfb322a` (`test(qa): gate E6 ciclo 1, salida 1 (B-16)`). Ese commit agrega el gate y toca `docs/ESTADO.md`. Esta revisión no editó ese archivo. Las pruebas y el manual están en `e47f8c1` (`test(e6): tendencia, omision y conformidad no medida (B-16)`). El contrato es `0327903`, anterior al código. No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni un `ATLASPMO_GOLDEN_DIR` real. No se editó código de producto, el gate, umbrales, skips ni oráculos. No se abrió un navegador.

Este es el rechazo 1 de 3. La etapa no queda bloqueada. No es el tercer rechazo y esta revisión no la marca bloqueada. Cabe un ciclo de corrección. No se bajan umbrales. No se copia un kill score.

La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass. El cierre no cabe. No se reabren E0, E1, E2, E3, E4 ni E5.

## Contraste

`docs/qa/E6/gate.md` sale 1. Pass: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. Fail: G4 y G13. Las cifras completas están en `gate.json`. En `gate.md` la línea de G4 se corta en «engine ramas 79.» y la de G6 se queda en la barra.

G4, bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.8. En `gate.json` el modelo está en 100.0 / 100.0. El resto está en líneas 90.2 y ramas 78.5. El TOTAL de la tabla es 86 % (4256, 435, 1636, 317). «216 passed, 4 deselected in 26.70s» es la duración de esta suite. El umbral de 8.1 es 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y 80 % de líneas en el resto. El resto, en líneas, está sobre el 80 % y no compensa. La línea base no perdona G4 en E6. Las seis cifras del fail no cruzan el umbral. El detalle de I-35.

G6 en `gate.json`: 4 passed in 3.66 s. Es `pytest -m perf` sobre `tests/perf`, según `scripts/qa_gate.py`. No registra el equipo ni las metas de la sección 11. `"benchmarks": {}`. G6 en verde no es la sección 11 completa. La fila E6 de 10.2 pide todos los criterios automatizables de la sección 11 en verde y evidenciados. B-16 pide G6 en verde con `gen_scale.py`. Ese pass no sustituye las mediciones que faltan. El detalle está en I-37.

G10: 5 requisitos de E6 citan un archivo de test que existe. El verde de la suite lo mide G3. En el contrato son R-181, R-196, R-304, R-060 y R-180. Citar el archivo no mide la sección 11 ni una tendencia de cronogramas reales.

G12: tests 216 frente a 212. La subida no declara G4 en pass y no evidencia la sección 11.

G13: «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E6/sabotaje.md`. No hay kill score de esta etapa. No se inventa uno. No se copia el de otra etapa. No se rehace la mutación. 8.3 pide, en los módulos tocados, al menos 85 % en `engine`, `calendars` y `analysis/logic`, y al menos 70 % en el resto. La fila E6 de 10.2 pide G13 sobre todo `src/`. Sin informe no hay cifra que comparar. El detalle está en I-36.

G8 en pass: «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red». Es el control estático del gate. No abre un golden y no mide conformidad.

`docs/qa/E6/QC1_contrato.md` se escribió antes del código. Deja fuera de verde una tendencia de cronogramas reales, un `skip` nuevo, el 99,5 % y el 100 %, el resto de la sección 11, y una comparación contra P6. El manual no debe afirmar el e2e de B-01 ni un gate en verde. Los tests de `e47f8c1` coinciden con ese corte. Coincidir con el corte no cumple la fila E6 de 10.2 ni la sección 11. El contrato deja los resultados condicionales a I-3 y a E0, E1, E2, E3, E4 y E5 en el estado de su tercer rechazo. Esta revisión no les cambia el estado.

R-181. `tests/test_e6_trends.py` arma dos `ModuleResult` sintéticos, con `quality_index` 10 y 20 y los nombres `uno.xer` y `dos.xer`. No lee un XER. `Library.trend("quality_index")` devuelve `[(first, 10.0), (second, 20.0)]`. `Library.trend` ordena por `runs.seq`. Eso es el orden de inserción de dos puntos sintéticos. No es una tendencia de cronogramas reales. El contrato ya lo decía. No se marca R-181 en verde como esa tendencia. No se abre otro importante: no hay una afirmación de tendencia real puesta en verde. G10 no la crea.

R-196. `tests/test_e6_skips.py` lee `docs/qa/skips.toml` y exige el encabezado y los motivos `dependencia_opcional`, `fixture_nicolas` y `plataforma`. No escribe el archivo. `e47f8c1` no toca `skips.toml`. La otra prueba renombra `tests/fixtures/p6_verified` a `p6_verified_aside`, llama a `main([])`, exige `p6_verified: omitido` y restaura la carpeta en `finally`. En el árbol, esa carpeta solo tiene `.gitkeep`. No agrega un `skip` ni un `xfail`. G7 en pass («no hay skip ni xfail») concuerda con eso. No es un `skip` nuevo.

R-304. `tests/test_e6_conformance.py` borra `ATLASPMO_GOLDEN_DIR` si estaba, llama a `main([])` y exige `golden: omitido`. Después crea una carpeta temporal con `secreto.xer` en bytes `SECRET`, apunta la variable ahí, y exige el texto `esta corrida no abre esa carpeta`, que la salida no contenga `secreto` y que los bytes sigan iguales. El tramo del fuente posterior a `os.environ.get("ATLASPMO_GOLDEN_DIR")` no usa `iterdir`, `listdir`, `scandir`, `glob` ni `read_`. `scripts/run_conformance.py` imprime `golden: omitido` si la variable falta, y si está definida imprime que esta corrida no abre esa carpeta. No calcula un 99,5 % ni un 100 %. No es un pase de la sección 11. La conformidad contra P6 no se puede correr aquí. No se leyó un golden real.

R-180. El contrato lo deja en `tests/test_phase4.py::test_compare_reports_the_hand_differences` y dice que no se reescribe y que no es una comparación contra P6. Esta revisión no lo reescribió y no lo marca como conformidad con P6.

R-060. Sigue en `tests/perf/test_scale.py`. La lectura de 30 000 ya midió 0.197 s en E1. El contrato dice que eso no cubre el resto de la sección 11. G6 de este gate tampoco.

El manual en `e47f8c1` describe la pantalla que hay y sus límites. Carga un XER, elige módulos y un perfil de calidad, y parte resultados y exportaciones. El visor aparece solo si el módulo trae una tabla CPM con inicio y fin tempranos. El baseline no se asocia. No hay avance parcial: la barra se llena al terminar. No hay bandas de holgura ni filtro por WBS. No se abrió un navegador para escribirlo. La evidencia que el propio manual cita es AppTest, en `tests/test_e5_ui.py`. Dice que no se contrastó con P6, que no se midió Monte Carlo de 30 000 por 1 000, y que el checklist de reimportación no se ejecutó. No afirma el e2e de B-01 ni un gate en verde. Describir límites no cierra B-01. I-32 sigue abierto.

Los commits de este ciclo (`0327903`, `e47f8c1`, `d75593c`) no tocan `docs/VALIDACIONES_PENDIENTES.md`. El checklist final de la fila E6 de 10.2 no está en esta entrega. No se marca cumplido. No cierra I-37. Va en M-36.

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni un criterio de la sección 11 medido por encima de su meta.

No hay crítico de un tiempo de confirmación de 30 000 medido por encima de 3 minutos, porque la confirmación no se corrió. No hay crítico de un Monte Carlo de 30 000 por 1 000 medido por encima de 5 minutos, porque no se corrió. La proyección de unas 2,6 h no es una medición. No se abre un crítico de un tiempo que esta evidencia no trae. El criterio igual no está cumplido. Va en I-37.

8.5 nombra un criterio de la sección 11 incumplido entre lo crítico. La sección 11 dice que no medido nunca equivale a cumplido. G6 falla si un criterio medible de la etapa supera su meta. Aquí no hay una superación medida en el detalle de G6. No se abre un crítico de un tiempo que esta evidencia no trae. No se marca la sección 11 en verde.

G13 no está medido. Sin informe no hay kill score que comparar con 8.3. No se inventa un score y no se copia el de otra etapa. No medido no es un pase y no es un crítico de un score que esta evidencia no trae. Va en I-36.

La lectura de 0.197 s está bajo 15 s. No se usa para abrir un crítico de esa meta, ni para dar por cumplido el resto.

## Importante

Abiertos. Bloquean el cierre. Ninguno se cierra en este ciclo.

No se cierran, no se reabren, y E6 queda condicional a ellos: I-3 y los de E1 a E5 (I-11 a I-34). E0, E1, E2, E3, E4 y E5 siguen en el estado de su tercer rechazo, sin cuarto ciclo. Esta revisión no les cambia el estado y no marca E6 bloqueada. Los resultados de E6 quedan condicionales a I-3 y a esos bloqueos.

De E6, abiertos: I-35 (G4), I-36 (G13) e I-37 (sección 11 no medida).

### I-3 — Heredado de E0, sigue abierto

R-198 no se releyó. No se cierra I-3. No se reabre E0. El contrato de E6 condiciona la etapa a ese hallazgo. R-304 no lo cierra: imprime que el golden se omite o que no se abre, y no es el 99,5 %.

### I-11 a I-14 — E1, siguen abiertos

No son el fail de este gate. No se reescribe G4 de E1 con las cifras de E6. No se copia un kill score de E1 como resultado de este G13. No se cierra I-11, I-12, I-13 ni I-14. No se reabre E1. La lectura de 0.197 s en `docs/qa/E1/perf.md` no se usa para cerrar esos hallazgos ni para completar la sección 11. La lectura de este gate es I-35 e I-36.

### I-15 a I-18 — E2, siguen abiertos

No se reabren. No se cierran I-15, I-16, I-17 ni I-18. E2 no aporta un kill score a este gate. El filtro de 0.345 s no es la confirmación. La confirmación de 30 000 no se midió de nuevo y no se da por cumplida.

### I-19 a I-24 — E3, siguen abiertos

No se reabre E3. No se cierran I-19, I-20, I-21, I-22, I-23 ni I-24. `evaluate` en 0.261 s, con CPLI `no_evaluable` en esa red, no cierra la doble firma, la cadena driving, float paths, la continuidad ni la WBS requerida. No es un pass de la definición de CPLI.

### I-25 a I-29 — E4, siguen abiertos

No se reabre E4. No se cierran I-25, I-26, I-27, I-28 ni I-29. Las seis cifras de paquete de este G4 coinciden con las que I-25 dejó bajo 8.1. No se usan para cerrar I-25. La lectura de este gate es I-35. G13 de E6 es I-36, no un cierre de I-26. El cono y la curva por periodo no se midieron de nuevo. Un CPM de 9.401 s no es Monte Carlo. La proyección de unas 2,6 h no cumple 5 minutos y no cierra I-29.

### I-30 a I-34 — E5, siguen abiertos

No se reabre E5. No se cierran I-30, I-31, I-32, I-33 ni I-34. Las seis cifras de este G4 son las de I-30. No se usan para cerrarlo. La lectura de este gate es I-35. G13 de E6 es I-36, no un cierre de I-31. El manual describe el mismo corte de pantalla: sin baseline, sin avance parcial, sin bandas de holgura y sin filtro por WBS, y sin un socket. Describirlo no cierra I-32, I-33 ni I-34. No se marca B-01 cerrado.

### I-35 — G4 de E6 incumple 8.1

Estado: abierto. Importante. El gate lo deja en fail. No se marca pass. No se baja el umbral. La línea base de la sección 10.2 no aplica: perdona G4 solo en E0.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto. G4 falla si se incumple 8.1 en cualquier paquete.

Siguen bajo el umbral:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

El modelo en 100.0 / 100.0 no está en el texto de fail y no cierra el hallazgo. El resto, líneas 90.2, está sobre el 80 %. Las ramas 78.5 del resto no están en el texto de fail. Ninguno de los dos compensa los tres paquetes. cobertura_total 89.8 y el TOTAL 86 % de la tabla (4256, 435, 1636, 317) no dejan el control en pass. «216 passed, 4 deselected in 26.70s» es la duración de esta suite, no un cumplimiento de 8.1.

### I-36 — G13 de E6 no está medido

Estado: abierto. Importante. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa.

`docs/qa/E6/sabotaje.md` no existe. El detalle de G13 es «no medido: falta el informe de qa-sabotaje». Sin informe no hay cifra de esta etapa que comparar con 8.3. No medido no es un pase. No se inventa un kill score. No se usa el de otra etapa como score de este gate. No se usa el «no medido» de E2, E3, E4 o E5 para declarar este control cumplido. No se rehace la mutación. No se copia un score.

La fila E6 de 10.2 pide G13 sobre todo `src/`. Esta entrega no lo evidencia. 8.3, en los módulos que la etapa toca, pide al menos 85 % en `engine`, `calendars` y `analysis/logic`, y al menos 70 % en el resto. Sin score no se puede decir que eso se cumpla, ni que falle por una cifra. Falla porque no está medido.

### I-37 — La sección 11 no está medida

Estado: abierto. Importante. Desviación de la sección 11, de la fila E6 de 10.2 y de R-060 / R-304. No es un crítico: no hay una medición de esta entrega que supere una meta. No medido no es cumplido, y tampoco es un tiempo medido por encima de la meta.

La sección 11 pide lectura de 30 000 bajo 15 s, DCMA y chequeos bajo 10 s, redundancia con confirmación bajo 3 min, Monte Carlo de 1 000 iteraciones y 30 000 actividades bajo 5 min, y conformidad de al menos 99,5 % en reales y 100 % en `p6_verified`, con el 100 % de las diferencias explicadas. Los criterios se miden con `scripts/gen_scale.py` y se registran en G6 con el equipo. «No medido» nunca equivale a cumplido. G6 falla si un criterio medible de la etapa supera su meta. Un pass de G6 no convierte lo no medido en cumplido.

Qué hay, y qué no cierra la sección:

- G6 de este gate: 4 passed in 3.66 s. No trae CPU, RAM ni SO. No cita una meta de la sección 11. `"benchmarks": {}`. No es la sección 11 completa.
- Lectura de 30 000. `docs/qa/E1/perf.md`: `gen_scale.py`, `series=False`, `read_xer` en 0.197 s, en Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise. Está bajo 15 s. Esta revisión no la reejecutó. No completa el resto de la sección 11. R-060 no queda en verde por esa cifra sola.
- DCMA. `docs/qa/E3/perf.md`: `evaluate` de calidad, sin baseline, 0.261 s, en la misma clase de red. El test cronometra solo `evaluate`. 0.261 s está bajo 10 s. No incluye el CPM. CPLI, dentro de esa llamada, queda `no_evaluable` si la red no trae un término crítico usable. Eso no es un pass de la definición de CPLI. No se reabre E3 para reescribirlo.
- Redundancia. `docs/qa/E2/perf.md`: el filtro de candidatos de 30 000 midió 0.345 s (24 998 candidatos sobre 69 996 vínculos). La confirmación de 30 000 no se corrió. El documento dice que no cumple los 3 minutos y que no es un pass. El test de perf cronometra solo el filtro. No se da por cumplida la confirmación. No se cierra I-17.
- Monte Carlo. `docs/qa/E4/perf.md`: un CPM de 30 000, una llamada a `schedule_cpm`, midió 9.401 s. No es Monte Carlo. Monte Carlo de 30 000 por 1 000 no se corrió. La proyección 1 000 × 9.401 s son unas 2,6 h. No es una medición y no cumple 5 minutos. El tornado de 30 000 no se corrió. No se cierra I-29.
- Conformidad contra P6. No se puede correr aquí. R-304 no imprime un porcentaje. El 99,5 % y el 100 % no están medidos. `p6_verified` solo tiene `.gitkeep`. El manual dice que no se contrastó con P6 y que el checklist de reimportación no se ejecutó. No es un pase de la sección 11.

La fila E6 de 10.2 no se cumple con este corte. No se marca la sección 11 en verde.

## Menor

No bloquean. No autorizan el cierre.

### M-31 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest`. No cierra I-35 ni I-37.

### M-32 — G6 en verde no es la sección 11

Pass: 4 passed in 3.66 s. No es la fila E6 de 10.2. No acredita I-37. No es un fail de G6 y no es un crítico. El 0.197 s, el 0.261 s, el 0.345 s y el 9.401 s están en los `perf.md` de E1 a E4, no en el detalle de este G6.

### M-33 — G10 cita archivos, no la sección 11

Pass: 5 requisitos de E6 citan un archivo de test que existe. El verde de la suite lo mide G3. Esos tests ordenan dos puntos sintéticos, leen el motivo de omisión, no abren el golden, apuntan a `tests/perf/test_scale.py` y dejan R-180 donde estaba. No miden el 99,5 %, el 100 %, la confirmación de 30 000 ni Monte Carlo de 30 000 por 1 000. No acreditan I-37. No convierten R-181 en una tendencia de cronogramas reales.

### M-34 — `gate.md` corta el detalle

La línea de G4 se corta en «engine ramas 79.». La de G6 se queda en la barra. Las cifras completas están en `gate.json`: calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3, cobertura_total 89.8, resto 90.2 / 78.5, modelo 100.0 / 100.0, TOTAL 86 % y G6 en 3.66 s. No cambia I-35 ni el fail.

### M-35 — G12 no mide la sección 11

Pass: tests 216 frente a 212. `"benchmarks": {}`. El aumento no declara G4 en pass. cobertura_total 89.8 no perdona 8.1. No acredita I-37.

### M-36 — El checklist final no está en esta entrega

La fila E6 de 10.2 pide el checklist final de `docs/VALIDACIONES_PENDIENTES.md`. Los commits de este ciclo no tocan ese archivo. Esta revisión no lo editó y no lo marca cumplido. No cierra I-37 ni los heredados.

## Gate

Exit code 1. test_count 216. Cobertura citada por el control: 89.8. Rechazo 1 de 3. Esta revisión no marca la etapa bloqueada. Cabe un ciclo de corrección. No se bajan umbrales. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-31 |
| G4 | fail | I-35. calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. cobertura_total 89.8. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a–e con perfil qa. No cierra la sección 11 |
| G6 | pass | 4 passed in 3.66 s. No es la sección 11. Ver M-32 e I-37 |
| G7 | pass | no hay skip ni xfail. R-196 no agrega uno |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red. No es conformidad con P6 |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 5 requisitos de E6 citan un archivo que existe. Ver M-33. No es la sección 11 |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | tests 216 frente a 212. Ver M-35 |
| G13 | fail | I-36. No medido: falta el informe de qa-sabotaje. No hay kill score. No se copia uno |
