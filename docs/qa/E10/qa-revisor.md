# qa-revisor — E10

Revisión de QC-4, etapa E10, HEAD `5edd81e`, rama `v3`. El diff es `git diff 8934ffc..HEAD`. 8934ffc es el cierre de E9. No se reabrió E8 ni E9. No se editó producto, tests, oráculos, el contrato ni `qa-spec.md`. No se escribió `docs/qa/E10/VEREDICTO.md`. No se hizo commit ni push. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se corrió el gate, ni `tests/perf`, ni la marca `seccion11`, ni la red de 30 000.

Esto no cierra la etapa. No hay `gate.json` de E10. H-1 es importante y queda abierto. H-2 y H-3 son menores.

## Diff

36 archivos, 1958 inserciones y 53 borrados, entre documentación de la etapa, la UI, las rutas, EVM, la biblioteca, el Gantt, los dos XER nuevos, los oráculos y los tests `test_e10_*`. No entran `src/atlaspmo/engine/cpm.py`, `src/atlaspmo/engine/fast.py`, `src/atlaspmo/numeric/kernels.py`, `tests/oracle/span.py`, `tests/perf/test_seccion11.py`, `docs/qa/baseline.json`, `docs/qa/seccion11.toml`, `scripts/qa_gate.py` ni `docs/qa/skips.toml`. `cpli.xer` viejo y `baseline.yaml` no cambian. No hay meta nueva de la sección 11.

## Qué leí

- `docs/qa/E10/QC1_contrato.md` y `docs/qa/E10/qa-spec.md` (segunda pasada aceptada). No los reescribí.
- `docs/MEGAPROMPT_v3.md`, secciones 2, 6 (M2, M6 y Transversales), 8 (8.1, 8.4 y 8.5) y 11, y el párrafo E10 de 10.3.
- `docs/VALIDACIONES_PENDIENTES.md` sección E10, las filas R-387 a R-396 de `docs/qa/TRAZABILIDAD.md` y el párrafo nuevo de `docs/ESTADO.md`.
- `docs/XER_SPEC.md` en `driving_path_flag`.
- Producto: `src/atlaspmo/ui/app.py`, `src/atlaspmo/reports/gantt.py`, `src/atlaspmo/library/store.py`, `src/atlaspmo/analysis/paths/mode_a.py`, `src/atlaspmo/analysis/paths/mode_b.py`, `src/atlaspmo/model/schedule.py`, `src/atlaspmo/io/xer.py`, `src/atlaspmo/io/load.py`, `src/atlaspmo/analysis/resources/evm.py`, `src/atlaspmo/analysis/resources/module.py`.
- Para el informe y el baseline: `src/atlaspmo/analysis/quality/module.py`, `src/atlaspmo/analysis/quality/check.py` (BEI, perdidas, CPLI, índice), `src/atlaspmo/runner.py`, `src/atlaspmo/reports/export.py`, `src/atlaspmo/reports/parquet_star.py`, `src/atlaspmo/analysis/compare/module.py`.
- Tests y firma: `tests/test_e10_ui.py`, `tests/test_e10_paths.py`, `tests/test_e10_spread.py`, `tests/test_e10_edges.py`, `tests/test_e10_sign.py`, `tests/test_e5_ui.py`, `tests/test_e4_spreads.py`, `tests/test_e3_paths.py`, `tests/oracle/span_holiday.py`, `tests/oracle/bei.py`, los YAML `cpli_ss.yaml` y `bei.yaml`, y el alta de `scripts/build_cases.py`.
- Notas de implementación en `docs/qa/E10/` (`ui-reportes.md`, `logica-red.md`, `recursos-evm.md`, `motor-cpm.md`, `qa-oraculo.md`) y el párrafo de EVM en `docs/MANUAL_USUARIO.md`.

## Requisitos

R-387. La frase vieja del baseline no está. Los requisitos «requiere recursos» y «requiere dos versiones» salen, y Calidad no lleva esa línea. La barra queda en 1 y hay una pestaña por módulo, con el cuerpo vacío (H-2). El orden de widgets que fijan los tests se sostiene: uploader 0 cronograma, uploader 1 baseline, botón 0 Ejecutar, botón 1 Correr lote, botón 2 Guardar corrida. La UI no llama a `schedule_cpm`. El BEI que se ve es el de `evaluate`, pero es un parche de una celda. La corrida y el informe no lo usan. H-1.

