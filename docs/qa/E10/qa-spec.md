RECHAZADO

# qa-spec — E10

Auditoría de QC-1 antes del código. Se contrastaron `docs/qa/E10/QC1_contrato.md` (HEAD `d38bdaa`, rama `v3`), las filas R-387 a R-396 de `docs/qa/TRAZABILIDAD.md`, las secciones 6 (M2, M6 y Transversales), 7, 8.4, 8.5 y 10.3 (párrafo E10) de `docs/MEGAPROMPT_v3.md`, y `docs/XER_SPEC.md` en TASK, TASKPRED, TASKRSRC y la nota de RSRCRATE. No se editó producto, tests, oráculos, el contrato ni `TRAZABILIDAD.md`. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se usó red. No se corrió la red de 30 000 ni el gate. El 4/3 y el 2/2 no se firmaron con `evaluate`.

Los tests `tests/test_e10_ui.py`, `tests/test_e10_paths.py`, `tests/test_e10_spread.py`, `tests/test_e10_edges.py` y `tests/test_e10_sign.py` no están en el árbol. Tampoco `tests/oracle/span_holiday.py` ni `tests/oracle/bei.py`. El contrato los deja fuera de verde. Eso no es rechazo.

## Requisitos

R-387: **sí.** La pantalla deja de decir «El baseline no se asocia en esta pantalla.» El BEI mostrado es el de `evaluate(actual, perfil, baseline)` sobre el par de sintéticos del test: el oráculo es esa función ya existente, no la UI nueva. El módulo que declara `RESOURCES` muestra «requiere recursos»; el que declara `TWO_VERSIONS` muestra «requiere dos versiones»; un módulo sin requisitos no muestra esa línea. Esos dos requisitos ya están en el código (`EvmModule` y el módulo de comparación). Tras ejecutar, `st.progress` queda en 1 y hay una pestaña por módulo corrido. «Informe completo» ofrece un binario que empieza con `PK` y otro que empieza con `%PDF`: la magia no es el código nuevo. `tests/test_e5_ui.py` solo reemplaza el assert de «baseline no se asocia». `test_localhost_config_disables_usage_stats` y `test_quality_profile_is_sent` siguen en verde. El conjunto exacto de etiquetas de `download_button` de `test_load_run_and_show_approximations` no está autorizado a cambiar y no tiene por qué cambiar: ese test no pulsa un control nuevo, y los cuatro nombres pueden seguir ahí. No es un hueco.

R-388: **sí.** El filtro por código `B` deja solo actividades cuyo código contiene `B`. Con N = 1 desde B, en la cadena A–B–C, se ven A, B y C; con N = 0, solo B. La caminata la hace el test sobre `schedule.relationships`, no un helper de la UI comparado consigo mismo. El resaltado driving es el conjunto `task_code` de `driving_chain` de `PathsModeB` para el mismo cronograma. Esa tabla ya existe. El oráculo no es el código nuevo.

R-389: **sí.** Dos XER sintéticos dan un ranking de dos filas, de mayor a menor índice de calidad de `evaluate` de cada archivo. Con la opción de guardar apagada, ninguna celda de la biblioteca contiene `ERMHDR`; prendida, una celda sí, y el XER es el que escribió el test. Guardar por defecto, u ordenar por nombre, no queda en verde. El oráculo es `evaluate` y la lectura de las celdas, no el código nuevo.

R-390: **sí.** El algoritmo está escrito y no se presenta como el de P6. En SHORT 8 h, LONG 16 h y JOIN 8 h, con FS de las dos primeras a JOIN, la semilla de la ruta 1 es JOIN: empata en holgura cero con LONG y termina más tarde; su driving es LONG. La ruta 1 queda LONG orden 1 y JOIN orden 2. SHORT es la ruta 2, orden 1. LOE y WBS quedan fuera del conjunto y no reciben número. La frase «Multiple float paths no se calculan» no aparece. `test_the_longer_predecessor_is_the_driving_one` sigue con driving `LONG` y cadena `{LONG, JOIN}`. El oráculo son los literales del contrato, no un `float_path` de P6 ni la función nueva.

