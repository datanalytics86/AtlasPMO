# Reglas de calidad

Catálogo de lo que calcula M1 en la fase 1. DCMA 12 no está: pide el motor CPM de la fase 2.

Estado de una métrica: `cumple`, `no_cumple`, `no_evaluable`, `info` o `manual`. Si falta un requisito, la métrica es `no_evaluable` y el motivo queda en un hallazgo.

## Población incompleta

Actividades con `status_code` distinto de `TK_Complete`. El perfil puede excluir `TT_LOE` y `TT_WBS`. Los hitos `TT_Mile` y `TT_FinMile` salen solo de la duración alta. Si falta `TASK.status_code`, la lógica no se evalúa.

Horas a días: `horas / hours_per_day` del perfil, si el perfil lo fija. Si no, `horas / day_hr_cnt` del calendario de la actividad. Si falta `day_hr_cnt` y el perfil no fija `hours_per_day`, la métrica es `no_evaluable`. No se usa 8 en silencio.

Fecha de corte: el único `last_recalc_date` entre los proyectos seleccionados. Si hay más de una fecha distinta, no hay fecha de corte.

## DCMA implementado

Umbrales de `profiles/dcma_estricto.yaml`, salvo que el perfil diga otra cosa.

| Id | Definición | Población | Umbral | Fuente |
|---|---|---|---|---|
| logic | Parte sin predecesora o sin sucesora | Incompletas | máximo 5 % | DCMA 1 |
| leads | Vínculos con `lag_hr_cnt` < 0 | Vínculos con predecesora y sucesora | máximo 0 | DCMA 2 |
| lags | Vínculos con `lag_hr_cnt` > 0 | La misma | máximo 5 % | DCMA 3 |
| relationship_types | Parte con `pred_type` = `PR_FS` | La misma | mínimo 90 % | DCMA 4 |
| hard_constraints | Incompletas con `cstr_type` o `cstr_type2` en el conjunto duro | Incompletas | máximo 5 % | DCMA 5 |
| high_float | Holgura total en días > `high_float_days` (44) | Incompletas | máximo 5 % | DCMA 6 |
| negative_float | Holgura total en días < 0 | Incompletas | máximo 0 | DCMA 7 |
| high_duration | Duración en días > `high_duration_days` (44). Campo `remain` o `original` | Incompletas, sin hitos | máximo 5 % | DCMA 8 |
| invalid_dates | Conteo, no razón. Prevista (`early_start` o `early_end`) anterior a la fecha de corte en una no completa, o real (`act_start` o `act_end`) posterior | Actividades del proyecto | máximo 0 | DCMA 9 |
| resources | Incompletas no hito, duración > 0, sin `TASKRSRC.rsrc_id` y sin costo si existe `target_cost` | Esa población | `resources_max` nulo: estado `info` y fuera del índice | DCMA 10 |
| missed_tasks | Con fin baseline ≤ fecha de corte, no `TK_Complete` o `act_end_date` posterior al fin baseline | Esas actividades | máximo 5 % | DCMA 11 |
| cpli | (días remanentes de la ruta `"1"` + holgura total en días de la actividad de mayor orden en esa ruta) / días remanentes | Ruta guardada | mínimo 0,95 | DCMA 13 |
| bei | Completadas / actividades con fin baseline ≤ fecha de corte | La misma que missed | mínimo 0,95 | DCMA 14 |

Lag vacío o columna de lag ausente: leads y lags quedan `no_evaluable`. No se trata el vacío como cero.

Fin baseline: `target_end_date` del proyecto `baseline_proj_id`, emparejado por `task_code`. Ver `XER_SPEC.md`. Sin ese proyecto, missed y BEI son `no_evaluable`. Los hallazgos de BEI salen solo si el estado es `no_cumple`, y solo para las que no están completas.

CPLI: columna `TASK.float_path` si existe; si no, `TASK.int_path`, con la nota de aproximación. Días de ruta 0, o duración, holgura o horas/día faltantes: `no_evaluable`.

