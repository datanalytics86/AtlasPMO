# QC-1 — contrato de E8

Etapa E8, brecha B-02. El oráculo es `classify_links` con `engine="reference"` (reconstruye el cronograma y llama al motor de referencia). No se lee un cronograma real ni `ATLASPMO_GOLDEN_DIR`. No se activa `redundancia_30k` si la corrida de 30 000 no baja de 180 s en este equipo.

| Requisito | Criterio ejecutable | Qué no queda en verde |
|---|---|---|
| R-370 | Hypothesis, perfil qa, redes de a lo más 8 actividades: el estado de cada `task_pred_id` del motor rápido es el mismo que el de la referencia | Conformidad contra P6 |
| R-371 | En un caso con candidatos, la confirmación rápida no vuelve a llamar a `schedule_cpm` ni reconstruye `Schedule`. La base puede llamar al motor una vez | Afirmar el costo sin el contador o el mock del test |
| R-372 | `tests/test_e2_joint.py` sigue en verde: dos vínculos que solo sobran juntos no se confirman por separado | Cambiar la bisección o la unión de ADR-016 |
| R-373 | `tests/test_e2_guards.py` sigue en verde. El filtro por origen no cambia de resultado | Tocar `_origin_candidates` para "acelerar" el filtro |
| R-374 | El pase enmascarado iguala al pase completo del motor rápido en fechas y holguras al minuto. Si se usa cono, el mismo test lo iguala al pase completo en redes chicas y en una red mediana | Un cono sin esa igualdad |
| R-375 | `test_s11_redundancia_30k` se mide a 30 000. Entra en `seccion11.toml` solo si queda bajo 180 s. El implementador no edita ese archivo ni `baseline.json` ni el gate | Copiar el tiempo de la revisión, que era de 300 actividades |

Archivos del implementador: `src/atlaspmo/analysis/logic/`, `src/atlaspmo/engine/fast.py` y `src/atlaspmo/numeric/kernels.py` solo para enmascarar aristas sin cambiar el pase cuando la máscara está toda activa, `tests/property/test_e8_differential.py`, `tests/test_e8_mask.py`, `docs/qa/E8/logica-red.md`, `docs/qa/E8/perf.md`.

No tocar: `tests/fixtures/**/expected*`, `tests/oracle/**`, `docs/qa/skips.toml`, `scripts/qa_gate.py`, `docs/qa/baseline.json`, `docs/qa/seccion11.toml`, `docs/qa/E8/QC1_contrato.md`, `docs/qa/E8/VEREDICTO.md`.
