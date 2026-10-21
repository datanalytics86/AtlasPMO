# Hallazgos E5 — ciclo 2

Revisión de QC-6 sobre `docs/qa/E5/gate.md`, `docs/qa/E5/gate.json` (exit_code 1, test_count 210, coverage_percent 89.7), `docs/qa/E5/ciclo2.md`, `docs/qa/E5/QC1_contrato.md`, `tests/test_e5_ui.py`, `tests/test_e5_manifest.py` y `src/atlaspmo/ui/app.py`. HEAD `056866e3a3f7aac6d2ee81a6da46080c7d788ea5` (`test(qa): gate E5 ciclo 2, salida 1 (B-01)`). Ese commit actualiza el gate y toca `docs/ESTADO.md`. Esta revisión no editó ese archivo. La pantalla de este ciclo está en `0d387b4`, junto con `docs/qa/E5/ciclo2.md`. El contrato es `6498d00`, anterior al código. No se reejecutó pytest, el gate ni la mutación. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó código de producto, el gate, umbrales, skips ni oráculos. No se abrió un navegador. La evidencia de la pantalla es el fuente de AppTest y de `app.py`.

Este es el rechazo 2 de 3. La etapa no queda bloqueada. No es el tercer rechazo. Esta revisión no la marca bloqueada. El orquestador cambia el estado solo después del tercer rechazo. Queda un ciclo dentro del tope de tres. No hay cuarto ciclo. No se bajan umbrales. No se copia un kill score.

La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. El gate está en rojo. La línea base de la sección 10.2 vale solo para E0. G4 y G13 en fail no se marcan pass. El cierre no cabe. No se reabren E0, E1, E2, E3 ni E4.

## Contraste

`docs/qa/E5/gate.md` sale 1. Pass: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. Fail: G4 y G13. Las cifras completas están en `gate.json`. En `gate.md` la línea de G4 se corta en «engine ramas 79.» y la de G6 se queda en la barra.

G4, bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.7. En `gate.json` el modelo está en 100.0 / 100.0. El resto está en líneas 90.1 y ramas 78.2. El TOTAL de la tabla es 86 % (4197, 432, 1618, 316). «210 passed, 4 deselected in 22.56s» es la duración de esta suite. El umbral de 8.1 es 90 % de líneas y 85 % de ramas en esos paquetes, y 80 % de líneas en el resto. El resto, en líneas, está sobre el 80 % y no compensa. La línea base no perdona G4 en E5. Las seis cifras del fail no cruzan el umbral.

G6 en `gate.json`: 4 passed in 3.84 s. G10: 5 requisitos de E5 citan un archivo de test que existe. El verde de la suite lo mide G3. G12: tests 210 frente a 205. `"benchmarks": {}`.

