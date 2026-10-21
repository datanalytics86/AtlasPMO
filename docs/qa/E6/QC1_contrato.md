# QC-1 — contrato de E6

Escrito el 2026-10-21, antes del código de E6. Los resultados quedan condicionales a I-3 y a E0, E1, E2, E3, E4 y E5 en RECHAZADA-BLOQUEADA. No se leen datos reales ni `ATLASPMO_GOLDEN_DIR`. No se baja un umbral y no se copia un kill score.

| Requisito | Qué se va a probar | Qué no se va a marcar en verde |
|---|---|---|
| R-181 | `Library.trend` devuelve los puntos en el orden de inserción | Una tendencia de cronogramas reales |
| R-196 | `skips.toml` declara el motivo de omisión, y el script imprime que `p6_verified` se omite si la carpeta no está | Un `skip` nuevo. El archivo no se edita |
| R-304 | Con la variable ausente el script dice `golden: omitido`. Si apunta a una carpeta temporal creada por la prueba, no imprime su nombre y no cambia sus bytes | El 99,5 % ni el 100 %. Aquí no se miden |
| R-060 | Sigue en `tests/perf/test_scale.py`. La lectura de 30 000 ya midió 0.197 s en E1 | El resto de la sección 11 |
| R-180 | Sigue en `tests/test_phase4.py`. No se reescribe | Una comparación contra P6 |

El manual se actualiza para describir la pantalla que hay, con los límites: el baseline no se asocia, no hay avance parcial, el visor solo aparece con tabla CPM, y la conformidad con P6 no está medida. No se afirma el e2e de B-01 ni un gate en verde.