R-391: **sí.** La cadena A–B–C de 8 h con FS y fecha de corte igual al inicio de A tiene ruta 1 `A, B, C` y continuidad verdadera: el inicio de la orden 1 no es posterior al corte, el fin de C es `project_finish` (el máximo de los fin temprano) y hay vínculo en cada par. Una sola actividad con `CS_MSO` posterior al corte tiene ruta 1 de esa actividad y continuidad falsa con «quiebre», porque el inicio de referencia queda después del corte. Sin `last_recalc_date` el estado es `no_evaluable`, la nota dice que falta la fecha de corte y la continuidad no es verdadera. La frase de que la continuidad no se verifica no aparece. El oráculo es `schedule_cpm_reference` y la fecha de corte, no el código nuevo. «Esas tres» del algoritmo se lee como inicio, término y vínculo; la ruta vacía impide que sea verdadera y no es uno de los tres casos de la fila. No es un hueco.

R-392: **sí.** `TASK.driving_path_flag` en `Y` o `y` pone `driving_activity` verdadero; otro valor, o la columna ausente, lo deja en falso. Sigue «Los vínculos driving no se marcan en modo A». El modo A no llama a `schedule_cpm`. `tests/test_e3_paths.py` suma `driving_activity` a la lista de columnas de `bands` y no pierde la frase: el assert actual busca «driving no se marcan», que sigue siendo subcadena. `docs/XER_SPEC.md` pasa esa columna de «esta fase no carga» a leída, citando que PyP6Xer la nombra. El oráculo es el flag en la actividad, no el CPM. No se marca un vínculo de `TASKPRED` ni se inventa otro campo. Los conteos `0-5`, `>5` y `0-10` de ese archivo no se tocan.

R-393: **sí.** Una actividad de 24 h, lunes a viernes 08:00–16:00, corte el lunes 2026-01-05 08:00 y sin feriado, reparte 8 h en 2026-01-05, 2026-01-06 y 2026-01-07. Las tres fechas caen en la semana ISO 2026-W02 y en el mes 2026-01: cada suma es 24 h. La acumulada es 8, 16 y 24. La nota dice que la distribución es lineal en tiempo laboral. En A 8 h y B 16 h con FS, A cae el 2026-01-05 con 8 h y B el 2026-01-06 y el 2026-01-07 con 8 h cada uno. Eso reemplaza el balde `corte` de `tests/test_e4_spreads.py`, incluidas las filas `("A", "corte", 8.0)` y `("B", "corte", 16.0)`. No aparecen «balde corte» ni «No es una curva por periodo». El calendario de `_week` es de siete días, pero esas tres fechas son lunes, martes y miércoles: el reparto de A y B coincide. Sin filas de `TASKRSRC` el histograma está vacío. `resource_limit` sigue `no_evaluable`. El oráculo es la suma de horas de trabajo del calendario, igual a la duración remanente, no el código nuevo. No se inventa un máximo en `RSRCRATE`. Los números de `tests/test_evm.py` (PV 50, `scurve` de un punto, CPI 1,25) no son el balde `corte` y el contrato no los mueve.

R-394: **sí.** Proyecto 1 con A de 8 h y proyecto 2 con B de 8 h, calendario de `_week`, corte 2026-01-05 08:00 y FS con `pred_proj_id` del proyecto 1: A termina el lunes 2026-01-05 16:00 y B empieza el martes 2026-01-06 08:00 y termina a las 16:00, en los dos motores, al minuto. Esas fechas se escriben en el test antes de mirar el resultado. Que los dos motores coincidan el lunes si la mano dice martes no queda en verde. No se reescriben los tests ya verdes de FS, SS, FF, SF, lags, feriado, restricciones, avance fuera de secuencia, LOE, WBS, hitos, ciclos, SS+FF, redundancia ni extremos abiertos. `test_fs_chain_is_critical` sigue con A el lunes 16:00 y B el martes 08:00 en el mismo proyecto. `numeric/kernels.py` no se edita. `pred_proj_id` ya está en `XER_SPEC.md`. El oráculo son las dos fechas, no el código nuevo.

R-395: **no.** La cuenta del texto cierra y el oráculo no es el producto: ver el hueco 1. El calendario es lunes a viernes 08:00–16:00, feriado el miércoles 2026-01-07, corte el lunes 2026-01-05 08:00 y fin de plan el viernes 2026-01-09 16:00. A dura 24 h: lunes 8 h, martes 8 h, miércoles 0 h, jueves 8 h, y termina el jueves 2026-01-08 16:00. B dura 8 h con SS a A y lag 0: empieza el lunes 08:00 y termina el lunes 16:00, y no mueve ese término. El largo laboral hasta el término es 24 h. Del jueves 16:00 al viernes 16:00 hay 8 h. CPLI = (24+8)/24 = 4/3. 4/3 es mayor que `cpli_min` 0,95 de `dcma_estricto`, así que el estado `cumple` cierra. `(24+8)/24` y `4/3` son el mismo flotante. No se suma 24+8 como largo, ni se cuenta el miércoles. `tests/oracle/span.py` sigue siendo el caso de siete días: lunes 08:00 a miércoles 16:00 son 24 h y de ahí al viernes 16:00 son 16 h, o sea (24+16)/24. Ese assert de `tests/test_e3_cpli.py` y el de `tests/test_e3_oracle.py` no se mueven. Firmar el 4/3 con `evaluate` no queda en verde.

