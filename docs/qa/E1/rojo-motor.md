# Rojo — motor-cpm, antes del arreglo

Comando (worktree `e1/motor-cpm`, sin arreglo de producto todavía):

```
py -3.12 -m uv run python -m pytest -q tests/test_calendars.py tests/test_cpm.py tests/test_e1_calendar.py tests/test_e1_constraints.py tests/test_e1_longest.py tests/test_e1_milestone.py --tb=line
```

Las rutas absolutas del worktree se recortaron a rutas relativas. Últimas líneas:

```
.................FFFF.FF.FF..                                            [100%]
================================== FAILURES ===================================
E   atlaspmo.calendars.worktime.CalendarLimitError: horizonte de calendario agotado
src\atlaspmo\calendars\worktime.py:58: atlaspmo.calendars.worktime.CalendarLimitError: horizonte de calendario agotado
E   atlaspmo.calendars.worktime.CalendarLimitError: horizonte de calendario agotado
src\atlaspmo\calendars\worktime.py:58: atlaspmo.calendars.worktime.CalendarLimitError: horizonte de calendario agotado
E   atlaspmo.calendars.worktime.CalendarLimitError: horizonte de calendario agotado
src\atlaspmo\calendars\worktime.py:114: atlaspmo.calendars.worktime.CalendarLimitError: horizonte de calendario agotado
E   ValueError: hour must be in 0..23
src\atlaspmo\calendars\worktime.py:128: ValueError: hour must be in 0..23
E   AssertionError: assert datetime.datetime(2026, 1, 6, 12, 0) == datetime.datetime(2026, 1, 5, 8, 0)
tests\test_e1_constraints.py:100: AssertionError: assert datetime.datetime(2026, 1, 6, 12, 0) == datetime.datetime(2026, 1, 5, 8, 0)
E   AssertionError: assert datetime.datetime(2026, 1, 6, 16, 0) == datetime.datetime(2026, 1, 5, 16, 0)
tests\test_e1_constraints.py:120: AssertionError: assert datetime.datetime(2026, 1, 6, 16, 0) == datetime.datetime(2026, 1, 5, 16, 0)
E   TypeError: EngineOptions.__init__() got an unexpected keyword argument 'critical_rule'
tests\test_e1_longest.py:100: TypeError: EngineOptions.__init__() got an unexpected keyword argument 'critical_rule'
E   AssertionError: assert datetime.datetime(2026, 1, 5, 16, 0) == datetime.datetime(2026, 1, 6, 8, 0)
tests\test_e1_milestone.py:87: AssertionError: assert datetime.datetime(2026, 1, 5, 16, 0) == datetime.datetime(2026, 1, 6, 8, 0)
=========================== short test summary info ===========================
FAILED tests/test_e1_calendar.py::test_twenty_year_span_is_exact_and_does_not_raise
FAILED tests/test_e1_calendar.py::test_weekday_calendar_skips_weekends_and_covers_twenty_years
FAILED tests/test_e1_calendar.py::test_exception_replaces_the_weekday_including_years_ahead
FAILED tests/test_e1_calendar.py::test_full_day_shift_lands_on_the_next_midnight
FAILED tests/test_e1_constraints.py::test_mandatory_start_overrides_a_tuesday_logic_date
FAILED tests/test_e1_constraints.py::test_mandatory_finish_overrides_a_later_network_finish
FAILED tests/test_e1_longest.py::test_float_and_longest_path_disagree_on_a_pinned_side_activity
FAILED tests/test_e1_milestone.py::test_start_milestone_on_the_close_moves_to_the_next_open
8 failed, 21 passed in 0.76s
```

Lectura: el tope de 3.660 días sigue en `add_work` (línea 58) y `work_between` (línea 114). Un turno de 24 h revienta al sellar la hora 24. `CS_MANDSTART` deja el inicio el martes 12:00. `CS_MANDFIN` deja el fin el martes 16:00. No existe `critical_rule`. El hito de inicio queda a las 16:00.
