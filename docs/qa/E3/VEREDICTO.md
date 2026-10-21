RECHAZADA-BLOQUEADA

Diagnóstico de esta corrida, después del tercer rechazo. No es APROBADO. G4 sigue bajo 8.1: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. G13 no está medido: no hay informe de sabotaje de E3 y no se copia el kill score 54.0 de E1. La cadena driving del ciclo 2 es parcial y no tiene doble firma. Multiple float paths, la continuidad desde la fecha de corte, el caso SS, el feriado y la WBS requerida siguen sin implementarse. No hay cuarto ciclo. Los resultados de las etapas siguientes quedan condicionales a este bloqueo y a I-3.

Texto del revisor, que esta corrida no convierte en APROBADO:

Ciclo 3 de E3. Este es el rechazo 3 de 3. Esta revisión no marca la etapa bloqueada. El orquestador cambia el estado después. HEAD `98a6d28f39dc42a8e276c202fb79833b308caafe` (`test(qa): gate E3 ciclo 3, salida 1 (B-12)`). El gate no está en verde: `docs/qa/E3/gate.json` trae exit_code 1, test_count 201 y coverage_percent 89.4. Fallan G4 y G13, igual que el ciclo 2. Hay importantes abiertos. La etapa no se cierra.

No autorizo un cuarto ciclo ni bajar los umbrales de 8.1 ni los de G13 (ADR-014). ADR-013 no abre otro ciclo de esta etapa tras el tercer rechazo. Esta revisión no lo cambia y no marca la etapa bloqueada.

APROBADO no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser APROBADO.

La excepción de línea base de la sección 10.2 vale solo para E0. En E3, G4 y G13 en fail impiden el cierre. No se marcan pass.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 registra 3 passed in 3.83 s. Ese verde no prueba la definición de CPLI. G10 dice que 42 requisitos de E3 citan un archivo de test que existe; el verde de la suite lo mide G3. No comprueba doble firma.

G4 incumple 8.1. Las seis cifras no se movieron respecto del ciclo 1, del ciclo 2 ni del gate de E2: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. El umbral de 8.1 es 90 % de líneas y 85 % de ramas. cobertura_total 89.4. El modelo está en 100.0 / 100.0 y no está en el texto de fail. El resto, líneas 89.7, está sobre el 80 % y no compensa. Lo único que cambió de reloj es la suite de ese control: 18.47 s frente a 22.46 s del ciclo 2. Ese reloj no es un cumplimiento de 8.1. No se marca pass. El detalle está en I-19.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E3/sabotaje.md`. `docs/qa/E3/ciclo3.md` dice que no se copia el 54.0 de E1: el código de lógica cambió en E2 y esa cifra no llega a 85. Copiarlo sería falso. No se inventa otro score. No medido no es pass. El detalle está en I-20.

No hubo cambio de producto en este ciclo. `740c7f6` solo agrega `docs/qa/E3/ciclo3.md`. `98a6d28` reescribe `docs/qa/E3/gate.json` y toca `docs/ESTADO.md`. Entre `436e1fc` y `98a6d28` no hay diff en `src/` ni en `tests/`. `docs/qa/E3/gate.md` no se reescribió: sigue en el texto del ciclo 2. `ciclo3.md` dice que no hay una corrección correcta, en esta corrida, que deje G4 o G13 en verde. No se agregan tests vacíos.

La cadena driving del ciclo 2 sigue parcial. En la red a mano, SHORT dura 8 h y no es driving; LONG dura 16 h y sí lo es. La cadena de JOIN es LONG y JOIN. No es doble firma. No es un float path de P6. Multiple float paths y la continuidad desde la fecha de corte hasta el término siguen sin implementarse. I-22 e I-23. La WBS requerida de R-326 sigue sin implementarse. I-24. QC-2 sigue incompleto fuera del caso CPLI de ADR-017 (24 h + 16 h). No hay caso de SS solapado ni feriado. I-21. No se cierra I-14.

`docs/qa/E3/perf.md`, en este equipo el 2026-10-21, red de `gen_scale` de 30 000 actividades con `series=False`, sin XER real: `evaluate` de calidad, sin baseline, 0.261 s. Está bajo 10 s. No es un crítico de rendimiento. El mismo documento dice que CPLI en esa red queda `no_evaluable` y que el tiempo no incluye el CPM ni prueba la definición de CPLI. G6 no prueba CPLI. Los otros criterios de la sección 11 no se miden ahí. La confirmación de redundancia de 30 000 sigue sin medirse (I-17).

No hay críticos. Importantes abiertos, los mismos del ciclo 2, ninguno cerrado y ninguno nuevo: I-19 (G4), I-20 (G13 no medido), I-21 (doble firma), I-22 (cadena driving parcial del ciclo 2, que no cierra B-12), I-23 (continuidad y multiple float paths) e I-24 (WBS requerida). Heredados que siguen abiertos y no se cierran ni se reabren: I-3, I-11, I-12, I-13, I-14 parcial, I-15, I-16, I-17 e I-18 parcial. E0, E1 y E2 siguen RECHAZADA-BLOQUEADA, cada una tras su tercer rechazo, sin cuarto ciclo. Los resultados de E3 quedan condicionales a I-3 y a esos bloqueos. Esta revisión no les cambia el estado.

No se leyeron datos reales. No se bajaron umbrales. No se reejecutó pytest, el gate ni la mutación. Ciclos previos: ciclo 1 RECHAZADO en `0bd66bb`, sobre el gate `51d281f`. Ciclo 2 RECHAZADO en `b46bfb9`, sobre el gate `436e1fc` y la cadena `c0b50ca`. El detalle está en `docs/qa/E3/hallazgos.md`.
