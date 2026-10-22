RECHAZADO

El gate de E7 está en verde y no alcanza. `docs/qa/E7/gate.json` (commit `de37f8a`) sale 0: G1–G12 en pass, G13 en info. 237 tests, cobertura 91,3. La meta pendiente de cobertura no bloquea (ADR-019). No reejecuté la red de 30 000.

H-1, H-2 y el caso de H-3 quedaron cerrados, con el test nuevo, el diferencial (2 passed en 3,68 s) y la comparación directa contra `schedule_cpm_reference`. Siguen abiertos H-4 (crítico) y H-5 (importante) en `docs/qa/E7/hallazgos.md`. Una actividad no iniciada cuyo inicio real cae en el mismo minuto que el inicio temprano pierde las conductoras y, con longest path, saca a la predecesora de la ruta. H-6 y H-7 son segundos en el fin, el minuto coincide, y no deciden.
