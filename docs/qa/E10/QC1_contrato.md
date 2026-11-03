# QC-1 — contrato de E10

Etapa E10. Ciclo 1. Anterior al código. Brechas B-01, B-12, B-13, B-14, B-10 y B-11, en ese orden. No hay meta nueva de la sección 11. El implementador no edita `docs/qa/seccion11.toml`, `docs/qa/baseline.json`, `scripts/qa_gate.py`, `docs/qa/skips.toml`, `tests/oracle/**` ni `tests/fixtures/**/expected*`.

Los tests `tests/test_e10_ui.py`, `tests/test_e10_paths.py`, `tests/test_e10_spread.py`, `tests/test_e10_edges.py` y `tests/test_e10_sign.py` todavía no existen: no están en verde. Los oráculos `tests/oracle/span_holiday.py` y `tests/oracle/bei.py` tampoco. `qa-oraculo` los escribe y no importa `src/atlaspmo`. El número del YAML sale de este contrato, no de una corrida de `evaluate`.

La cobertura del gate de E9 es 91,1. G12 falla si baja más de 0,5. No se edita `numeric/kernels.py`. No se agregan ramas en el empaquetado de `engine/fast.py`. Un calendario real, `data/real/` y `ATLASPMO_GOLDEN_DIR` no son oráculo.

Puntos abiertos, registrados, que no se presentan como hechos:

- Igualar estos float paths con un export de P6 queda en `VALIDACIONES_PENDIENTES.md`. El algoritmo de abajo no es el de P6.
- El tope de `RSRCRATE` no se calcula. `docs/XER_SPEC.md` dice que no hay un campo citado de límite.
- La tabla de curvas de recurso no tiene nombre con evidencia. La distribución es lineal en tiempo laboral y se anota como aproximación.
- Los bordes de la sección 7 que ya tienen test no se reescriben. El borde nuevo es el vínculo entre dos proyectos.

