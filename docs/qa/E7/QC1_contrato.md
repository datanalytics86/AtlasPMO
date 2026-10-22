# QC-1 — contrato de E7

El oráculo es el motor de referencia (`schedule_cpm` con `engine="reference"`). No se lee un cronograma real ni `ATLASPMO_GOLDEN_DIR`. No se activa una meta de la sección 11 que no haya pasado a 30 000 actividades en este equipo.

| Requisito | Criterio ejecutable | Qué no queda en verde |
|---|---|---|
| R-360 | Hypothesis, 500 ejemplos, deriva fija: ES, EF, LS, LF, TF y FF al minuto, misma lista de aproximaciones, mismo crítico y el mismo orden de predecesoras conductoras | Conformidad contra P6 |
| R-361 | La tabla de intervalos reproduce `WorkCalendar` en snap de 0 minutos, fin de semana, feriado, media jornada y jornada de 24 h | Un calendario con turnos solapados dentro de numba |
| R-362 | Casos fijos: el camino de semana usa `path=fast`; la holgura libre ve a la sucesora después de ALAP; solape cae a la referencia sin nota nueva; horizonte corto crece; horizonte agotado nombra el límite | Que toda red de 30 000 quepa en 0,5 s antes de medirla |
| R-363 | `tests/test_cpm.py` y los de restricciones, longest path e hitos corren con el motor rápido por defecto | Borrar la referencia |
| R-364 | `test_s11_cpm_30k` y `test_s11_dcma_30k` se miden a 30 000. Entran en `seccion11.toml` solo si el tiempo queda bajo 0,5 s y 10 s | Copiar los tiempos de la revisión en Linux |

La compilación a arrays y el pase se miden aparte del empaquetado, en `perf.md`.