R-396: **no.** El 2/2 del caso ya escrito cierra, y el assert no se mueve: ver el hueco 1. Corte 2026-02-01 00:00. LATE está completa, fin real 2026-01-12 y fin baseline 2026-01-10: entra en las dos cuentas. OPEN no está completa y su fin baseline es 2026-01-20: solo en el denominador. EARLY está completa, fin real 2026-01-05 16:00 y fin baseline 2026-03-01: solo en el numerador. Vencidas LATE y OPEN; completadas a la fecha de corte LATE y EARLY. 2/2 y `cumple` con `bei_min` 0,95. Es el comentario que ya está en `tests/test_e3_bei.py` y la definición de la sección 6: todas las completadas al corte, incluidas las tempranas, sobre las de fin baseline anterior o igual al corte. `tests/oracle/bei.py` no importa `src/atlaspmo`. Cambiar el 2/2 para que otro oráculo pase no queda en verde.

La cobertura que cita el contrato es la de `docs/qa/E9/gate.json`: `coverage_percent` 91,1. G12 falla si la bajada es mayor que 0,5. No hay meta nueva de la sección 11. No es un hueco.

## Huecos

1. Falta, en R-395 y R-396, el contrato que deje en verde `tests/test_phase1.py::test_hand_calculated_metrics`. Ese test recorre cada `*.yaml` de `tests/fixtures/synthetic/cases/`, exige `file` (un XER de esa carpeta), y por cada clave de `expect` exige `status` y un `value` numérico (`pytest.approx`). El contrato pone ahí `cpli_ss.yaml` y `bei.yaml`. De `cpli_ss.yaml` dice `calculado_por`, `verificado_por: tests/oracle/span_holiday.py` y `expect.cpli.value` 4/3; no dice `file` ni la clave `status`. De `bei.yaml` no dice campos. No hay XER nuevo en la lista de archivos, y `scripts/build_cases.py` no está autorizado a sumar uno. `test_phase1.py` tampoco está en los archivos editables. Un YAML con solo lo escrito, o sin `file`, tumba ese test verde. El 4/3 y el 2/2 no son el hueco: la cuenta de ambos cierra. La sección 7 pide además `metodo` en la doble firma; el contrato no lo nombra. Eso solo no rechazaría.

## Asserts que no quedan en contradicción

- `tests/test_e5_ui.py`: solo se reemplaza «baseline no se asocia». No hay otro assert numérico de esa pantalla que el contrato vuelva falso. «Puntos de quality_index: 1» sigue siendo una corrida guardada.
- `tests/test_e4_spreads.py`: las dos frases y las filas `("A", "corte", 8.0)`, `("B", "corte", 16.0)` se reemplazan por los tres días ya contados. El reemplazo está autorizado. No queda otro assert de horas en un balde `corte`.
- `tests/test_e3_paths.py`: se suma `driving_activity` y se conserva la frase. Los conteos 1, 1 y 2, y el driving `LONG` con cadena `{LONG, JOIN}`, siguen.
- `tests/test_e3_cpli.py` y `tests/test_e3_oracle.py`: (24+16)/24 y 24×60 / 16×60 no se tocan.
- `tests/test_e3_bei.py`: `2 / 2` y `cumple` no se mueven.
- `tests/test_evm.py`: `resource_limit` sigue `no_evaluable`. El tope de `RSRCRATE` no se inventa. `XER_SPEC.md` dice que no hay un campo citado de límite, y el contrato lo repite.

`driving_path_flag` no es un campo inventado: `XER_SPEC.md` ya dice que PyP6Xer lo nombra y que esta fase no lo carga. El contrato solo lo pasa a leído. No aparece otro nombre de tabla o de columna XER que esa especificación no cite. La tabla de curvas de recurso sigue sin nombre.

## Comandos

En el worktree, sin pytest, sin red y sin la red de 30 000:

