# E10 · motor-cpm

R-394. Un FS entre dos proyectos. No se tocó el motor.

Proyecto 1 con A de 8 h y proyecto 2 con B de 8 h, calendario de `_week`, fecha de corte 2026-01-05 08:00 y FS con `pred_proj_id` del proyecto 1. Las fechas se escribieron en `tests/test_e10_edges.py` antes de mirar el resultado: A empieza el lunes 2026-01-05 08:00 y termina a las 16:00; B empieza el martes 2026-01-06 08:00 y termina a las 16:00. `schedule_cpm_reference` y `schedule_cpm_fast` (`LAST["path"] == "fast"`) coinciden con esas horas, al minuto. El borde ya estaba: el vínculo se usa cuando los dos extremos están en el pase, igual que un FS del mismo proyecto. El test lo traba. No se reescribieron los tests ya verdes de la sección 7. `test_fs_chain_is_critical` sigue en verde. No se editó `src/atlaspmo/engine/cpm.py`, `src/atlaspmo/engine/fast.py` ni `src/atlaspmo/numeric/kernels.py`.

## Comando

`.\.venv\Scripts\python.exe -m pytest tests/test_e10_edges.py tests/test_cpm.py::test_fs_chain_is_critical -q --tb=short`

```
..                                                                       [100%]
2 passed in 1.29s
```
