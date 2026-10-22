RECHAZADO

El gate de E7 está en verde y no alcanza. `docs/qa/E7/gate.json` (HEAD `73666eb`) sale 0: G1–G12 en pass, G13 en info («no medido»). 236 tests, cobertura 91,2. G6 corrió `lectura_30k`, `cpm_30k` y `dcma_30k`. La «meta pendiente» de cobertura no bloquea (ADR-019). La sección 8.4 de `docs/MEGAPROMPT_v3.md` exige además cero hallazgos críticos o importantes.

Hay uno de cada uno, abiertos, en `docs/qa/E7/hallazgos.md`. El pase de `src/atlaspmo/numeric/kernels.py` trunca los reales a minuto y con eso no reproduce el crítico por longest path ni las predecesoras conductoras de `schedule_cpm_reference` (`src/atlaspmo/engine/cpm.py`). R-360 lo pide, y el diferencial de `tests/property/test_e7_differential.py` no genera ese borde. Las metas de tiempo de E7 no son el motivo del rechazo.