- `git rev-parse --short HEAD` y `git branch --show-current`: `d38bdaa`, rama `v3`. El mensaje es el contrato de E10 anterior al código.
- `git status --porcelain` antes de este archivo: vacío.
- `tests/test_e10_*.py`, `tests/oracle/span_holiday.py` y `tests/oracle/bei.py`: no están.
- Calendario, sin importar `src/atlaspmo`: 2026-01-01 es jueves; 2026-01-05 a 2026-01-09 son lunes a viernes; 2026-01-05, 06 y 07 son la semana ISO 2026-W02; `(24+8)/24 == 4/3`.
- `docs/qa/E9/gate.json`: `coverage_percent` 91,1.

## Qué no pude verificar

No reejecuté pytest ni el gate. El 91,1 es el del gate de E9 ya versionado, no una medición de esta auditoría. No corrí `evaluate` para firmar el 4/3 ni el 2/2: la cuenta es la del texto. No abrí `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

## Segunda pasada

ACEPTADO

Segunda lectura del contrato en `fef86e5` (rama `v3`), no del texto de `d38bdaa`. El rechazo de arriba se conserva. Los tests `tests/test_e10_*.py` y los oráculos `tests/oracle/span_holiday.py` y `tests/oracle/bei.py` siguen sin existir: el contrato los deja fuera de verde. No es rechazo. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se corrió el gate ni la red de 30 000. No se firmó el 4/3 ni el 2/2 con `evaluate`.

El hueco 1 quedó cerrado. `tests/test_phase1.py` no se edita. `test_hand_calculated_metrics` exige `file` y, en cada clave de `expect`, `value` numérico y `status`. El contrato lo dice en las dos filas y en la lista de archivos.

1. Cerrado. `cpli_ss.yaml` trae `file: cpli_ss.xer`, `calculado_por`, `verificado_por: tests/oracle/span_holiday.py`, `metodo` y `expect.cpli` con `value` 1.3333333333333333 y `status: cumple`. Ese flotante es `(24+8)/24`, el mismo 4/3. `scripts/build_cases.py` escribe `cpli_ss.xer` con `plan_end_date` y el feriado en `clndr_data`. Esas dos columnas ya las lee el cargador. `parse_clndr_data` ya acepta `DaysOfWeek` y una excepción `(d|serial)` sin turno, que es un día sin trabajo. `test_round_trip_cases` no se toca. Dejar el YAML sin `file` o sin `status` no queda en verde.
2. Cerrado. `bei.yaml` trae `file: bei.xer`, `proj_id: "1"`, `baseline_proj_id: "2"`, `calculado_por`, `verificado_por: tests/oracle/bei.py`, `metodo` y `expect.bei` con `value` 1.0 y `status: cumple`. 1.0 es el `2 / 2` que el assert de `tests/test_e3_bei.py` no mueve. El XER lo escribe `scripts/build_cases.py`: proyecto 1 con corte 2026-02-01 00:00 y proyecto 2 como baseline. LATE completa, fin real 2026-01-12 08:00 y fin baseline 2026-01-10 08:00. OPEN sin completar, fin baseline 2026-01-20 08:00. EARLY completa, fin real 2026-01-05 16:00 y fin baseline 2026-03-01 08:00. Son las tres filas del caso ya escrito. El YAML tiene que pasar el test sin editarlo. Dejarlo sin `file`, sin `status` o sin los dos proyectos no queda en verde.

R-395: **sí.** El término guardado de A es el jueves 2026-01-08 16:00, con `float_path` 1. B no está en esa ruta. El largo sigue siendo 24 h y la holgura 8 h. El oráculo recorre los turnos, se salta el miércoles y no importa `src/atlaspmo`. `evaluate` iguala el 4/3; firmar el número con `evaluate` no queda en verde. `tests/oracle/span.py` y el (24+16)/24 no se tocan.

R-396: **sí.** El oráculo recibe las tres filas y la fecha de corte y devuelve 2/2. No importa `src/atlaspmo`. El assert `2 / 2` y `cumple` no se mueven.

No queda otro hueco. No se inventa un campo XER. El tope de `RSRCRATE` sigue sin calcularse.

## Comandos de la segunda pasada

- `git rev-parse --short HEAD` y `git log -1 --oneline`: `fef86e5`, «segunda redaccion del contrato de E10». El rechazo de arriba queda en este archivo.
- `git status --porcelain` antes de esta sección: vacío.
