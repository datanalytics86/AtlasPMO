# QC-1 E1 — contrato

Este contrato se escribió después del código de xer-io y motor-cpm, ya integrados en `366209b` y `3ddbddd`. La sección 8.4 pedía el contrato antes de implementar. Queda registrado como desviación de proceso del ciclo 1. No se reescribe esa historia.

Los resultados de E1 son condicionales al hallazgo I-3 de E0: R-198 no prueba que el script de conformidad deje cerrada `ATLASPMO_GOLDEN_DIR`. El script actual no la abre. Esta etapa no la abre.

## Brechas y requisitos

| Brecha | Requisito | Test | Oráculo | Estado al escribir el contrato |
|---|---|---|---|---|
| B-05 | R-010 | `tests/test_e1_cycles.py` | cadena en memoria y un ciclo de 3 | implementado, sin contraste P6 |
| B-06 | R-011, R-161 | `tests/test_e1_calendar.py` | suma manual de jornadas | implementado |
| B-08 | R-012, R-163 | `tests/test_e1_constraints.py` | tabla a mano | implementado, [VALIDAR] con p6_verified |
| B-09 | R-013, R-165 | `tests/test_e1_longest.py` | camino más largo en horas laborales | implementado, [VALIDAR] |
| B-20 | R-014, R-111 | `tests/test_e1_cp1252.py` | bytes de entrada | implementado |
| B-21 | R-015, R-164 | `tests/test_e1_milestone.py` | calendario 08:00-16:00 | implementado, [VALIDAR] |
| B-14 | R-016 | `tests/property/test_round_trip.py` | bytes del escritor | perfil `qa`, 500 ejemplos |
| B-14 | R-350 | `tests/test_e1_synthetic.py` | nombres de `XER_SPEC.md` | el generador ya no emite `SYNTH` |
| B-14 | R-351 | `tests/test_e1_scale_shape.py` | forma de `gen_scale.py` | WBS, feriado, cuatro vínculos, avance |
| B-16 | R-017, R-300 | `tests/perf/test_scale.py` | reloj de pared | lectura, no el tiempo de generar el archivo |
| B-15 | R-024, R-042 | `tests/property/test_logic.py`, `tests/property/test_invariant_e.py` | CPM y Monte Carlo de varianza cero | adelantados porque G5 los exige para cerrar |
| B-03, B-04 | R-021, R-022, R-023 | `tests/test_e2_joint.py`, `tests/test_e2_clean.py`, `tests/test_e2_guards.py` | CPM y bytes | la confirmación conjunta y el no-escritura están; el algoritmo de 30k no |

## Lo que este contrato no declara

- Conformidad contra P6. No hay `p6_verified`.
- Redundancia de 30k bajo 3 minutos. No medida.
- UDF como marca de hito contractual. No hay columna verificada. La lista de códigos es el camino soportado.
- QC-2 con doble firma independiente. Los esperados de los casos nuevos salen del calendario y del CPM, no de un segundo cálculo en `tests/oracle/`.
