# E10 — H-1, el segundo XER entra en la corrida

Sin commit. HEAD de partida `f45a51f`. No se tocó H-2 ni H-3. La fórmula de `check.py` no se movió.

## Rojo

Antes de `module.py` y de quitar el parche de la pantalla. El módulo no leía `ctx.other`. La tabla solo pisaba el BEI.

```
.\.venv\Scripts\python.exe -m pytest tests/test_e10_ui.py -q --tb=short
```

```
F..F.                                                                    [100%]
================================== FAILURES ===================================
_____________ test_baseline_requirements_progress_and_full_report _____________
tests\test_e10_ui.py:237: in test_baseline_requirements_progress_and_full_report
    _same_quality(quality.metrics, expected)
tests\test_e10_ui.py:64: in _same_quality
    assert got[key].status == expected[key].status
E   AssertionError: assert 'no_evaluable' == 'cumple'
E
E     - cumple
E     + no_evaluable
_________________ test_quality_module_reads_other_as_baseline _________________
tests\test_e10_ui.py:407: in test_quality_module_reads_other_as_baseline
    _same_quality(result.metrics, expected)
tests\test_e10_ui.py:64: in _same_quality
    assert got[key].status == expected[key].status
E   AssertionError: assert 'no_evaluable' == 'cumple'
E
E     - cumple
E     + no_evaluable
=========================== short test summary info ===========================
FAILED tests/test_e10_ui.py::test_baseline_requirements_progress_and_full_report
FAILED tests/test_e10_ui.py::test_quality_module_reads_other_as_baseline - As...
2 failed, 3 passed in 6.18s
```

El primer fallo es el BEI de la corrida: `no_evaluable` contra `cumple` de `evaluate` con el segundo archivo. Pytest se detuvo ahí dentro del mismo test, antes del dataframe, del hallazgo y del Excel. `test_baseline_proj_id_ignores_other` ya pasaba: con id, el baseline sigue saliendo de `select` y no de `ctx.other`. El log de Streamlit fue el aviso de `ScriptRunContext` en bare mode.

## Verde

```
.\.venv\Scripts\python.exe -m pytest tests/test_e10_ui.py tests/test_e5_ui.py -q --tb=short
```

```
...........                                                              [100%]
11 passed in 9.51s
```

Con `baseline_proj_id` puesto, el baseline sigue siendo `ctx.schedule.select`. Sin id, si `ctx.other` es un `Schedule`, ese cronograma entra a `evaluate`. Si no hay ninguno, el baseline queda en `None`. La pantalla ya no calcula un BEI aparte ni reemplaza la celda: la tabla muestra `result.metrics`.

La corrida con los dos XER iguala `evaluate` en `bei`, `missed_tasks`, `gao_10` y `quality_index`, en valor y estado. El BEI del dataframe es el de ese resultado. «Falta el proyecto baseline.» no está en los hallazgos ni en `informe.xlsx`. El Excel sigue en `PK` y el PDF en `%PDF`. E5 sigue en verde, incluidas las cuatro descargas de la corrida de calidad y `test_localhost_config_disables_usage_stats`.

## Archivos

- `src/atlaspmo/analysis/quality/module.py`
- `src/atlaspmo/ui/app.py`
- `tests/test_e10_ui.py`
- `docs/qa/E10/calidad-h1.md`