| Requisito | Criterio ejecutable | Oráculo | Qué no queda en verde |
|---|---|---|---|
| R-387 | Con dos XER sintéticos del test, la pantalla deja de decir «El baseline no se asocia en esta pantalla.» El BEI que muestra es el de `evaluate(actual, perfil, baseline)` sobre ese par. El módulo que declara `RESOURCES` muestra «requiere recursos». El que declara `TWO_VERSIONS` muestra «requiere dos versiones». Un módulo sin requisitos no muestra esa línea. Tras ejecutar hay una barra `st.progress` en 1 y una pestaña por módulo corrido. «Informe completo» ofrece un binario que empieza con `PK` y otro que empieza con `%PDF`. `tests/test_e5_ui.py` reemplaza el assert de la frase vieja; `test_localhost_config_disables_usage_stats` y `test_quality_profile_is_sent` siguen en verde | `evaluate` ya existente, y la magia de los dos binarios | Afirmar el e2e sin AppTest. Abrir un socket. Leer un cronograma real. Dejar la frase de que el baseline no se asocia |
| R-388 | En la cadena A–B–C el filtro por código `B` deja solo actividades cuyo código contiene `B`. Con N = 1 desde B el visor muestra A, B y C. Con N = 0 muestra solo B. La caminata de predecesoras y sucesoras la hace el test sobre `schedule.relationships`, no una función de la UI. El resaltado driving es el conjunto `task_code` de la tabla `driving_chain` de `PathsModeB` para el mismo cronograma | La caminata del test y la tabla `driving_chain` ya existente | Contar niveles dentro del helper de la UI y comparar el helper consigo mismo |
| R-389 | Una carpeta con dos XER sintéticos produce un ranking de dos filas, ordenado por el índice de calidad de `evaluate` de cada uno, de mayor a menor. Con la opción de guardar el cronograma apagada, ninguna celda de la biblioteca contiene `ERMHDR`. Con la opción prendida, una celda sí lo contiene. El XER es el que escribió el test | `evaluate` de cada archivo, y la lectura de todas las celdas de la biblioteca | Guardar el cronograma por defecto. Ordenar por nombre de archivo |
| R-390 | El algoritmo de abajo, en SHORT 8 h, LONG 16 h y JOIN 8 h, con FS de SHORT a JOIN y de LONG a JOIN, publica la ruta 1 como LONG orden 1 y JOIN orden 2, y la ruta 2 como SHORT orden 1. LOE y WBS no reciben número de ruta. La frase «Multiple float paths no se calculan» no aparece. El caso de `test_the_longer_predecessor_is_the_driving_one` sigue con driving `LONG` y cadena `{LONG, JOIN}` | Los literales de este contrato | Copiar un `float_path` guardado por P6 y llamarlo cálculo del motor. Presentar el algoritmo como el de P6 |
| R-391 | La cadena A–B–C de 8 h, FS, con fecha de corte igual al inicio de A, tiene ruta 1 `A, B, C` en ese orden y continuidad verdadera. Una sola actividad con `CS_MSO` posterior a la fecha de corte tiene ruta 1 de esa actividad y continuidad falsa, con la nota «quiebre». Sin fecha de corte el estado es `no_evaluable`, la nota dice que falta la fecha de corte, y la continuidad no es verdadera. La frase «La continuidad desde la fecha de corte hasta el término no se verifica» no aparece | `schedule_cpm_reference` para el inicio y el término, y la fecha de corte del proyecto | Dar por continua una ruta cuyo inicio de referencia es posterior a la fecha de corte |
| R-392 | Si la columna `TASK.driving_path_flag` está y el valor es `Y` o `y`, la fila de esa actividad trae `driving_activity` verdadero. Cualquier otro valor, o la columna ausente, lo deja en falso. Sigue la frase «Los vínculos driving no se marcan en modo A». El modo A no llama a `schedule_cpm`. `tests/test_e3_paths.py` suma la columna `driving_activity` a la lista y no pierde la frase. `docs/XER_SPEC.md` pasa esa columna de «esta fase no carga» a leída, citando que PyP6Xer la nombra | El flag en la actividad, no el CPM | Marcar un vínculo de `TASKPRED` como driving. Inventar otro campo |
| R-393 | Una actividad de 24 h, calendario lunes a viernes de 08:00 a 16:00, fecha de corte lunes 2026-01-05 08:00 y sin feriado, reparte 8 h en `2026-01-05`, `2026-01-06` y `2026-01-07`. La semana ISO `2026-W02` suma 24 h. El mes `2026-01` suma 24 h. La curva acumulada es 8, 16 y 24. La nota dice que la distribución es lineal en tiempo laboral. En A 8 h y B 16 h con FS, el día de A es `2026-01-05` con 8 h y los de B son `2026-01-06` y `2026-01-07` con 8 h cada uno: eso reemplaza el balde `corte` de `tests/test_e4_spreads.py`. No aparecen «balde corte» ni «No es una curva por periodo». Sin filas de `TASKRSRC` el histograma está vacío y la nota dice que no hay asignación. `resource_limit` sigue `no_evaluable` | Suma de horas de trabajo del calendario, igual a la duración remanente | Inventar un máximo en `RSRCRATE`. Dejar las horas en un solo balde `corte` |
| R-394 | Proyecto 1 con A de 8 h y proyecto 2 con B de 8 h, el mismo calendario de `_week`, fecha de corte 2026-01-05 08:00 y un FS con `pred_proj_id` del proyecto 1. A termina el lunes 2026-01-05 16:00 y B empieza el martes 2026-01-06 08:00 y termina a las 16:00, en el motor de referencia y en el rápido, al minuto. No se reescriben los tests ya verdes de FS, SS, FF, SF, lags, feriado, restricciones, avance fuera de secuencia, LOE, WBS, hitos, ciclos, SS+FF, redundancia ni extremos abiertos | Esas dos fechas, escritas en el test antes de mirar el resultado | Dar por bueno que los dos motores coincidan el lunes si la mano dice martes. Tocar `numeric/kernels.py` |
| R-395 | Calendario lunes a viernes 08:00–16:00, feriado el miércoles 2026-01-07, fecha de corte el lunes 2026-01-05 08:00, fin de plan el viernes 2026-01-09 16:00. A dura 24 h. B dura 8 h y tiene un SS con A y lag 0. El término crítico es el jueves 2026-01-08 16:00. B empieza el lunes 08:00 y termina el lunes 16:00. El largo laboral hasta el término es 24 h y la holgura hasta el plan es 8 h. CPLI = (24+8)/24 = 4/3, estado `cumple` con `dcma_estricto` (`cpli_min` 0,95). `tests/oracle/span_holiday.py` recorre los turnos, se salta el feriado y no importa `src/atlaspmo`. `evaluate` iguala ese valor. El YAML `cpli_ss.yaml` trae `calculado_por`, `verificado_por: tests/oracle/span_holiday.py` y `expect.cpli.value` 4/3. `tests/oracle/span.py` no se toca: sigue siendo el caso de siete días | El oráculo de turnos y el 4/3 de este contrato | Firmar con `evaluate`. Sumar duraciones. Contar el miércoles como laboral |
| R-396 | El caso de `tests/test_e3_bei.py` sigue en 2/2 y `cumple`. `tests/oracle/bei.py` no importa `src/atlaspmo`. Recibe las tres filas (código, estado, fin real, fin baseline) y la fecha de corte, y devuelve 2/2: vencidas LATE y OPEN; completadas a la fecha de corte LATE y EARLY. El test de firma iguala `evaluate` con ese retorno. El assert `2 / 2` no se mueve | El conteo de este contrato y el assert ya escrito | Cambiar el 2/2 para que un oráculo distinto pase |

