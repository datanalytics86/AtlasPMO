# Hallazgos E7 ciclo 2

El gate de `docs/qa/E7/gate.json` (commit `de37f8a`, el mismo archivo en HEAD `6052e9b`) sale 0: G1–G12 en pass, G13 en info («no medido»). 237 tests, cobertura 91,3. La meta pendiente de cobertura no bloquea (ADR-019). No reejecuté `cpm_30k` ni `dcma_30k`; el pass de G6 es el del gate. Reejecuté `tests/test_e7_match.py::test_actual_seconds_do_not_widen_the_longest_path_or_driving` y `tests/property/test_e7_differential.py`: 2 passed en 3,68 s. Además comparé el motor rápido contra `schedule_cpm_reference` con datetime completo, crítico, conductoras, holguras y aproximaciones. Calendario 08:00–16:00 los siete días y fecha de corte `2026-01-05 08:00`, salvo que se diga otra cosa.

## H-1 — cerrado

Los dos casos del ciclo 1 quedan iguales a la referencia, segundos incluidos.

1. A `TK_Complete`, fin real `2026-01-05 16:00:45`, y B de 8 h sin vínculos. Igualdad con `critical_rule="longest"` y con `float`. El test nuevo cubre longest mediante `_same`.
2. Hito `TT_Mile` con `CS_MSO` a las `2026-01-05 16:00` y sucesora `TK_Active` con inicio `2026-01-06 08:00:45`, `PR_SS` lag 0. Igualdad con el defecto (`float`, retained) y con `longest`.

En una actividad iniciada, el mecanismo del commit no ensancha el crítico. `_pre_finish` conserva los segundos del fin real en el fin previo al ALAP, `_longest` siembra con ese datetime, y `src/atlaspmo/numeric/kernels.py` copia `es` en `logic_es` cuando `started==1` antes del ALAP. `_driving` devuelve `()` si el inicio real tiene segundos o microsegundos y ese minuto es el ancla. También coincidieron: FS además de SS, solo microsegundos, `actual_dates` con las dos fechas, una terminada que no arrastra a su predecesora, una terminada que sí conduce a la sucesora, dos completas en el mismo minuto (`16:00:30` y `16:00:45`), ALAP de una iniciada, y un `CS_MEO` que empuja el inicio de una en curso hasta el fin real de otra.

## H-2 — cerrado

`tests/property/test_e7_differential.py` sortea segundos 0 o 45 en el `act_start` de `TK_Active`. El test fija 500 ejemplos y `derandomize=True`; `tests/property/conftest.py` carga el perfil `qa` con los mismos tres valores. Pasó. No afirmo que esa semilla haya sorteado un empate: el caso fijo de H-1 sí corre siempre y exige datetime, crítico y orden de conductoras.

## H-3 — cerrado en el caso informado

En el caso 1 el fin tarde de B quedó igual al de la referencia: el fin de proyecto `2026-01-05 16:00:45`. ALAP sin otra restricción también: inicio temprano `2026-01-05 08:00:00`, fin temprano y fin tarde `2026-01-05 16:00:45` en los dos motores, y B no crítica por longest. Los segundos que todavía se pierden o se agregan están en H-6 y H-7. No son este caso.

## H-4 — crítico

`_driving` borra todas las conductoras cuando hay un `act_start_date` con segundos, aunque la actividad no esté iniciada y la referencia ignore ese real. Con longest path la predecesora sale de la ruta. Cambia el resultado. Lo prohíbe la sección 12 de `docs/MEGAPROMPT_v3.md` (optimizar el motor cambiando resultados) y el contrato de E7 en `docs/qa/E7/QC1_contrato.md` (mismo crítico y el mismo orden de predecesoras conductoras).

P de 8 h, sin real. B de 8 h, `TK_NotStart`, `act_start_date=2026-01-06 08:00:45`. Vínculo P→B `PR_FS` lag 0. El inicio por red de B cae en ese minuto.

- `critical_rule="longest"`: P es crítica en la referencia y no en el rápido. Conductoras de B: referencia `('P',)`, rápido `()`. Inicio temprano de B: referencia `2026-01-06 08:00:00`, rápido `2026-01-06 08:00:45`. El resto (fechas, holguras, aproximaciones, fin de proyecto y el crítico de B) coincidió.
- `critical_rule="float"`: el crítico coincidió. Siguen distintos el inicio temprano, solo en segundos, y las conductoras, `('P',)` contra `()`.
- B hito de inicio (`TT_Mile`, duración 0) con el mismo real y el mismo vínculo, longest: otra vez P deja de ser crítica y las conductoras pasan de `('P',)` a `()`.

