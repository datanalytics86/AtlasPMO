# E10 — logica-red

R-390, R-391, R-392. B-12. HEAD de partida `b24b315`. Sin commit. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se usó red.

Los float paths los calcula el motor con el algoritmo del contrato. No son los de P6. La continuidad se juzga solo en la ruta 1, desde `last_recalc_date`. En modo A un vínculo no se marca driving. `driving_path_flag` se lee cuando la columna está: PyP6Xer la nombra.

## Rojo

Antes del cálculo, contra el código que todavía dice que no hay float paths:

```
.\.venv\Scripts\python.exe -m pytest tests/test_e10_paths.py tests/test_e3_paths.py -q --tb=short
```

```
FFFFF.F.                                                                 [100%]
================================== FAILURES ===================================
__________ test_contract_paths_number_long_then_join_and_then_short ___________
tests\test_e10_paths.py:47: in test_contract_paths_number_long_then_join_and_then_short
    assert _NOT_CALCULATED not in text
E   AssertionError: assert 'Multiple fl... se calculan' not in 'LOE: resume...r task_code.'
E     
E     'Multiple float paths no se calculan' is contained here:
E       th de P6. Multiple float paths no se calculan. La continuidad desde la fecha de corte hasta el término no se verifica. CP Test atrasa 8 horas la primera actividad crítica ordenada por task_code.
E     ?           +++++++++++++++++++++++++++++++++++
____________ test_path_one_is_continuous_from_the_reference_start _____________
tests\test_e10_paths.py:71: in test_path_one_is_continuous_from_the_reference_start
    assert _ordered(result.tables["float_paths"], 1) == [("A", 1), ("B", 2), ("C", 3)]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'float_paths'
____________ test_a_start_on_after_the_data_date_breaks_continuity ____________
tests\test_e10_paths.py:89: in test_a_start_on_after_the_data_date_breaks_continuity
    assert _ordered(result.tables["float_paths"], 1) == [("SOLO", 1)]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'float_paths'
__________________ test_missing_data_date_is_not_continuous ___________________
tests\test_e10_paths.py:100: in test_missing_data_date_is_not_continuous
    assert result.metrics["continuity"].status == "no_evaluable"
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   KeyError: 'continuity'
________________ test_mode_a_marks_the_activity_from_the_flag _________________
tests\test_e10_paths.py:121: in test_mode_a_marks_the_activity_from_the_flag
    stored = {item.task_code: item.driving_path_flag for item in present.activities}
                              ^^^^^^^^^^^^^^^^^^^^^^
E   AttributeError: 'Activity' object has no attribute 'driving_path_flag'
_________________ test_mode_a_does_not_trace_a_driving_chain __________________
tests\test_e3_paths.py:39: in test_mode_a_does_not_trace_a_driving_chain
    assert list(result.tables["bands"].columns) == [
E   AssertionError: assert ['task_code',...ical', 'path'] == ['task_code',..., 'path', ...]
E     
E     Right contains one more item: 'driving_activity'
E     Use -v to get more diff
=========================== short test summary info ===========================
FAILED tests/test_e10_paths.py::test_contract_paths_number_long_then_join_and_then_short
FAILED tests/test_e10_paths.py::test_path_one_is_continuous_from_the_reference_start
FAILED tests/test_e10_paths.py::test_a_start_on_after_the_data_date_breaks_continuity
FAILED tests/test_e10_paths.py::test_missing_data_date_is_not_continuous - Ke...
FAILED tests/test_e10_paths.py::test_mode_a_marks_the_activity_from_the_flag
FAILED tests/test_e3_paths.py::test_mode_a_does_not_trace_a_driving_chain - A...
6 failed, 2 passed in 2.71s
```

Los dos que ya pasaban son los conteos `0-5`, `>5` y `0-10`, y `test_the_longer_predecessor_is_the_driving_one`. En el rojo, el inicio de A y el de `CS_MSO` salieron de `schedule_cpm_reference`: esos assert se cumplieron y el fallo quedó después, en la tabla que todavía no existe.

## Verde

El mismo comando, después del algoritmo:

```
........                                                                 [100%]
8 passed in 1.80s
```

La ruta 1 de SHORT, LONG y JOIN es LONG orden 1 y JOIN orden 2. SHORT es la ruta 2, orden 1. LOE y WBS no entran. `driving_codes` de JOIN sigue en `LONG`. La cadena `{LONG, JOIN}` la conserva `test_the_longer_predecessor_is_the_driving_one`: el caso con WBS no se usa para eso, porque el resumen ya caía en la caminata vieja. No aparecen «Multiple float paths no se calculan» ni «La continuidad desde la fecha de corte hasta el término no se verifica».

La cadena A–B–C queda `A, B, C` y la continuidad es `verdadera`. El `CS_MSO` posterior al corte queda en `falsa` con «quiebre». Sin `last_recalc_date` el estado es `no_evaluable`, la nota dice que falta la fecha de corte y el valor no es verdadero. El modo A pone `driving_activity` con `Y` o `y`, lo deja en falso si no, no llama a `schedule_cpm` y conserva «Los vínculos driving no se marcan en modo A». Los conteos `0-5`, `>5` y `0-10` siguen.

El algoritmo está en el docstring de `_contract_float_paths`. La salida no se presenta como un float path de P6.

## Archivos

- `src/atlaspmo/analysis/paths/mode_a.py`
- `src/atlaspmo/analysis/paths/mode_b.py`
- `src/atlaspmo/model/schedule.py`
- `src/atlaspmo/io/xer.py`
- `src/atlaspmo/io/load.py`
- `docs/XER_SPEC.md`
- `tests/test_e10_paths.py`
- `tests/test_e3_paths.py`
- `docs/qa/E10/logica-red.md`

`xer.py` lee la celda solo si la columna está. `load.py` la guarda en la actividad: es ahí donde se arma `Activity` desde `TASK`. El campo nuevo va al final, con default `None`. `tests/test_e3_paths.py` solo suma `driving_activity`.

`git status --porcelain` al cerrar solo lista esos archivos. No hubo commit ni push.