G13: «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E5/sabotaje.md`. No hay kill score de esta etapa. No se inventa uno. No se copia el de otra etapa. No se rehace la mutación.

G8 en pass: «sin cronogramas fuera de fixtures, sin rutas de perfil, sin red». Es el control estático del gate. No es un socket abierto contra un proceso de la app.

`docs/qa/E5/ciclo2.md` dice que la pantalla ofrece PDF, un zip Parquet, el manifiesto y, cuando el módulo trae tabla CPM, el visor de `gantt_figure`; que `minimal.xer` no trae fecha de corte; que el lote llama a `run_folder`; y que nada de eso recalcula fechas en la UI. El fuente sostiene el corte, con el límite de abajo. No sostiene el e2e completo.

La UI arma los resultados con `run_selected` y el lote con `run_folder`. El visor llama a `gantt_figure` sobre la tabla que ya trae el módulo. `gantt_figure` dibuja barras con `early_start` y `early_finish`. No llama al motor. El ancho de la barra es de presentación. La UI no recalcula fechas. El docstring de `app.py` dice que la pantalla no calcula el cronograma.

`test_load_run_and_show_approximations` carga `tests/fixtures/synthetic/minimal.xer`, elige Calidad, pulsa Ejecutar y exige el subtítulo `quality`, más de dos captions, el texto «no hay Gantt» y estos cuatro rótulos: «Exportar Excel», «Exportar PDF», «Exportar Parquet» y «Exportar manifiesto». No exige los bytes de esos botones.

`minimal.xer` trae en PROJECT `proj_id`, `proj_short_name` y `clndr_id`. No trae `last_recalc_date`. La pantalla, en esa corrida, escribe «Esta corrida no trae tabla CPM, así que no hay Gantt.» No escribe «no hay fecha de corte». Calidad entrega `tables={}`. El motor, si no hay `last_recalc_date`, devuelve un CPM sin filas y anota «No hay fecha de corte (last_recalc_date).» Esa nota no es el caption que la prueba afirma. Las tres frases no son la misma. El visor no se cierra con este sintético.

`test_mode_b_shows_the_cpm_gantt` arma `case.xer` con `_load`, `_task` y `_link` de `tests/test_cpm.py`. `_load` escribe `last_recalc_date` (por defecto `2026-01-05 08:00`) y un calendario. Elige «Ruta crítica (modo B)», pulsa Ejecutar y exige `plotly_chart` y «No recalcula fechas». Es AppTest. No se abrió un navegador. En `app.py` el chart sale solo si la tabla `cpm` no está vacía y tiene `task_code`, `early_start` y `early_finish`.

`test_batch_ranks_one_synthetic` copia `minimal.xer` a un temporal, escribe la ruta en «Carpeta de lote» y pulsa el segundo botón. Exige `minimal.xer` en el dataframe. En `app.py` ese botón llama a `run_folder(folder)` sin los módulos del multiselect. `run_folder` usa `["quality"]` si no recibe ids. La pantalla muestra `archivo` e `indice`. No llama a `write_ranking`. No hay Excel consolidado del lote.

Siguen fuera del fuente de la pantalla: selector de perfil, barra de progreso, pestañas y biblioteca. `run_selected` se llama sin `configs`. No hay `st.progress`, ni `st.tabs`, ni DuckDB. Eso no es el e2e completo de B-01.

El mismo test de carga exige «baseline no se asocia». `app.py` escribe «El baseline no se asocia en esta pantalla.» El lote añade «No asocia un baseline.» La prueba confirma la ausencia. No asocia un baseline. R-120, en `docs/qa/TRAZABILIDAD.md`, sigue como no implementado y no está en verde. El contrato dice que no se va a marcar en verde.

`test_localhost_config_disables_usage_stats` lee `.streamlit/config.toml` como texto. Afirma las cadenas `address = "localhost"` y `gatherUsageStats = false`. El archivo las tiene, la primera bajo `[server]` y la segunda bajo `[browser]`. No abre un socket. No demuestra que un proceso esté escuchando. R-051 pide que la app escuche en localhost y no envíe estadísticas. La fila E5 de 10.2 pide que la app solo escuche en localhost, con test. Leer la configuración no es esa prueba.

Las aproximaciones se pintan: `app.py` recorre `result.approximations` y llama a `st.caption`. El test de Calidad solo exige más de dos captions, además de frases fijas de la pantalla. No cita el texto de una aproximación. No se usa ese conteo para declarar R-104 cerrado.

`tests/test_e5_manifest.py` no es una corrida de la UI. Copia el sintético a un temporal, llama a `run_selected` con `quality`, escribe `run_manifest.json` y compara los bytes de la entrada antes y después. Exige `input_name`, un `input_sha256`, el módulo `quality`, que `excel_bytes` y el zip Parquet empiecen con `PK`, que `pdf_bytes` empiece con `%PDF`, y que `manifest_bytes` repita el nombre y el hash. Eso es lo que el fuente afirma. G3 en verde no convierte esas funciones en el e2e. El botón de la pantalla no se pulsa en AppTest.

`docs/qa/E5/QC1_contrato.md` se escribió antes del código. Deja el visor, el lote, PDF y Parquet fuera hasta que una prueba los ejercite. Esas pruebas ahora están en el árbol. Ejercer una parte no cumple el e2e. El contrato deja los resultados condicionales a I-3 y a E0, E1, E2, E3 y E4 en el estado de su tercer rechazo. Esta revisión no les cambia el estado. No se leyeron datos reales. No se bajaron umbrales.

## Crítico

No hay críticos. No hay un resultado numérico medido que esta evidencia deje en incorrecto, ni una llamada de red observada.

No hay crítico de telemetría medida. `.streamlit/config.toml` deja `gatherUsageStats = false` y `address = "localhost"`. G8 informa sin red. No se observó una red. No se abrió un navegador ni un socket. Eso no es una violación medida. Tampoco cierra R-051 como prueba de proceso: falta demostrar que un proceso escucha, y solo escucha, en localhost. La brecha queda en I-34. No se abre un crítico por un tráfico que esta evidencia no trae.

G13 no está medido. Sin informe no hay kill score que comparar con 8.3. No se inventa un score y no se copia el de otra etapa. No medido no es un pase y no es un crítico de un score que esta evidencia no trae. Va en I-31.

El e2e incompleto no se trata como un número incorrecto. La pantalla carga, ejecuta Calidad, ofrece cuatro descargas, dibuja un Gantt cuando el módulo trae la tabla CPM y rankea una carpeta. Lo que falta es de spec. Va en I-32.

El baseline no asociado no es un cálculo falso. La pantalla dice que no se asocia y el test lo repite. R-120 sigue fuera de verde. Va en I-33.

## Importante

Abiertos. Bloquean el cierre. Ninguno se cierra en este ciclo.

No se cierran, no se reabren, y E5 queda condicional a ellos: I-3 y los de E1 a E4 (I-11 a I-29). E0, E1, E2, E3 y E4 siguen en el estado de su tercer rechazo, sin cuarto ciclo. Esta revisión no les cambia el estado y no marca E5 bloqueada. Los resultados de E5 quedan condicionales a I-3 y a esos bloqueos.

De E5, abiertos: I-30 (G4), I-31 (G13), I-32 (e2e incompleto), I-33 (baseline no asociado) e I-34 (localhost sin socket).

### I-3 — Heredado de E0, sigue abierto

R-198 no se releyó. No se cierra I-3. No se reabre E0. El contrato de E5 condiciona la etapa a ese hallazgo.

### I-11 a I-14 — E1, siguen abiertos

No son el fail de este gate. No se reescribe G4 de E1 con las cifras de E5. No se copia un kill score de E1 como resultado de este G13. No se cierra I-11, I-12, I-13 ni I-14. No se reabre E1. La lectura de este gate es I-30 e I-31.

### I-15 a I-18 — E2, siguen abiertos

No se reabren. No se cierran I-15, I-16, I-17 ni I-18. E2 no aporta un kill score a este gate. La confirmación de 30 000 no se midió de nuevo.

### I-19 a I-24 — E3, siguen abiertos

No se reabre E3. No se cierran I-19, I-20, I-21, I-22, I-23 ni I-24. La doble firma, la cadena driving, float paths, la continuidad y la WBS requerida no se revisaron como cierre de E5.

### I-25 a I-29 — E4, siguen abiertos

No se reabre E4. No se cierran I-25, I-26, I-27, I-28 ni I-29. Las seis cifras de paquete de este G4 coinciden con las que I-25 dejó bajo 8.1. No se usan para cerrar I-25. La lectura de este gate es I-30. G13 de E5 es I-31, no un cierre de I-26. El cono, la curva por periodo y la meta de 5 minutos no se midieron de nuevo y no se dan por cumplidos.

### I-30 — G4 de E5 incumple 8.1

Estado: abierto. Importante. El gate lo deja en fail. No se marca pass. No se baja el umbral. La línea base de la sección 10.2 no aplica: perdona G4 solo en E0.

8.1 pide, con `--cov-branch`, al menos 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y al menos 80 % de líneas en el resto.

Siguen bajo el umbral:

- calendars líneas 85.2 < 90; ramas 70.9 < 85
- engine líneas 89.4 < 90; ramas 79.5 < 85
- logic líneas 88.6 < 90; ramas 75.3 < 85

El modelo en 100.0 / 100.0 no está en el texto de fail y no cierra el hallazgo. El resto, líneas 90.1, está sobre el 80 %. Las ramas 78.2 del resto no están en el texto de fail. Ninguno de los dos compensa los tres paquetes. cobertura_total 89.7 y el TOTAL 86 % de la tabla (4197, 432, 1618, 316) no dejan el control en pass. «210 passed, 4 deselected in 22.56s» es la duración de esta suite, no un cumplimiento de 8.1. Este ciclo no mueve esas seis cifras sobre el umbral.

### I-31 — G13 de E5 no está medido

Estado: abierto. Importante. El gate lo deja en fail. No se marca pass. No hay kill score de esta etapa.

`docs/qa/E5/sabotaje.md` no existe. El detalle de G13 es «no medido: falta el informe de qa-sabotaje». Sin informe no hay cifra de esta etapa que comparar con 8.3. No medido no es un pase. No se inventa un kill score. No se usa el de otra etapa como score de este gate. No se usa el «no medido» de E2, E3 o E4 para declarar este control cumplido. No se rehace la mutación.

### I-32 — El e2e de B-01 no está completo

Estado: abierto. Importante. Desviación de B-01, de la fila E5 de 10.2 y de la sección 6 (Transversales). El corte de `0d387b4` no es el flujo que B-01 dice cubrir. No es una aproximación silenciosa de un número.

B-01 pide un AppTest que cargue un sintético, muestre resumen y validación, elija módulos, configure con perfil, ejecute con progreso, abra pestañas y exporte Excel, PDF, Parquet y manifiesto, más el visor Gantt y el modo lote. La fila E5 pide ese e2e completo en verde, y lote y biblioteca desde la UI. La sección 6 pide los siete pasos de la pantalla, el visor con ruta crítica, bandas de holgura y filtros, el lote con los módulos elegidos y un Excel consolidado, y la biblioteca DuckDB. R-050 cita `tests/test_e5_ui.py`.

Qué parte del corte existe:

- Carga `minimal.xer` por el file uploader de AppTest. El resumen visible es el conteo de actividades.
- Elige «Calidad (DCMA y GAO)» y pulsa Ejecutar. Ve el subtítulo `quality`.
- Si hay resultados de `run_selected`, ofrece «Exportar Excel», «Exportar PDF», «Exportar Parquet» (`atlaspmo-star.zip`, `parquet_zip_bytes`) y «Exportar manifiesto». El test de pantalla exige los cuatro rótulos. No exige los bytes. `tests/test_e5_manifest.py` exige `%PDF`, `PK` y el JSON del manifiesto por función, no por un clic en AppTest. Los bytes de la entrada no cambian en esa prueba. La UI no recalcula fechas: exporta `results`.
- Visor Plotly solo si `tables["cpm"]` no está vacía y tiene `task_code`, `early_start` y `early_finish`. El caption dice que el visor usa la tabla del módulo y no recalcula fechas. `gantt_figure` dibuja una barra por código. `test_mode_b_shows_the_cpm_gantt` lo exige con AppTest sobre un XER de `_load` en `tests/test_cpm.py`, que sí escribe `last_recalc_date` y un calendario. No se abrió un navegador.
- `minimal.xer` no trae `last_recalc_date`. La corrida de Calidad exige «no hay Gantt». La pantalla dice «Esta corrida no trae tabla CPM, así que no hay Gantt.» Calidad no entrega tabla `cpm`. La pantalla no dice que falte la fecha de corte. El motor, sin esa fecha, no arma filas de CPM. Esa nota no es el texto de la prueba. El visor no queda demostrado con `minimal.xer`.
- Lote: «Carpeta de lote» y «Correr lote» llaman a `run_folder` sobre la carpeta. La prueba ve `minimal.xer` en el dataframe de `archivo` e `indice`. El caption dice que el lote no asocia un baseline.

Qué parte no existe, y por eso el e2e sigue abierto:

- Perfil en la pantalla. No hay selector. `run_selected` va sin `configs`.
- Barra de progreso. No hay `st.progress`.
- Pestañas de resultados. Hay un `st.subheader` por módulo, no `st.tabs`.
- Biblioteca desde la UI. No hay DuckDB.
- El lote no recibe los módulos elegidos. `run_folder` cae en `["quality"]`. No hay Excel consolidado: la pantalla no llama a `write_ranking`.
- El visor no filtra por WBS o código, no marca la ruta crítica, no dibuja bandas de holgura y no traza predecesoras ni la cadena driving. La tabla `driving_chain` del modo B no se muestra.
- No hay botón «Informe completo». Los PDF y el Excel van separados.
- No hay panel de validación aparte del conteo y de los captions.
- El baseline no se asocia. Va en I-33. La prueba de localhost no abre un socket. Va en I-34.

G10 queda en pass porque el archivo de test existe. Existir no es el e2e. No se marca B-01 cerrado.

El conteo de captions no cita una aproximación. El código sí las pinta con `st.caption`. No se marca R-104 en verde por `len(app.caption) > 2`. No se abre otro importante: la brecha que bloquea es el e2e incompleto.

### I-33 — El baseline no se asocia

Estado: abierto. Importante. Desviación de R-120 y de la sección 5. No está en verde. El contrato ya lo decía. Decirlo no lo cumple.

`app.py` escribe «El baseline no se asocia en esta pantalla.» `test_load_run_and_show_approximations` exige esa frase en los captions. El lote escribe «No asocia un baseline.» La prueba demuestra que la pantalla avisa. No demuestra que el usuario asocie un baseline. No hay control para elegirlo. `AnalysisContext` de la pantalla no lleva baseline. R-120 sigue fuera de verde. No se marca pass.

### I-34 — La prueba de localhost no abre un socket

Estado: abierto. Importante. Desviación de R-051 y de la fila E5 de 10.2. El test no prueba lo que el requisito dice. No es un crítico de telemetría medida.

R-051 pide que la app escuche en localhost y no envíe estadísticas. La fila E5 pide que solo escuche en localhost, con test. La sección 2 pide `server.address = "localhost"` y `browser.gatherUsageStats = false`, y una app sin red y sin telemetría.

Qué hay:

- `.streamlit/config.toml` tiene `address = "localhost"` bajo `[server]` y `gatherUsageStats = false` bajo `[browser]`.
- El test lee ese archivo y busca las dos cadenas. No importa `socket`. No abre un puerto. No arranca `streamlit run`. No demuestra que un proceso esté escuchando.
- G8 en pass informa sin red. Es un control estático. No es la observación de un proceso.
- No se abrió un navegador. No se observó una red. La configuración apaga las estadísticas de uso. No hay crítico de telemetría medida.

Qué no cierra el requisito: una prueba de proceso. Leer el archivo no demuestra que la app escuche, ni que escuche solo en localhost. No se marca R-051 en verde. No se marca pass por el texto de la configuración ni por G8.

## Menor

No bloquean. No autorizan el cierre.

### M-25 — G3 no corrió `uv run pytest`

El detalle dice que no arranca (ADR-004) y que corrió `python -m pytest` con exit 0. El pass no afirma el comando `uv run pytest`. No cierra I-30 ni I-32.

### M-26 — G6 en verde no es el e2e

Pass: 4 passed in 3.84 s. No es la fila E5 de 10.2. No acredita I-32 ni I-34. No es un fail de G6 y no es un crítico.

### M-27 — G10 cita archivos, no el flujo

Pass: 5 requisitos de E5 citan un archivo de test que existe. El verde de la suite lo mide G3. Los tests de este ciclo tocan rótulos de descarga, un `plotly_chart` y un dataframe de lote. No comprueban perfil, progreso, pestañas, biblioteca, el baseline ni un socket. No acredita I-32, I-33 ni I-34.

### M-28 — G8 «sin red» no es un socket

Pass: sin cronogramas fuera de fixtures, sin rutas de perfil, sin red. No abre un puerto. No reemplaza a I-34. No es un crítico de telemetría: no se observó una red y la configuración apaga las estadísticas.

### M-29 — `gate.md` corta el detalle

La línea de G4 se corta en «engine ramas 79.». La de G6 se queda en la barra. Las cifras completas están en `gate.json`: calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3, cobertura_total 89.7, resto 90.1 / 78.2, modelo 100.0 / 100.0, TOTAL 86 % y G6 en 3.84 s. No cambia I-30 ni el fail.

### M-30 — G12 no compara el e2e

Pass: tests 210 frente a 205. `"benchmarks": {}`. El aumento no declara G4 en pass y no acredita B-01. La cobertura_total 89.7 no perdona 8.1.

## Gate

Exit code 1. test_count 210. Cobertura citada por el control: 89.7. Rechazo 2 de 3. Esta revisión no marca la etapa bloqueada. No se bajan umbrales. La etapa no se cierra.

| Control | Estado | Lectura |
|---|---|---|
| G1 | pass | ruff check y ruff format --check en verde |
| G2 | pass | mypy src sin errores |
| G3 | pass | `python -m pytest` exit 0. Ver M-25 |
| G4 | fail | I-30. calendars 85.2 / 70.9, engine 89.4 / 79.5, logic 88.6 / 75.3. cobertura_total 89.7. La línea base de 10.2 no aplica |
| G5 | pass | invariantes a–e con perfil qa. No cierra el e2e |
| G6 | pass | 4 passed in 3.84 s. No es B-01. Ver M-26 |
| G7 | pass | no hay skip ni xfail |
| G8 | pass | sin cronogramas fuera de fixtures, sin rutas de perfil, sin red. No es un socket. Ver M-28 e I-34. No es un crítico de telemetría |
| G9 | pass | tablas y campos literales de src/ están en `XER_SPEC.md` |
| G10 | pass | 5 requisitos de E5 citan un archivo que existe. Ver M-27. No es el e2e |
| G11 | pass | cambios protegidos citan un ADR |
| G12 | pass | tests 210 frente a 205. Ver M-30 |
| G13 | fail | I-31. No medido: falta el informe de qa-sabotaje. No hay kill score. No se copia uno |
