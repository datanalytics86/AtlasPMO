# Hallazgos E7 ciclo 1

El gate de `docs/qa/E7/gate.json` (HEAD `73666eb`) sale 0: G1–G12 en pass, G13 en info («no medido»). 236 tests, cobertura 91,2. G6 corrió `lectura_30k`, `cpm_30k` y `dcma_30k`. La «meta pendiente» de cobertura no bloquea (ADR-019). Los tiempos de Linux en `docs/qa/v3_linea_base.md` no son este equipo. Eso no cierra la etapa: hay un hallazgo crítico y uno importante abiertos.

## H-1 — crítico

El pase numba compara instantes ya truncados al minuto. La referencia compara el `datetime` del real, segundos incluidos. Con `critical_rule="longest"` el motor rápido marca críticas de más, y en retained logic reporta predecesoras conductoras que la referencia no tiene. Cambia el resultado. Lo prohíbe la sección 12 de `docs/MEGAPROMPT_v3.md` («sin cambiar un solo resultado») y R-360 en `docs/qa/TRAZABILIDAD.md` (mismo crítico y el mismo orden de predecesoras conductoras).

Dónde se trunca:

- `src/atlaspmo/engine/fast.py` guarda `act_start_date` y `act_end_date` con `to_minute` (segundos fuera).
- `src/atlaspmo/numeric/kernels.py` siembra el longest path con `ef[index] == pf`, y `pf` es el máximo de esos minutos. La referencia, en `src/atlaspmo/engine/cpm.py` (`_longest_ids` y `_project_finish`), exige `early_finish == project_finish` con el datetime completo.
- El mismo kernel asigna `es` al minuto truncado del real y marca conductora si `bound == es`. La referencia (`_driving_ids`) compara contra `early_start`, que conserva los segundos. Al empaquetar, `_keep` en `fast.py` vuelve a publicar el real con segundos, así que la fecha de salida coincide y la lista de conductoras no.

Reproducción mínima, calendario 08:00–16:00, fecha de corte 2026-01-05 08:00, contra `schedule_cpm_reference`:

1. A completa con fin real 2026-01-05 16:00:45 y B de 8 h sin vínculos, `critical_rule="longest"`. Las dos terminan en el minuto 16:00. La referencia deja B no crítica y con fin tarde 16:00:45. El motor rápido deja B crítica y con fin tarde 16:00:00.
2. Hito con `CS_MSO` a las 16:00 del 2026-01-05 (cae al 2026-01-06 08:00) y sucesora en curso, `PR_SS` con lag 0, inicio real 2026-01-06 08:00:45, retained logic. Fechas iguales al segundo. Conductoras: referencia `()`, motor rápido `('1',)`.

ES, EF, LS, TF y FF de esos casos quedan en el mismo minuto. El desvío que bloquea es el crítico y las conductoras.

## H-2 — importante

Ese borde no está cubierto, y por eso el diferencial queda verde.

- `tests/property/test_e7_differential.py` sí exige el mismo crítico y las mismas `driving_pred_ids`, pero el inicio real de una actividad en curso se arma sin segundos. El fin real de una completa sí lleva 0 o 45 s; en los 500 ejemplos de G3 no apareció el empate del hallazgo H-1, porque si no el test habría fallado.
- `tests/test_e7_match.py` tiene un fin real con segundos (15:30:45) y recorre `longest`, sin otra actividad que termine en ese mismo minuto, y sin un inicio real con segundos en retained logic.

R-360 queda afirmado por un test que no alcanza el caso. Es un caso borde sin cubrir (sección 8.5 de `docs/MEGAPROMPT_v3.md`).

## H-3 — menor

En el caso 1, el fin tarde de B pierde los segundos del fin de proyecto (16:00:45 contra 16:00:00). El ancla del pase atrás y el ALAP usan el minuto truncado; la referencia copia el datetime. R-360 pide igualdad al minuto, y el minuto coincide. No bloquea. Conviene dejarlo igual que la referencia al corregir H-1, para no publicar otra hora.

No hay otros hallazgos abiertos. No se reejecutó la red de 30 000: el límite de `cpm_30k` y `dcma_30k` lo afirma el gate, no este informe.