R-388. Con N = 0 el visor queda en B. Con N = 1, en A, B y C. La caminata del test recorre `schedule.relationships` y además afirma esos dos conjuntos. No importa el helper de la UI. El color distinto del Gantt es el conjunto `task_code` de `driving_chain` de `PathsModeB`. El rótulo dice que esa cadena no es un float path de P6.

R-389. `z_cycle.xer` queda antes que `a_open.xer`, que es el orden de `evaluate` y no el del nombre. Con la casilla apagada ninguna celda tiene `ERMHDR`. Prendida, una celda es el XER del test. El default de la casilla es falso.

R-390. SHORT 8 h, LONG 16 h, JOIN 8 h: ruta 1 LONG, JOIN; ruta 2 SHORT. LOE y WBS fuera. El docstring de `_contract_float_paths` dice que no es el algoritmo de P6. La nota de cara al usuario también. No aparece «Multiple float paths no se calculan». `test_the_longer_predecessor_is_the_driving_one` sigue con driving `LONG` y cadena `{LONG, JOIN}`. La semilla usa menor holgura, luego fin temprano más tarde, luego `task_code` ascendente. La predecesora usa mayor `remain_drtn_hr_cnt` (0 si falta) y empata por código ascendente. El caso del contrato ya obliga el empate por fin temprano (JOIN y LONG en holgura cero). No hay un test del empate solo por código. La clave está en el código. No lo subo.

R-391. A–B–C queda en ruta 1 y continuidad `verdadera`, con el inicio de A igual al corte y el fin de C igual a `project_finish` de `schedule_cpm_reference`. El `CS_MSO` posterior al corte queda `falsa` y la nota tiene «quiebre». Sin `last_recalc_date` el estado es `no_evaluable`, la nota dice que falta la fecha de corte y el valor no es verdadero. No aparece la frase de que la continuidad no se verifica. La continuidad se juzga solo sobre la ruta 1.

R-392. `Y` y `y` marcan `driving_activity`. `N`, `Yes`, vacío y la columna ausente quedan en falso. Sigue «Los vínculos driving no se marcan en modo A». `inspect.getsource` de `mode_a` no contiene `schedule_cpm`. El campo nuevo es el último de `Activity`, con default `None`. `docs/XER_SPEC.md` lo pasa a leído y cita a PyP6Xer. `tests/test_e3_paths.py` suma la columna y no pierde la frase.

R-393. 24 h en lunes a viernes 08:00–16:00, corte 2026-01-05 08:00: 8 h el 05, el 06 y el 07. Semana `2026-W02` y mes `2026-01` suman 24. La acumulada es 8, 16, 24. La nota dice que la distribución es lineal en tiempo laboral. A 8 h y B 16 h con FS caen en 2026-01-05, 06 y 07 como pide el contrato. No aparecen «balde corte» ni «No es una curva por periodo» en esas notas. Sin `TASKRSRC` el histograma está vacío y la nota dice que no hay asignación. `resource_limit` sigue `no_evaluable` y el valor es `None`. Una sonda de 12 h, fuera de la suite, dio 8 h el 05 y 4 h el 06: el corte del día no es solo el caso divisible por 8. `tests/test_evm.py` pasó sin mover PV, el punto de `scurve` ni el CPI. H-3 es el hueco del parquet, no de estas horas.

R-394. Proyecto 1 con A y proyecto 2 con B, FS y `pred_proj_id` del proyecto 1. El test escribe lunes 2026-01-05 16:00 y martes 2026-01-06 08:00 y 16:00 antes de mirar el motor. Referencia y rápido coinciden, al minuto, y `LAST["path"]` es `fast`. `cpm.py` y `fast.py` no están en el diff. `test_fs_chain_is_critical` pasó.

