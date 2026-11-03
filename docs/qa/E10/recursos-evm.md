# E10 — recursos-evm

R-393. B-13. HEAD de partida `b24b315`. Sin commit. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se usó red.

La duración remanente se reparte desde el inicio temprano del CPM, lineal en tiempo laboral, por día, semana ISO y mes. La curva de esas horas es la acumulada de los días (`curve`). Sin filas de `TASKRSRC` el histograma queda vacío y la nota dice que no hay asignación. `resource_limit` sigue `no_evaluable`: no hay un campo citado de tope en `RSRCRATE`.

`scurve` se dejó en un solo punto, en la fecha de corte. `tests/test_evm.py` lo exige (PV 50, un punto, CPI 1,25) y el contrato no autoriza moverlo. El caso nuevo no usa ese punto: su curva es `curve`.

`write_star` sigue grabando `spread_hours` en el balde fijo `corte`. Ese archivo no está en esta entrega. La actividad ya no publica `spread_hours`, así que el caso nuevo no cae en ese balde. Los periodos salen en las tablas `days`, `weeks`, `months`, `curve` e `histogram`.

## Rojo

Antes del arreglo, contra el código viejo:

```
.\.venv\Scripts\python.exe -m pytest tests/test_e10_spread.py tests/test_e4_spreads.py tests/test_evm.py -q --tb=short
```

```
FF.....                                                                  [100%]
================================== FAILURES ===================================
__________________ test_remaining_hours_follow_working_days ___________________
tests\test_e10_spread.py:18: in test_remaining_hours_follow_working_days
    assert [(row["bucket"], row["hours"]) for row in outcome.days] == [
                                                     ^^^^^^^^^^^^
E   AttributeError: 'EvmOutcome' object has no attribute 'days'
__________________ test_remaining_hours_follow_the_fs_chain ___________________
tests\test_e4_spreads.py:20: in test_remaining_hours_follow_the_fs_chain
    assert "balde corte" not in text
E   AssertionError: assert 'balde corte' not in 'cp_phys, cp...cido (none).'
E
E     'balde corte' is contained here:
E       nte en el balde corte. no es una curva por periodo. a: tipo de % completo no reconocido (none). b: tipo de % completo no reconocido (none).
E     ?           +++++++++++
=========================== short test summary info ===========================
FAILED tests/test_e10_spread.py::test_remaining_hours_follow_working_days
FAILED tests/test_e4_spreads.py::test_remaining_hours_follow_the_fs_chain
2 failed, 5 passed in 1.67s
```

`tests/test_evm.py` ya estaba en verde en ese rojo (5 passed).

## Verde

El mismo comando, después del reparto:

```
.......                                                                  [100%]
7 passed in 5.26s
```

Quedan PV 50, `scurve` de un punto, CPI 1,25 y `resource_limit` `no_evaluable`. No aparecen «balde corte» ni «No es una curva por periodo».

## Archivos

- `src/atlaspmo/analysis/resources/evm.py`
- `src/atlaspmo/analysis/resources/module.py`
- `tests/test_e10_spread.py`
- `tests/test_e4_spreads.py`
- `docs/qa/E10/recursos-evm.md`

`git status --porcelain` también lista `scripts/build_cases.py`, `tests/oracle/`, `tests/fixtures/synthetic/cases/` de CPLI y BEI, `tests/test_e10_sign.py` y `docs/qa/E10/qa-oraculo.md`. No los escribí ni los revertí.
