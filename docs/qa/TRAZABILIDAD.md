# Trazabilidad

Requisito R-xxx, etapa dueña, criterio, test planificado y fuente del oráculo. Un test planificado que aún no existe no se declara en verde. Las filas de esta tabla cubren las secciones 2, 5, 6, 7 y 11. La etapa dueña es la que debe dejar ese test en verde.

| ID | Etapa | Requisito | Test | Oráculo |
|---|---|---|---|---|
| R-001 | E0 | `pythonpath` permite importar `scripts` | tests/test_phase2.py::test_script_skips_missing_golden | colección de pytest |
| R-002 | E0 | ruff check y format sin errores | tests/test_qa_gate.py::test_g1_passes_a_clean_tree | ruff sobre un árbol temporal |
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
| R-042 | E4 | invariante e, varianza cero igual al CPM | tests/property/test_invariant_e.py | CPM determinístico |
| R-043 | E4 | curvas S y fact_timephased poblado | tests/test_e4_spreads.py | distribución lineal anotada como aproximación |
| R-050 | E5 | e2e AppTest de carga, ejecución y exportación | tests/test_e5_ui.py | sintético de tests/fixtures |
| R-051 | E5 | la app escucha en localhost y no envía estadísticas | tests/test_e5_ui.py | .streamlit/config.toml |
| R-060 | E6 | criterios automatizables de la sección 11 evidenciados | tests/perf/test_scale.py | gate G6 |
| R-061 | E2 | local, sin red en ejecución | tests/test_qa_gate.py | G8 |
| R-062 | E1 | round-trip XER byte a byte | tests/test_e1_cp1252.py | bytes originales |
| R-063 | E0 | instalación sin administrador | tests/test_e0_install.py::test_dev_tools_import_and_the_install_was_recorded | docs/qa/E0/acciones.md |
| R-100 | E0 | sección 2: sin imports de red en src | tests/test_qa_gate.py::test_g8_fails_on_a_network_import | árbol temporal |
| R-101 | E0 | sección 2: la config niega data/real y .env | tests/test_qa_gate.py::test_project_config_denies_real_data_and_dotenv | .grok/config.toml |
| R-102 | E5 | sección 2: la entrada no se reescribe y hay run_manifest | tests/test_e5_manifest.py | contrato de salida |
| R-103 | E4 | sección 2: versión, hash, parámetros, semilla y aproximaciones | tests/test_e4_metadata.py | RunMetadata |
| R-104 | E5 | sección 2: las aproximaciones se muestran | tests/test_e5_ui.py | ModuleResult.approximations |
| R-105 | E1 | sección 2 y 5: cp1252, CRLF, ERMHDR y %E | tests/test_synthetic_xer.py::test_minimal_xer_is_cp1252_crlf | bytes del fixture |
| R-110 | E1 | sección 5: bloques %T, %F, %R y %E | tests/test_synthetic_xer.py::test_minimal_xer_is_cp1252_crlf | XER_SPEC |
| R-111 | E1 | sección 5: bytes 0x81, 0x8D, 0x8F, 0x90 y 0x9D | tests/test_e1_cp1252.py | bytes de entrada |
| R-112 | E1 | sección 5: tablas mínimas, el resto genérico | tests/test_gen_scale.py::test_scale_tables_are_real_p6_names | XER_SPEC |
| R-113 | E1 | sección 5: PR_FS, PR_SS, PR_FF y PR_SF | tests/test_cpm.py::test_ss_ff_sf_and_lead | caso a mano, [VALIDAR] |
| R-114 | E1 | sección 5: TT_Task, TT_Rsrc, TT_Mile, TT_FinMile, TT_LOE, TT_WBS | tests/test_cpm.py::test_loe_and_wbs_follow_the_main_pass | caso a mano, [VALIDAR] |
| R-115 | E1 | sección 5: TK_NotStart, TK_Active, TK_Complete | tests/test_cpm.py::test_retained_logic_waits_and_override_does_not | caso a mano, [VALIDAR] |
| R-116 | E1 | sección 5: restricciones y cstr_type2 | tests/test_e1_constraints.py | [VALIDAR] |
| R-117 | E1 | sección 5: duraciones en horas y días por calendario | tests/test_calendars.py::test_add_and_subtract_stay_on_the_eight_hour_day | jornada de 8 h |
| R-118 | E1 | sección 5: fecha de corte desde PROJECT | tests/test_cpm.py::test_retained_logic_waits_and_override_does_not | XER_SPEC, [VALIDAR] |
| R-119 | E1 | sección 5: vínculo de otro proyecto marcado externo | tests/test_phase1.py::test_external_relationship_is_marked | caso a mano |
| R-120 | E5 | sección 5: el usuario asocia el baseline | tests/test_e5_ui.py | no implementado; no está en verde |
| R-121 | E1 | sección 5: huérfanos, duplicados, calendarios y ciclos | tests/test_phase1.py::test_cycle_is_reported | casos a mano |
| R-130 | E3 | DCMA 1 Logic | tests/test_e3_dcma.py | doble firma |
| R-131 | E3 | DCMA 2 Leads | tests/test_e3_dcma.py | doble firma |
| R-132 | E3 | DCMA 3 Lags | tests/test_e3_dcma.py | doble firma |
| R-133 | E3 | DCMA 4 Relationship types | tests/test_e3_dcma.py | doble firma |
| R-134 | E3 | DCMA 5 Hard constraints | tests/test_e3_dcma.py | doble firma |
| R-135 | E3 | DCMA 6 High float | tests/test_e3_dcma.py | doble firma |
| R-136 | E3 | DCMA 7 Negative float | tests/test_e3_dcma.py | doble firma |
| R-137 | E3 | DCMA 8 High duration | tests/test_e3_dcma.py | doble firma |
| R-138 | E3 | DCMA 9 Invalid dates | tests/test_e3_dcma.py | doble firma |
| R-139 | E3 | DCMA 10 Resources | tests/test_e3_dcma.py | doble firma |
| R-140 | E3 | DCMA 11 Missed tasks | tests/test_e3_dcma.py | doble firma, baseline |
| R-141 | E3 | DCMA 12 Critical Path Test | tests/test_e3_dcma.py | motor CPM |
| R-142 | E3 | DCMA 13 CPLI en tiempo laboral | tests/test_e3_cpli.py | doble firma, caso SS y feriado |
| R-143 | E3 | DCMA 14 BEI con todas las completadas | tests/test_e3_bei.py | caso completado antes de tiempo |
| R-150 | E3 | GAO 1 capturar actividades | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-151 | E3 | GAO 2 secuenciar | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-152 | E3 | GAO 3 asignar recursos | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-153 | E3 | GAO 4 establecer duraciones | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-154 | E3 | GAO 5 trazabilidad horizontal y vertical | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-155 | E3 | GAO 6 ruta crítica válida | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-156 | E3 | GAO 7 holgura razonable | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-157 | E3 | GAO 8 análisis de riesgo | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-158 | E3 | GAO 9 actualización con avance | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-159 | E3 | GAO 10 baseline | tests/test_e3_gao.py | REGLAS_CALIDAD |
| R-160 | E1 | M0 parser de clndr_data, excepciones y herencia | tests/test_calendars.py::test_exception_serial_uses_1899_12_30_and_empty_means_no_work | [VALIDAR] base Excel 1900 |
| R-161 | E1 | M0 índice laboral sin tope fijo | tests/test_e1_calendar.py | suma manual de jornadas |
| R-162 | E1 | M0 opciones retained, override, actual, lag, holgura | tests/test_cpm.py::test_retained_logic_waits_and_override_does_not | caso a mano |
| R-163 | E1 | M0 obligatorio impone fecha y reporta la violación | tests/test_e1_constraints.py | [VALIDAR] |
| R-164 | E1 | M0 hito de inicio al cierre pasa al turno siguiente | tests/test_e1_milestone.py | [VALIDAR] |
| R-165 | E1 | M0 crítico por holgura o longest path | tests/test_e1_longest.py | camino más largo a mano |
| R-166 | E2 | M3 redundancia confirmada en conjunto, no por subconjuntos | tests/test_e2_joint.py | reprogramación del CPM |
| R-167 | E2 | M4 solo se borran filas TASKPRED, o no se escribe | tests/test_e2_clean.py | comparación de bytes |
| R-168 | E4 | M5 tornado por cono y Monte Carlo con semilla | tests/test_e4_tornado.py | conteo de recalculadas |
| R-169 | E4 | M6 histogramas, curvas S, EVM y Earned Schedule | tests/test_e4_spreads.py | distribución lineal anotada |
| R-180 | E6 | M7 diferencias de update | tests/test_phase4.py::test_compare_reports_the_hand_differences | caso a mano |
| R-181 | E6 | M7 tendencias de varios updates | tests/test_e6_trends.py | biblioteca DuckDB |
| R-190 | E1 | sección 7: lags positivos y negativos en los cuatro vínculos | tests/test_cpm.py::test_ss_ff_sf_and_lead | caso a mano |
| R-191 | E1 | sección 7: feriado, media jornada, 24 h y 7 días | tests/test_e1_calendar.py | suma manual |
| R-192 | E1 | sección 7: avance fuera de secuencia | tests/test_cpm.py::test_retained_logic_waits_and_override_does_not | caso a mano |
| R-193 | E1 | sección 7: extremos abiertos | tests/test_phase1.py::test_hand_calculated_metrics | caso a mano |
| R-194 | E2 | sección 7: par SS+FF protegido | tests/test_e2_guards.py | positivo y negativo |
| R-195 | E2 | sección 7: vínculo no driver que no es redundante | tests/test_e2_guards.py | CPM |
| R-196 | E6 | sección 7: p6_verified ausente se omite con motivo | tests/test_e6_skips.py | skips.toml |
| R-197 | E3 | sección 7: esperado con doble firma | tests/test_e3_oracle.py | qa-oraculo, sin importar src |
| R-198 | E0 | sección 7: con ATLASPMO_GOLDEN_DIR definido el script no abre esa carpeta | tests/test_conformance_stub.py::test_stub_exits_and_leaves_files_untouched | bytes del archivo de prueba sin leer |
| R-300 | E1 | sección 11: lectura 30k bajo 15 s | tests/perf/test_scale.py | gen_scale.py, no medido hasta G6 |
| R-301 | E3 | sección 11: DCMA bajo 10 s | tests/perf/test_quality.py | gen_scale.py, no medido hasta G6 |
| R-302 | E2 | sección 11: redundancia bajo 3 min | tests/perf/test_redundancy.py | gen_scale.py, no medido hasta G6 |
| R-303 | E4 | sección 11: Monte Carlo 30k por 1000 bajo 5 min | tests/perf/test_montecarlo.py | gen_scale.py, no medido hasta G6 |
| R-304 | E6 | sección 11: conformidad 99,5 % y 100 % explicada | tests/test_e6_conformance.py | golden lo corre Nicolás; no medido aquí |
| R-305 | E2 | sección 11: XER limpio con delta cero o sin escritura | tests/test_e2_clean.py | comparación de bytes |
| R-306 | E1 | sección 11: round-trip idéntico | tests/test_e1_cp1252.py | bytes originales |
| R-307 | E0 | sección 11: instalación sin administrador | tests/test_e0_install.py::test_dev_tools_import_and_the_install_was_recorded | acciones.md |
| R-308 | E0 | sección 11: la suite corre | tests/test_qa_gate.py::test_g3_passes_when_pytest_passes_and_uv_is_unavailable | G3 |
| R-309 | E0 | herramienta de mutación con un mutante muerto y uno vivo | tests/test_qa_sabotage.py::test_sample_kills_a_return_and_keeps_an_equivalent_comparison | muestra, no es G13 |
| R-310 | E0 | pre-push solo acepta origin y refs/heads/v2 | tests/test_pre_push.py::test_pre_push_rejects_a_foreign_remote tests/test_pre_push.py::test_pre_push_rejects_another_branch tests/test_pre_push.py::test_pre_push_accepts_origin_v2 | sección 14.2 |
| R-311 | E0 | cada control G1–G13 tiene caso que pasa y caso que falla | tests/test_qa_gate.py | árboles temporales |
| R-312 | E0 | pre-commit corre G8 | tests/test_pre_commit_g8.py::test_pre_commit_rejects_when_g8_fails | sección 14.2 |
| R-313 | E0 | el hook rechaza .env y data/real | tests/test_reject_schedules.py::test_env_and_real_data_are_rejected | forbidden_reason |
| R-314 | E0 | G5 falla si el perfil qa tiene menos de 500 ejemplos | tests/test_qa_gate.py::test_g5_fails_when_the_qa_profile_has_too_few_examples | texto del perfil |
| R-315 | E0 | G7 exige una fila por cada skip | tests/test_qa_gate.py::test_g7_fails_when_the_listed_skip_is_a_different_test | AST y skips.toml |
| R-316 | E0 | G8 rechaza XML de cronograma fuera de fixtures | tests/test_qa_gate.py::test_g8_fails_on_schedule_xml | marcadores P6 y MSPDI |
| R-317 | E0 | G12 compara cobertura y benchmarks cuando existen | tests/test_qa_gate.py::test_g12_fails_when_coverage_drops | gate.json anterior |
| R-320 | E3 | M1 queda No evaluable si falta baseline o fecha objetivo | tests/test_e3_dcma.py | motivo escrito, no un cero |
| R-321 | E3 | M1 lag mayor que la duración de la sucesora | tests/test_e3_extra.py | caso a mano |
| R-322 | E3 | M1 vínculo SF como hallazgo de calidad | tests/test_e3_extra.py | caso a mano |
| R-323 | E3 | M1 puntos de convergencia | tests/test_e3_extra.py | conteo de predecesoras |
| R-324 | E3 | M1 calendario distinto al dominante | tests/test_e3_extra.py | caso a mano |
| R-325 | E3 | M1 LOE con lógica impropia | tests/test_e3_extra.py | caso a mano |
| R-326 | E3 | M1 actividades sin códigos o WBS requeridos | tests/test_e3_extra.py | perfil |
| R-327 | E3 | M1 densidad de lógica sin umbral por defecto | tests/test_e3_extra.py | se reporta, no se compara con un umbral |
| R-328 | E3 | perfiles dcma_estricto, corporativo y contratista | tests/test_e3_profiles.py | profiles/*.yaml |
| R-329 | E3 | índice de calidad de 0 a 100 con desglose | tests/test_e3_profiles.py | pesos del perfil |
| R-330 | E3 | M2 modo A con fechas guardadas y modo B con el motor | tests/test_phase1.py::test_mode_a_marks_negative_float_critical tests/test_phase5.py::test_mode_b_names_the_probe | fechas guardadas y motor |
| R-331 | E3 | M2 continuidad de la ruta crítica | tests/test_e3_paths.py | de la fecha de corte al término |
| R-340 | E4 | M5 triangular, uniforme y BetaPERT | tests/test_risk.py::test_samples_stay_inside_the_range_and_repeat_with_the_seed | rangos a mano |
| R-341 | E4 | M5 correlación Iman-Conover | tests/test_risk.py::test_perfect_correlation_matches_ranks | rangos iguales |
| R-342 | E4 | M5 eventos de riesgo | tests/test_risk.py::test_certain_event_moves_the_finish | caso cierto |
| R-343 | E4 | M5 P50, P80, P90, criticidad, SSI, crucialidad y Spearman | tests/test_e4_outputs.py | semilla fija |
| R-344 | E4 | M5 efecto de convergencia determinístico contra P50 | tests/test_e4_outputs.py | CPM determinístico |
| R-350 | E1 | gen_synthetic.py sin tablas inventadas | tests/test_e1_synthetic.py | XER_SPEC; hoy SYNTH sigue en el generador viejo y no está en verde |
| R-351 | E1 | red de escala con WBS, feriados, mezcla de vínculos y avance | tests/test_e1_scale_shape.py | gen_scale.py |
| R-352 | E1 | sanitize_fixture anonimiza ERMHDR antes de versionar | tests/test_phase1.py::test_sanitize_clears_header_and_user_column | encabezado anónimo |
| R-360 | E7 | ES, EF, LS, LF, TF, FF y aproximaciones idénticos al minuto frente a la referencia | tests/property/test_e7_differential.py | schedule_cpm_reference, hypothesis 500, perfil qa |
| R-361 | E7 | tablas de intervalos iguales a WorkCalendar | tests/test_e7_intervals.py | add_work, subtract_work y work_between |
| R-362 | E7 | camino rápido, ALAP antes de la holgura libre, restricciones, avance, hitos, LOE, WBS, horizonte y turno solapado | tests/test_e7_match.py | schedule_cpm_reference |
| R-363 | E7 | los tests de mano del motor siguen pasando con el motor rápido por defecto | tests/test_cpm.py | casos a mano de CPM |
| R-364 | E7 | cpm_30k y dcma_30k medidos a 30 000; se activan solo si cumplen | tests/perf/test_seccion11.py | gen_scale.py en este equipo |