## Índice

`100 * peso de las métricas DCMA evaluables que cumplen / peso de esas métricas`. Entran las que están en `cumple` o `no_cumple`. Quedan fuera `no_evaluable` e `info`. El índice mismo tiene estado `info`. Pesos por defecto 1 en: logic, leads, lags, relationship_types, hard_constraints, high_float, negative_float, high_duration, invalid_dates, missed_tasks, cpli, bei. Resources y DCMA 12 no pesan.

## GAO-16-89G

| Id | Práctica | Cómo |
|---|---|---|
| gao_01 | Capturar actividades | Cumple si hay actividades |
| gao_02 | Secuenciar | Se hereda de logic. Si logic no es evaluable, manual |
| gao_03 | Asignar recursos | Se hereda de resources. `info` pasa a manual |
| gao_04 | Establecer duraciones | Se hereda de high duration |
| gao_05 | Trazabilidad | Cumple si inicios abiertos ≤ 1 y fines abiertos ≤ 1 |
| gao_06 | Ruta crítica válida | Manual |
| gao_07 | Holgura razonable | Las dos holguras. Una que no cumple hace fallar el par |
| gao_08 | Análisis de riesgo | Manual |
| gao_09 | Actualizar con avance | Cumple si hay alguna fecha real. Si no, manual |
| gao_10 | Mantener el baseline | Se hereda de BEI. Si BEI es `no_evaluable`, manual |

Cada manual agrega un hallazgo info: "Requiere revisión manual."

## Chequeos adicionales

| Id | Regla | Estado |
|---|---|---|
| open_starts / open_finishes | Conteos de incompletas sin predecesora o sin sucesora | info |
| sf_links | Hay algún `PR_SF` | cumple o no_cumple, umbral 0 |
| convergence | Predecesoras entrantes ≥ `convergence_predecessors` (4) | info |
| out_of_sequence | La sucesora tiene `act_start_date` y la predecesora no está `TK_Complete` | cumple o no_cumple |
| actual_after_data_date | Real posterior a la fecha de corte | cumple o no_cumple |
| lag_vs_successor | `lag_hr_cnt` mayor que la duración remanente de la sucesora | info |
| odd_calendar | `clndr_id` distinto del dominante | info |
| loe_logic | `TT_LOE` precede a `TT_Task` | cumple o no_cumple |
| missing_codes | Falta un tipo listado en `required_code_type_ids` | Si la lista está vacía, `no_evaluable` |
| logic_density | Vínculos / actividades | info, sin umbral |

## Perfiles

Elecciones de producto, no campos del XER.

- `dcma_estricto`: umbrales de la tabla DCMA. Lags máximo 5 %. Holgura alta 44 días. FS mínimo 90 %. `resources_max` nulo.
- `corporativo`: lags máximo 10 %, holgura alta 60 días y máximo 10 %, FS mínimo 85 %, convergencia 5.
- `contratista`: conjunto duro solo `CS_MANDSTART` y `CS_MANDFIN`. Lags máximo 15 %, FS mínimo 80 %, duración alta 60 días, lógica máxima 10 %, CPLI y BEI mínimo 0,90, missed máximo 10 %, convergencia 6.

`hours_per_day` del archivo es nulo. Un argumento del módulo puede pisarlo. Si falta el YAML, se usa el perfil de código y queda una nota.

## Prueba de ruta (DCMA 12)

La fase 2 la calcula en el modo B. Elige la actividad crítica de menor `task_code` con duración remanente, le suma 8 horas y vuelve a programar. Cumple si el término del proyecto se mueve exactamente 8 horas laborales del calendario de esa actividad. Si no hay crítica con duración, o el motor no tiene término, queda `no_evaluable`.

## Modo B, redundancia y limpieza

El modo B publica las fechas recalculadas. No usa la holgura guardada.

