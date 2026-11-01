# QC-1 — contrato de E8

Etapa E8, brecha B-02. Ciclo 1, revisión de qa-spec: el primer texto quedó RECHAZADO. Este texto lo reemplaza.

El oráculo de la clasificación y de las fechas es el motor de referencia (`engine="reference"`), que recorta la tupla de vínculos y reprograma. No se lee un cronograma real ni `ATLASPMO_GOLDEN_DIR`. No se activa `redundancia_30k` si la corrida de 30 000 no baja de 180 s en este equipo.

Un calendario que el motor rápido no soporta (turnos solapados) no sirve de diferencial: el rápido delega en la referencia y la comparación sería contra sí mismo. Esos casos quedan fuera de R-370 y R-374.

| Requisito | Criterio ejecutable | Oráculo | Qué no queda en verde |
|---|---|---|---|
| R-370 | Hypothesis, perfil qa, redes de a lo más 8 actividades, solo calendarios que el rápido ejecuta (`LAST["path"]=="fast"`). El estado de cada `task_pred_id` coincide. Además, casos fijos de la sección 7 en `tests/test_e8_mask.py`: cuatro tipos de vínculo, lag positivo y negativo, feriado, media jornada, jornada de 24 h, una restricción de cada tipo soportado, avance fuera de secuencia, hito, LOE, WBS, par SS+FF protegido, cadena con un vínculo redundante de verdad, vínculo que no es driver y no es redundante, vínculo entre proyectos protegido, extremo que se quedaría sin vínculo, y un ciclo sin candidatos | `classify_links` con `engine="reference"` | Una red que haya caído a la referencia. Conformidad contra P6 |
| R-371 | En un caso con candidatos, la base llama al motor una vez. Durante la confirmación no se llama `schedule_cpm`, `schedule_cpm_fast`, `_compile` ni `build_tables`. `LAST["mask_passes"]` sube y el id de las tablas de calendario no cambia | Contador o mock, no la clasificación | Contar solo `schedule_cpm` mientras el bucle llama al rápido o recompila |
| R-372 | `tests/test_e2_joint.py` sigue en verde y, en ese mismo caso, el estado de cada vínculo con el rápido es el del reference. Dos vínculos que solo sobran juntos no se confirman por separado | Conteo a mano del par, y el reference en ese caso | Confirmar los dos por separado |
| R-373 | Lista de candidatos escrita a mano para una red de 6 actividades, distinta de `_candidate_ids`. El caso A–B–C de `tests/oracle/pathlen.py` sigue siendo el camino largo. El par SS+FF sale `protegido` sin entrar a candidatos | Lista a mano y `tests/oracle/pathlen.py`, que no importa `src/atlaspmo` | Dar por congelado el filtro porque pasó `test_e2_guards.py` |
| R-374 | En redes chicas y en `gen_scale` de 200 actividades, el pase enmascarado iguala al reference en ES, EF, LS, LF, holgura total y holgura libre, al minuto, para el conjunto que la confirmación quita. Si hay cono, ese cono iguala al reference en esa misma red de 200, no solo al pase rápido | Motor de referencia sobre el cronograma ya recortado | Igualar el cono únicamente al pase rápido |
| R-375 | `test_s11_redundancia_30k` se mide a 30 000. Entra en `seccion11.toml` solo si queda bajo 180 s. El implementador no edita ese archivo ni `baseline.json` ni el gate | Reloj de este equipo | Copiar los 52,5 s de la revisión, que eran de 300 actividades |
| R-376 | Quitar el único vínculo de un inicio, o el único de un fin, no queda `redundante_confirmado`, aunque el pase rápido devolviera las mismas fechas | Regla de ADR-016, caso a mano | Un conjunto que abre un evento y pasa `_same` |

Archivos del implementador: `src/atlaspmo/analysis/logic/`, `src/atlaspmo/engine/fast.py`, `src/atlaspmo/numeric/kernels.py` solo para saltar aristas con máscara 0, `tests/property/test_e8_differential.py`, `tests/test_e8_mask.py`, `docs/qa/E8/logica-red.md`, `docs/qa/E8/perf.md`, `docs/qa/E8/acciones.md`.

No tocar: `tests/fixtures/**/expected*`, `tests/oracle/**`, `docs/qa/skips.toml`, `scripts/qa_gate.py`, `docs/qa/baseline.json`, `docs/qa/seccion11.toml`, `docs/qa/E8/VEREDICTO.md`.
