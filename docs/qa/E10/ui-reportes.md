# E10 — UI, reportes, visor y biblioteca

Requisitos R-387, R-388 y R-389. HEAD de partida `b24b315`. Sin commit.

## Archivos

- `src/atlaspmo/ui/app.py`
- `src/atlaspmo/reports/gantt.py`
- `src/atlaspmo/library/store.py`
- `tests/test_e10_ui.py`
- `tests/test_e5_ui.py` (solo el docstring y el assert de «baseline no se asocia»)
- `docs/qa/E10/ui-reportes.md`

## Comando

```
.\.venv\Scripts\python.exe -m pytest tests/test_e10_ui.py tests/test_e5_ui.py -q --tb=short
```

## Rojo

Corrida anterior al arreglo de la pantalla. 4 failed, 5 passed, 18.29 s.

```
FFF.F....                                                                [100%]
================================== FAILURES ===================================
_____________ test_baseline_requirements_progress_and_full_report _____________
tests\test_e10_ui.py:185: in test_baseline_requirements_progress_and_full_report
    assert "baseline no se asocia" not in _captions(app)
E   AssertionError: assert 'baseline no se asocia' not in 'Análisis lo... cronograma.'
E     'baseline no se asocia' is contained here:
E       El baseline no se asocia en esta pantalla.
______________ test_filter_walks_neighbors_and_driving_is_mode_b ______________
tests\test_e10_ui.py:266: in test_filter_walks_neighbors_and_driving_is_mode_b
    _labeled(app.number_input, "Niveles").set_value(0)
E   AssertionError: Niveles
E   assert 0 == 1
_____________ test_batch_orders_by_evaluate_and_library_skips_xer _____________
tests\test_e10_ui.py:338: in test_batch_orders_by_evaluate_and_library_skips_xer
    assert _labeled(library.checkbox, "Guardar el cronograma").value is False
E   AssertionError: Guardar el cronograma
E   assert 0 == 1
____________________ test_load_run_and_show_approximations ____________________
tests\test_e5_ui.py:27: in test_load_run_and_show_approximations
    assert "baseline no se asocia" not in joined
E   AssertionError: assert 'baseline no se asocia' not in '...'
E     'baseline no se asocia' is contained here:
E       El baseline no se asocia en esta pantalla.
=========================== short test summary info ===========================
FAILED tests/test_e10_ui.py::test_baseline_requirements_progress_and_full_report
FAILED tests/test_e10_ui.py::test_filter_walks_neighbors_and_driving_is_mode_b
FAILED tests/test_e10_ui.py::test_batch_orders_by_evaluate_and_library_skips_xer
FAILED tests/test_e5_ui.py::test_load_run_and_show_approximations
4 failed, 5 passed in 18.29s
```

El lote de dos sintéticos ya ordenaba por el índice; el fallo de R-389 es la opción que guarda el XER. El filtro por código ya existía; faltan N niveles. La frase del baseline seguía en la pantalla.

## Verde

Mismo comando, después de la pantalla, el Gantt, la tabla `schedule_files` y el assert de E5.

```
.........                                                                [100%]
9 passed in 23.73s
```

La pantalla asocia el segundo XER y el BEI mostrado es el de `evaluate(actual, perfil, baseline)`. EVM dice «requiere recursos», la comparación «requiere dos versiones», y Calidad no lleva esa línea. Tras ejecutar, `st.progress(1.0)` queda en 100 en AppTest y hay una pestaña por módulo. «Informe completo» deja un binario `PK` y otro `%PDF`, sin quitar las cuatro descargas de E5.

El filtro por código usa contención. Con N = 0 desde B queda B; con N = 1 la caminata del test sobre `schedule.relationships` da A, B y C, y el visor muestra ese conjunto. El color distinto del Gantt es el conjunto `task_code` de `driving_chain` de `PathsModeB`.

El ranking de `a_open.xer` y `z_cycle.xer` sigue el índice de `evaluate` de cada archivo, de mayor a menor. Con la casilla apagada ninguna celda tiene `ERMHDR`. Prendida, una celda es el XER que escribió el test. `metrics` y el conteo de actividades no se borran. Los índices de E5 siguen: uploader 0, multiselect 0, selectbox 0, text_input 0 y 1, botones 0, 1 y 2.