## Algoritmo de float paths (R-390 y R-391)

No es el de P6. Queda escrito en el docstring de la función que lo calcule.

Entran las actividades de `result.by_id` cuyo `task_type` no es `TT_LOE` ni `TT_WBS`. Se repite hasta que no quede ninguna sin ruta:

1. La semilla es la no asignada de menor `total_float_hours`. Empate: la de `early_finish` más tarde. Empate: `task_code` ascendente.
2. La cadena nace en la semilla. Mientras el cursor tenga una predecesora driving, elegible y sin ruta, se elige una sola: la de mayor `remain_drtn_hr_cnt` (0 si falta). Empate: `task_code` ascendente. Se antepone a la cadena. Las otras driving quedan libres.
3. La ruta k, desde 1, numera `float_path_order` desde 1 en el extremo inicial de esa cadena hasta el final en la semilla.

La continuidad se juzga solo sobre la ruta 1.

- Sin `last_recalc_date`: `no_evaluable`, nota de que falta la fecha de corte, y la continuidad no es verdadera.
- Verdadera solo si la ruta no está vacía, el `early_start` de la orden 1 es menor o igual que la fecha de corte, el `early_finish` de la última iguala a `project_finish`, y cada par consecutivo tiene un vínculo del anterior al siguiente.
- Si falta cualquiera de esas tres, es falsa y la nota contiene «quiebre».

En SHORT, LONG y JOIN la semilla de la ruta 1 es JOIN: empata en holgura cero con LONG y termina más tarde. Su única driving es LONG. La ruta 1 queda LONG, JOIN. SHORT es la ruta 2.

## Archivos

- UI: `src/atlaspmo/ui/app.py`, `src/atlaspmo/reports/gantt.py`, `tests/test_e10_ui.py`, y solo el assert de la frase vieja en `tests/test_e5_ui.py`.
- Rutas: `src/atlaspmo/analysis/paths/`, el campo y la lectura de `driving_path_flag` en `src/atlaspmo/model/` y `src/atlaspmo/io/xer.py`, el párrafo de `docs/XER_SPEC.md`, `tests/test_e10_paths.py`, y la lista de columnas de `tests/test_e3_paths.py`.
- Recursos: `src/atlaspmo/analysis/resources/`, `tests/test_e10_spread.py` y el reemplazo autorizado de `tests/test_e4_spreads.py`.
- Borde: `tests/test_e10_edges.py`. `engine/cpm.py` solo si esas fechas no salen. `engine/fast.py` solo si el rápido no repite esas fechas. `numeric/kernels.py` no se edita.
- Firma: `qa-oraculo` posee `tests/oracle/span_holiday.py`, `tests/oracle/bei.py` y los YAML `tests/fixtures/synthetic/cases/cpli_ss.yaml` y `tests/fixtures/synthetic/cases/bei.yaml`. El test `tests/test_e10_sign.py` puede comparar. No cambia los literales 4/3 ni 2/2. `analysis/quality/check.py` solo si `evaluate` no da esos números.

No tocar: `src/atlaspmo/numeric/kernels.py`, `tests/perf/test_seccion11.py`, `docs/qa/E9/VEREDICTO.md`, `docs/qa/E10/VEREDICTO.md`.