Un vínculo es candidato si, en el grafo de eventos, otro camino entre sus extremos pesa al menos lo mismo. Se confirma solo si al quitarlo no cambian ES, EF, LS, LF, holgura total ni holgura libre en más de un minuto. Si el lote sí mueve fechas, se aísla el vínculo por bipartición. Quedan protegidos los vínculos entre proyectos, los que tocan un hito y los pares SS+FF.

La limpieza borra únicamente las filas `TASKPRED` confirmadas. El resto del archivo no se reescribe.

## Modo A de la ruta

No recalcula CPM. Bandas de holgura total guardada, en días: ≤ 0, 0–10, 10–20, 20–44, > 44. Crítica si los días son ≤ `critical_float_days` (0). Una actividad sin holgura convertible no entra. Los vínculos driving no se marcan: no hay un campo citado de holgura libre del vínculo.

## Riesgo (M5)

Los rangos mínimo / más probable / máximo, la distribución, la correlación y los eventos son configuración del usuario. No son columnas del XER.

- Ancho cero (`mínimo = probable = máximo`) devuelve el probable y no usa el generador. Sin eventos, cada iteración reproduce el CPM determinístico.
- Triangular, uniforme y BetaPERT. BetaPERT: α = 1 + 4 × (probable − mínimo) / (máximo − mínimo), β = 1 + 4 × (máximo − probable) / (máximo − mínimo).
- Iman-Conover solo si se pide correlación y hay al menos dos rangos con ancho. Si la matriz no admite Cholesky, se omite y queda anotado. A la diagonal se le suma 1e-8. Correlación 1 o −1 copia el orden de rangos.
- Un evento suma horas de impacto al remanente cuando sale su probabilidad. Probabilidad 0 no suma. Probabilidad 1 suma en cada iteración.
- P50, P80 y P90 son el percentil empírico del término: el menor valor cuya fracción acumulada alcanza el percentil. Si todos los términos son iguales, los tres coinciden.
- Criticidad: fracción de iteraciones en que la actividad queda crítica.
- SSI = criticidad × σ de la duración / σ del término, en horas laborales. Si σ del término es 0, SSI, crucialidad (Pearson) y Spearman quedan `no_evaluable`.
- El tornado suma las horas pedidas a la duración remanente de una actividad y mide cuánto se mueve el término, en el calendario de esa actividad.
- El motor es Python puro. numba no se cargó en esta fase. La semilla queda en `RunMetadata.seed` y en `run_manifest.json`.

## EVM y Earned Schedule (M6)

Códigos `CP_Phys`, `CP_Drtn` y `CP_Units`: vistos en XER públicos, sin confirmar en un export de Nicolás. Un código desconocido queda `no_evaluable`.

- `CP_Drtn`: porcentaje = acotar(1 − remanente / original, 0, 1), si la original es mayor que 0.
- `CP_Phys`: si `phys_complete_pct` es mayor que 1, se lee como 0–100 y se divide por 100.
- `CP_Units`: `no_evaluable`. No hay un campo de cantidad real cargado.
- BAC = suma de `target_cost`. AC = suma de `act_reg_cost`. Si todos los reales vienen vacíos, AC y CPI quedan `no_evaluable`.
- EV = porcentaje × BAC, acotado a BAC.
- PV lineal entre `target_start_date` y `target_end_date` hasta la fecha de corte, en tiempo laboral del calendario de la actividad. Sin calendario usable, el PV usa tiempo de reloj y lo anota. No hay curva de recurso.
- SPI = EV / PV solo si PV > 0. CPI = EV / AC solo si AC > 0.
- Earned Schedule, con PV lineal: PD es el tiempo laboral entre el inicio baseline más temprano y el fin baseline más tardío de las actividades con BAC. ES = (mín(EV, BAC) / BAC) × PD. AT es el tiempo laboral desde ese inicio hasta la fecha de corte. SPI(t) = ES / AT. IEAC(t) = PD / SPI(t).
- El histograma de recursos suma `target_qty` por `rsrc_id`. El tope contra `RSRCRATE` queda `no_evaluable`: no hay un campo citado de límite.
