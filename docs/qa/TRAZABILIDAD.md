# Trazabilidad

Requisito R-xxx, etapa dueña, criterio, test planificado y fuente del oráculo. Un test planificado que aún no existe no se declara en verde.

| ID | Etapa | Requisito | Test | Oráculo |
|---|---|---|---|---|
| R-001 | E0 | `pythonpath` permite importar `scripts` | tests/test_phase2.py::test_script_skips_missing_golden | colección de pytest |
| R-002 | E0 | ruff check y format sin errores | tests/test_qa_gate.py | salida de ruff |
| R-003 | E0 | G8 rechaza un XER fuera de fixtures | tests/test_qa_gate.py::test_g8_fails_on_a_schedule_outside_fixtures | árbol temporal |
| R-004 | E0 | G7 rechaza un skip no listado | tests/test_qa_gate.py::test_g7_fails_when_a_skip_is_not_listed | AST del test |
| R-005 | E0 | G9 rechaza una tabla ausente en XER_SPEC | tests/test_qa_gate.py::test_g9_fails_when_a_table_is_missing_from_the_spec | lista P6_TABLES |
| R-006 | E0 | generador de escala usa tablas P6, no SYNTH | tests/test_gen_scale.py::test_scale_tables_are_real_p6_names | docs/XER_SPEC.md |
| R-007 | E0 | 13 agentes y AGENTS.md apuntan a MEGAPROMPT_v2 | tests/test_qa_gate.py | sección 9.4 y 13 |
| R-010 | E1 | ciclos iterativos en una cadena de 60k | tests/test_e1_cycles.py | grafo en serie sin ciclo, y un ciclo de 3 a mano |
| R-011 | E1 | calendario con índice y horizonte dinámico de 20 años | tests/test_e1_calendar.py | suma manual de jornadas de 8 h |
| R-012 | E1 | CS_MANDSTART impone la fecha en ambos pases | tests/test_e1_constraints.py | tabla a mano, [VALIDAR] con p6_verified |
| R-013 | E1 | longest path seleccionable | tests/test_e1_longest.py | camino más largo en horas laborales |
| R-014 | E1 | bytes 0x81 preservados en el round-trip | tests/test_e1_cp1252.py | bytes de entrada |
| R-015 | E1 | hito de inicio al cierre de jornada pasa al siguiente inicio | tests/test_e1_milestone.py | calendario 08:00-16:00, [VALIDAR] |
| R-016 | E1 | invariante a, round-trip idéntico | tests/property/test_round_trip.py | hypothesis, perfil qa |
| R-017 | E1 | lectura de 30k realista bajo 15 s | tests/perf/test_scale.py | gen_scale.py |
| R-020 | E2 | redundancia 30k bajo 3 min | tests/perf/test_redundancy.py | gen_scale.py |
| R-021 | E2 | dos vínculos mutuamente redundantes dan delta cero en conjunto | tests/test_e2_joint.py | reprogramación del CPM |
| R-022 | E2 | no se escribe el XER si el delta no es cero | tests/test_e2_clean.py | comparación de bytes |
| R-023 | E2 | protecciones por evento, SS+FF, externos y hitos contractuales | tests/test_e2_guards.py | casos positivo y negativo |
| R-024 | E2 | invariantes b, c y d | tests/property/test_logic.py | hypothesis, perfil qa |
| R-030 | E3 | CPLI con tiempo laboral, no suma de duraciones | tests/test_e3_cpli.py | doble firma, caso SS y feriado |
| R-031 | E3 | BEI cuenta todas las completadas | tests/test_e3_bei.py | caso completado antes de tiempo |
| R-032 | E3 | cadena driving, float paths y bandas configurables | tests/test_e3_paths.py | algoritmo documentado |
| R-033 | E3 | DCMA sobre 30k bajo 10 s | tests/perf/test_quality.py | gen_scale.py |
| R-040 | E4 | Monte Carlo 30k por 1000 bajo 5 min | tests/perf/test_montecarlo.py | gen_scale.py |
| R-041 | E4 | tornado solo sobre el cono de sucesoras | tests/test_e4_tornado.py | conteo de actividades recalculadas |
| R-042 | E4 | invariante e, varianza cero igual al CPM | tests/property/test_risk.py | CPM determinístico |
| R-043 | E4 | curvas S y fact_timephased poblado | tests/test_e4_spreads.py | distribución lineal anotada como aproximación |
| R-050 | E5 | e2e AppTest de carga, ejecución y exportación | tests/test_e5_ui.py | sintético de tests/fixtures |
| R-051 | E5 | la app escucha en localhost y no envía estadísticas | tests/test_e5_ui.py | .streamlit/config.toml |
| R-060 | E6 | criterios automatizables de la sección 11 evidenciados | tests/perf/test_scale.py | gate G6 |
| R-061 | E2 | local, sin red en ejecución | tests/test_qa_gate.py | G8 |
| R-062 | E1 | round-trip XER byte a byte | tests/test_e1_cp1252.py | bytes originales |
| R-063 | E0 | instalación sin administrador | tests/test_gen_scale.py | uv sync --group dev |