R-395. `tests/oracle/span_holiday.py` no importa el producto. El miércoles 2026-01-07 aporta 0. Del lunes 08:00 al jueves 16:00 hay 24 h y de ahí al viernes 16:00 hay 8 h. `(24+8)/24` es el 4/3 del YAML. `evaluate` iguala ese valor y `cumple`. El CPM de referencia termina A el jueves 16:00 y B el lunes 16:00. `tests/oracle/span.py` no se tocó.

R-396. `tests/oracle/bei.py` no importa el producto. Las tres filas y el corte 2026-02-01 devuelven 2/2. `bei.yaml` trae `file`, los dos proyectos, `value` 1.0 y `status: cumple`. `evaluate` del proyecto 1 contra el 2 iguala eso. El assert `2 / 2` de `tests/test_e3_bei.py` no está en el diff.

## Comandos

`git rev-parse HEAD` → `5edd81e6dd5c9d96d39b9d94aca6332a062aeccb`. `git merge-base --is-ancestor 8934ffc HEAD` sale 0. `git diff --stat 8934ffc..HEAD` es el diff de arriba.

Con el Python del `.venv`, sin `uv run`:

- `tests/test_e10_ui.py`, `tests/test_e10_paths.py`, `tests/test_e10_spread.py`, `tests/test_e10_edges.py`, `tests/test_e10_sign.py`, `tests/test_e5_ui.py`, `tests/test_e4_spreads.py`, `tests/test_evm.py`, `tests/test_e3_paths.py`, `tests/test_e3_bei.py`, `tests/test_e3_cpli.py`, `tests/test_e3_oracle.py`, `tests/test_phase1.py` y `tests/test_cpm.py::test_fs_chain_is_critical`: 51 passed en 29,61 s.
- La suite por defecto (`-m` ya excluye `perf` y `seccion11`): 299 passed, 9 deselected, 264,03 s. Aparece el aviso de numba de que `batch_passes` no se puede guardar en disco. Ya estaba anotado en E9. No es un fallo de E10.

Sonda, sobre el mismo par de XER que arma el test de R-387, sin AppTest y sin red. `evaluate` con el baseline: BEI 1.0 `cumple`, perdidas 1.0 `no_cumple`, GAO-10 `cumple`, índice 60. `QualityModule` con `other` cargado y sin `baseline_proj_id`: BEI `None` `no_evaluable`, perdidas `None` `no_evaluable`, GAO-10 `manual`, índice 66,666… El hallazgo es «Falta el proyecto baseline.» El Excel de ese resultado contiene `66,67` y ese texto.

## Qué no pude verificar

No corrí `scripts/qa_gate.py`. No medí la cobertura contra `docs/qa/baseline.json` ni el trinquete de 0,5 sobre el 91,1 de E9. No corrí la red de 30 000 ni una meta de la sección 11. No comparé los float paths con un export de P6: sigue en `VALIDACIONES_PENDIENTES.md` y el texto no los presenta como P6. No abrí `data/real/` ni un directorio golden.

## Segunda pasada — H-1

HEAD `576ac59`, rama `v3`. `git merge-base --is-ancestor f45a51f HEAD` sale 0. `git diff --stat f45a51f..HEAD` toca `src/atlaspmo/analysis/quality/module.py`, `src/atlaspmo/ui/app.py`, `tests/test_e10_ui.py` y `docs/qa/E10/calidad-h1.md`. No entran `check.py`, el motor ni `docs/qa/E10/qa-privacidad.md`. No se editó producto en esta pasada. No se escribió `VEREDICTO.md`. El gate no corrió: la etapa no queda cerrada.

Leí el diff y el cuerpo de `QualityModule.run` y de la pantalla. Con `baseline_proj_id` el baseline sale de `ctx.schedule.select`. Sin id, si `ctx.other` es un `Schedule`, entra a `evaluate`. La pantalla ya no importa `evaluate` ni pisa `bei`.

```
.\.venv\Scripts\python.exe -m pytest tests/test_e10_ui.py::test_baseline_requirements_progress_and_full_report tests/test_e10_ui.py::test_quality_module_reads_other_as_baseline tests/test_e10_ui.py::test_baseline_proj_id_ignores_other -q --tb=short
```

3 passed en 2,83 s. H-1 queda cerrado en `docs/qa/E10/hallazgos.md`. H-2 y H-3 siguen menores. No apareció otro crítico ni otro importante.
