# XER_SPEC

Nombres usados por el lector de la fase 1. **Sin confirmar en un export de Nicolás.**

La evidencia pública de esta sesión es el lector PyP6Xer (`task.py`, `taskpred.py`) y los ejemplos de la sección 5 de `MEGAPROMPT.md`. Un nombre que no está en esa evidencia queda marcado como supuesto. `scripts/gen_synthetic.py` sigue emitiendo la tabla `SYNTH` con `col_a` y `col_b`: esos nombres no son campos de P6.

## Archivo

Texto delimitado por tabuladores. La primera línea empieza por `ERMHDR`. Cada tabla es `%T`, `%F`, `%R`. El archivo termina en una línea que empieza por `%E`.

El lector guarda las líneas ya decodificadas y el salto de línea original. Si el modelo no cambia nada, el escritor devuelve los mismos bytes. Codificación cp1252. Se rechaza un BOM UTF-8 y los bytes que cp1252 no define (0x81, 0x8D, 0x8F, 0x90, 0x9D).

Los identificadores quedan como texto. Una celda vacía es `None` y no es una columna ausente. Una columna que no está en `%F` es `None` y se anota en `Schedule.absent_columns` como `TABLA.columna`. Una tabla ausente se anota en `absent_tables`. Una coma decimal sin punto se lee como punto y queda en `parse_notes`. Las duraciones no se dividen por 8 en silencio: `day_hr_cnt` vive en el calendario.

Fechas aceptadas: `%Y-%m-%d %H:%M` (formato que usa PyP6Xer), `%Y-%m-%d %H:%M:%S` y `%Y-%m-%d`.

## PROJECT

Leídos: `proj_id`, `proj_short_name`, `proj_name`, `clndr_id`, `last_recalc_date`, `plan_end_date`, `scd_end_date`.

`last_recalc_date` es la fecha de corte citada por el megaprompt. `plan_end_date` y `scd_end_date` son supuestos de nombre, sin confirmar. Los campos `sched_*` y `critical_*` de la sección 5 no se leen en esta fase.

## CALENDAR

Leídos: `clndr_id`, `clndr_name`, `proj_id`, `day_hr_cnt`, `base_clndr_id`, `clndr_data`.

`day_hr_cnt` y `clndr_data` los pide el megaprompt. El texto de `clndr_data` se guarda crudo. Esta fase no lo interpreta. `base_clndr_id` es un supuesto de nombre.

## PROJWBS

Leídos: `wbs_id`, `proj_id`, `parent_wbs_id`, `wbs_short_name`, `wbs_name`. Supuestos de nombre, salvo que el megaprompt nombra la tabla.

## TASK

Citados por PyP6Xer y leídos aquí: `task_id`, `proj_id`, `wbs_id`, `clndr_id`, `phys_complete_pct`, `complete_pct_type`, `task_type`, `status_code`, `task_code`, `task_name`, `total_float_hr_cnt`, `free_float_hr_cnt`, `remain_drtn_hr_cnt`, `target_drtn_hr_cnt`, `act_start_date`, `act_end_date`, `late_start_date`, `late_end_date`, `early_start_date`, `early_end_date`, `target_start_date`, `target_end_date`, `cstr_type`, `cstr_type2`, `int_path`, `int_path_order`.

PyP6Xer también nombra, y esta fase no carga: `duration_type`, `rsrc_id`, `cstr_date`, `expect_end_date`, `restart_date`, `reend_date`, `driving_path_flag`.

`float_path` y `float_path_order` los nombra el megaprompt en la sección 6 (modo A). PyP6Xer no los lee en `TASK`; lee `int_path` e `int_path_order`. El modo A prefiere `TASK.float_path` si la columna está. Si no, usa `TASK.int_path` y deja la aproximación en el resultado. La ruta `"1"` se toma como la primera ruta guardada. Es un supuesto.

## TASKPRED

Citados por PyP6Xer y leídos aquí: `task_pred_id`, `task_id`, `pred_task_id`, `proj_id`, `pred_proj_id`, `pred_type`, `lag_hr_cnt`.

PyP6Xer lee `pred_proj_id` con la clave `proj_id` por un error de su `__init__`. Este lector usa la columna `pred_proj_id`.

`float_path` en `TASKPRED` no es la holgura libre del vínculo. El modo A no marca vínculos driving. PyP6Xer también nombra `aref`, `arls` y `comments`; no se leen.

## TASKRSRC

Leídos: `taskrsrc_id`, `task_id`, `rsrc_id`, `target_qty`, `target_cost`, `act_reg_cost`, `remain_cost`.

`task_id` y `rsrc_id` son los nombres que el chequeo de recursos necesita. El resto son supuestos de nombre. Si la columna `target_cost` no está, el chequeo de recursos mira solo la asignación y lo anota como aproximación.

## TASKACTV

`task_id` es el nombre seguro. `actv_code_id` y `actv_code_type_id` son supuestos de nombre habitual en P6, sin cita de PyP6Xer en esta sesión.

## Códigos de la sección 5

No están verificados en un export. Se usan tal como los cita el megaprompt:

- Vínculos: `PR_FS`, `PR_SS`, `PR_FF`, `PR_SF`.
- Actividades: `TT_Task`, `TT_Rsrc`, `TT_Mile`, `TT_FinMile`, `TT_LOE`, `TT_WBS`.
- Estados: `TK_NotStart`, `TK_Active`, `TK_Complete`.
- Restricciones: `CS_MSO`, `CS_MSOA`, `CS_MSOB`, `CS_MEO`, `CS_MEOA`, `CS_MEOB`, `CS_MANDSTART`, `CS_MANDFIN`, `CS_ALAP`.

El conjunto duro por defecto (`CS_MSO`, `CS_MEO`, `CS_MANDSTART`, `CS_MANDFIN`) es una decisión de producto, no un campo del archivo. El perfil contratista deja solo `CS_MANDSTART` y `CS_MANDFIN`.

## Baseline

No hay un campo de baseline por actividad verificado. La fase 1 toma el fin baseline como `target_end_date` del proyecto indicado por `baseline_proj_id`, emparejado por `task_code`.

## PMXML mínimo

El lector de `tests/fixtures/synthetic/minimal.xml` usa `APIBusinessObjects`, `Project`, `Activity` y `Relationship`. No está confirmado contra un export de Nicolás.

Traducción explícita, no leída de un XER:

- `Not Started` → `TK_NotStart`, `In Progress` → `TK_Active`, `Completed` → `TK_Complete`.
- `Task Dependent` → `TT_Task`, `Resource Dependent` → `TT_Rsrc`, `Level of Effort` → `TT_LOE`, `Start Milestone` → `TT_Mile`, `Finish Milestone` → `TT_FinMile`, `WBS Summary` → `TT_WBS`.

`PlannedDuration`, `RemainingDuration`, `TotalFloat` y `Lag` se leen como horas en punto flotante, sin conversión de unidad. Es un supuesto.

## Tablas que el megaprompt nombra y esta fase no modela

`RSRC`, `RSRCRATE`, `ACTVTYPE`, `ACTVCODE`, `UDFTYPE`, `UDFVALUE` y la tabla de curvas de recurso. El nombre de esa última tabla no tiene evidencia. El lector genérico conserva sus líneas para el round-trip.
