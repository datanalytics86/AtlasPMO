APROBADO

El gate de E7 está en verde. `docs/qa/E7/gate.json` (commit `577c6ba`) sale 0: G1–G12 en pass, G13 en info. 239 tests, cobertura 91,2. La meta pendiente de cobertura no bloquea (ADR-019). No reejecuté la red de 30 000.

H-4 y H-5 quedan cerrados. Una no iniciada con real en el mismo minuto conserva las conductoras y, con longest, a la predecesora. Lo cubre `test_not_started_actual_does_not_erase_driving` y el diferencial, que ahora sortea `TK_NotStart`. Esos tests y el de segundos del ciclo 1 pasaron: 4 passed en 4,08 s. H-6 y H-7 quedan cerrados en los casos del ciclo 2.

Queda abierto H-8, menor, en `docs/qa/E7/hallazgos.md`. En duración 0 con un MSO que no mueve el minuto, en una iniciada con mandato, o con una sucesora SS/SF que no ata el fin, el rápido pierde los segundos del fin de proyecto. El minuto, la holgura, el crítico y las conductoras coinciden. No bloquea. En 458 redes no hubo otra diferencia.
