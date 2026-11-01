# qa-spec — E8

Auditoría de QC-1 antes de dar por cerrado el código. Se contrastaron `docs/qa/E8/QC1_contrato.md`, las filas R-370 a R-375 de `docs/qa/TRAZABILIDAD.md`, ADR-021 y ADR-016 en `docs/DECISIONES.md`, y las secciones 10.3 (E8), 8.4 y 12 de `docs/MEGAPROMPT_v3.md`. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se editó producto, tests, gate, umbrales ni decisiones. No se corrió pytest ni la red de 30 000.

## Veredicto

**RECHAZADO.**

## Requisitos

R-370: **sí.** Hypothesis con perfil qa (500 ejemplos y deriva fija, ya definidos en el perfil) y redes de a lo más 8 actividades: el estado de cada `task_pred_id` del lado rápido igual al de `classify_links` con `engine="reference"`. ADR-021 fija ese camino como oráculo: recorta la tupla de vínculos y llama al motor de referencia, no al rápido. La conformidad contra P6 no deja el requisito en verde.

R-371: **sí.** En un caso con candidatos, la confirmación no vuelve a llamar a `schedule_cpm` ni reconstruye `Schedule`; la base puede llamar al motor una vez. El oráculo es el contador o el mock del test, no la salida del motor rápido. Afirmar el costo sin ese instrumento no cuenta.

R-372: **sí.** `tests/test_e2_joint.py` exige un solo `redundante_confirmado` en el par de dos FS iguales, y que la limpieza quite una fila con el mismo término. El esperado es ese conteo escrito a mano, no un resultado leído del motor rápido. Cambiar la bisección o la unión y confirmar los dos no pasa ese caso.

R-373: **no.** Que `tests/test_e2_guards.py` siga en verde es ejecutable, y el estado `protegido` del hito listado y del vínculo externo está escrito a mano: eso no sale del motor rápido. La otra frase del criterio, «el filtro por origen no cambia de resultado», no tiene caso ni oráculo. Esos dos tests no leen candidatos: la protección se decide antes del filtro. La fila dice «casos positivo y negativo» y no observa `_origin_candidates`. Prohibir tocarlo para «acelerar» no es una prueba.

R-374: **no.** El criterio es ejecutable: fechas y holguras al minuto, y, si hay cono, la misma igualdad en redes chicas y en una red mediana. El oráculo de la fila es `schedule_cpm_fast` sobre el cronograma ya recortado. Es el motor rápido. QC-2 (sección 8.4) pide como oráculo principal de E8 el motor de referencia. Un cono que solo iguala al pase rápido queda en verde, y el propio contrato dice que eso no debería contar solo si falta la igualdad, no si la igualdad es contra el mismo motor.

R-375: **sí.** `test_s11_redundancia_30k` ya mide `classify_links` (filtro y confirmación) sobre `gen_scale.py`. El límite de 180 s solo se exige con 30 000 actividades; por debajo se imprime el tiempo y no se activa la meta. El implementador no edita `seccion11.toml`, `baseline.json` ni el gate. Copiar los 52,5 s de la revisión, medidos con 300 actividades, no deja el requisito en verde. El oráculo es el reloj en este equipo, no el motor rápido ni el cuadro de la sección 8.3.

## Huecos que bloquean el cierre

**Crítico.** R-374 compara el pase enmascarado, y el cono si se usa, con el pase completo del motor rápido. En una red mediana ese cono puede coincidir con el rápido y apartarse del motor de referencia en fechas u holguras. R-370 no llega ahí: corta en 8 actividades y solo mira el estado del vínculo, no las fechas del pase. La sección 12 prohíbe optimizar sin diferencial contra la referencia. «Red mediana» tampoco tiene tamaño: nueve actividades cumplirían la letra.

**Importante.** La sección 10.3 pide la clasificación del rápido idéntica a la de la referencia en las redes chicas de hypothesis y en los casos de la sección 7. R-370 no exige el dominio: cuatro vínculos, lags positivos y negativos, feriado, media jornada, 24 h, 7 días, cada restricción, avance fuera de secuencia, LOE, WBS, hitos, pares SS+FF, cadena con redundancia real, vínculo que no es driver y no es redundante, externo, extremo abierto y ciclo. Tampoco exige que el lado rápido siga en el pase enmascarado. Si el calendario no entra en la tabla, el rápido delega en la referencia (ADR-020) y el diferencial se compara consigo mismo. El filtro de candidatos es el mismo código en los dos lados: un candidato mal marcado no se ve.

**Importante.** R-373 no congela el filtro. Un cambio de `_origin_candidates` que respete hito y vínculo externo deja el requisito en verde. La sección 10.3 permite tocarlo solo para el diferencial, y ese diferencial no lo contrasta con otro método. `tests/oracle/pathlen.py` suma dos duraciones y no llama al filtro (ADR-018). El par SS+FF está en otro archivo, no en el test citado.

**Importante.** R-371 no exige la máscara del CSR ni prohíbe recompilar calendarios, que es el contrato de ADR-021. Contar `schedule_cpm` no ve un bucle de `schedule_cpm_fast` o de la compilación. La sección 12 prohíbe reconstruir el modelo o recalcular el cronograma completo dentro del bucle de la redundancia. Ese bucle puede cumplir R-371.

**Importante.** ADR-016 exige bisección, validación del conjunto entero y que ningún inicio o fin quede sin vínculo. R-372 solo cita el par mutuo, y ese test llama a `classify_links` sin `engine="reference"`: hoy el defecto es el motor rápido, así que la fila no dice el oráculo que el test ejecuta. No hay caso de extremo abierto. Un conjunto que abre un evento y aun así pasa `_same` del pase rápido no tiene quién lo rechace frente a la referencia.