La referencia, en `_forward` y `_driving_ids` de `src/atlaspmo/engine/cpm.py`, usa el real solo si la actividad está iniciada o completa. El rápido publica ese real con `_keep` cuando el minuto coincide (`src/atlaspmo/engine/fast.py`; ya estaba en `73666eb`) y, desde `de37f8a`, `_driving` retorna `()` antes de leer `drive` si el real tiene segundos y el minuto iguala el ancla. En una no iniciada el ancla es `es`. En `73666eb` la lista era solo las aristas con `drive==1`, y ese flag se prende por igualdad de minutos. No reejecuté ese commit.

No es un borrado ciego: con el real en otro minuto (`2026-01-05 09:15:45`) los dos motores coinciden. Una iniciada con segundos en el minuto del predecesor sigue en `()` en los dos lados, que es el arreglo de H-1. Una iniciada sin segundos conserva la conductora.

## H-5 — importante

Ese borde no está cubierto. `test_actual_seconds_do_not_widen_the_longest_path_or_driving` solo arma `TK_Complete` y `TK_Active`. El diferencial solo pone `act_start` en esos dos estados. Los 500 ejemplos quedan verdes con H-4 abierto. Es un caso borde sin cubrir (sección 8.5 de `docs/MEGAPROMPT_v3.md`): el test afirma las conductoras y no alcanza la rama que las borra.

## H-6 — menor

Fin de proyecto `2026-01-05 16:00:45` (A completa) y B de 8 h sin sucesoras. La referencia conserva los segundos en el fin tarde. El rápido los trunca a `16:00:00` si hay un código de restricción que no mueve ese fin:

- `CS_MEOB` al `2026-01-08 16:00`
- `CS_MSOA` al `2026-01-05 08:00`, que no atrasa el inicio
- `CS_MSO` sin fecha
- `CS_ALAP` más `CS_MSOA` al `2026-01-05 08:00`: también el fin temprano, `16:00:45` contra `16:00:00`
- `CS_ALAP` más `CS_MSO` sin fecha: igual en fin temprano y fin tarde

`_finish_anchor` rechaza cualquier código distinto de vacío o `CS_ALAP`, aunque la referencia no use esa restricción en el pase atrás (sin fecha, cota posterior al fin de proyecto, o solo de avance). El ALAP copia después ese fin tarde ya truncado. El minuto, la holgura, el crítico y las conductoras coinciden. R-360 pide igualdad al minuto. No bloquea.

Donde la restricción sí mueve, no vi desvío. `CS_MEO` a las `16:00` y a las `16:00:45` dejan el fin tarde en `16:00:00` en los dos motores: la cota sin segundos gana el mínimo. `CS_MSO` a las `16:00` y `CS_MEO` al `2026-01-08 16:00` corren a B, y el fin de proyecto ya no trae segundos.

## H-7 — menor

Hito de inicio no iniciado, sin sucesoras ni restricción, fin de proyecto dentro de la jornada (`2026-01-05 15:30:45`). La referencia ajusta el fin tarde con `add_work` y lo deja en `15:30:00`. El rápido lo vuelve a escribir con `:45`, porque el minuto coincide y `_finish_anchor` no mira el tipo. Con `CS_ALAP`, el fin temprano también: referencia `15:30:00`, rápido `15:30:45`.

No pasa con el hito de fin (`TT_FinMile`), ni con el de inicio si el fin de proyecto es el cierre `16:00:45` (los dos caen al `2026-01-06 08:00`), ni con un hito de inicio ya en curso. Minuto, holgura, crítico y conductoras coinciden. No bloquea.

## Lo demás que coincidió

Rollup WBS y LOE con un hijo completo a las `16:00:45`. Fecha de corte con segundos. Retained y progress override fuera de secuencia. ALAP con sucesora. 200 redes chicas, semilla 1, reales solo si el estado los usa: 194 idénticas al datetime y 6 solo con segundos de más o de menos en un fin, la misma familia que H-6 y H-7. En esas 200 no hubo diferencias de minuto, holgura, aproximaciones, crítico ni conductoras. El generador a veces sortea lag vacío y el motor no tiende ese vínculo. H-4, H-6 y H-7 no dependen de eso.

No hay otros hallazgos abiertos.
