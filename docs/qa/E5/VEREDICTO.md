RECHAZADO

Ciclo 2 de E5. Este es el rechazo 2 de 3. La etapa no queda bloqueada. No es el tercer rechazo y esta revisión no la marca bloqueada. El orquestador cambia el estado solo después del tercer rechazo. Queda un ciclo dentro del tope de tres. No hay cuarto ciclo. No se autoriza saltar el tope. HEAD `056866e3a3f7aac6d2ee81a6da46080c7d788ea5` (`test(qa): gate E5 ciclo 2, salida 1 (B-01)`). El gate no está en verde: `docs/qa/E5/gate.json` trae exit_code 1, test_count 210 y coverage_percent 89.7. Fallan G4 y G13. Hay importantes abiertos. La etapa no se cierra.

El cierre no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser de cierre.

La excepción de línea base de la sección 10.2 vale solo para E0. En E5, G4 y G13 en fail impiden el cierre. No se marcan pass. No se bajan umbrales.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 registra 4 passed in 3.84 s. Ese verde no es el e2e de B-01 ni una prueba de que un proceso escuche en localhost. G8 informa sin red. No es una telemetría medida en contra y no demuestra un proceso a la escucha. G10 dice que 5 requisitos de E5 citan un archivo de test que existe. El verde de la suite lo mide G3. No comprueba el perfil, la barra de progreso, las pestañas, la biblioteca, el baseline ni un socket.

`056866e` actualiza `docs/qa/E5/gate.json` y `docs/qa/E5/gate.md`, y toca `docs/ESTADO.md`. Esta revisión no editó ese archivo. La pantalla de este ciclo está en `0d387b4` (`feat(ui): PDF, Parquet, manifiesto, lote y visor CPM (B-01)`), junto con `docs/qa/E5/ciclo2.md`. El contrato es `6498d00`, anterior al código. El veredicto del ciclo 1 es `54929d9`. Esta revisión no reejecutó pytest, el gate ni la mutación.

G4 incumple 8.1. El umbral es 90 % de líneas y 85 % de ramas. Este gate: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.7. El modelo en 100.0 / 100.0 y el resto en líneas 90.1 no compensan. No se marca pass. La línea base no se aplica a E5. El detalle está en I-30.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E5/sabotaje.md`. No se inventa un kill score y no se copia el de otra etapa. No medido no es un pase. El detalle está en I-31.

El e2e de B-01 no está completo. Sobre resultados ya calculados, la pantalla ofrece Excel, PDF, un zip Parquet y el manifiesto. El visor Plotly sale solo si la tabla `cpm` trae `task_code`, `early_start` y `early_finish`. El lote llama a `run_folder`. La UI no recalcula fechas. `minimal.xer` no trae `last_recalc_date`. La corrida de Calidad sobre ese archivo ve «no hay Gantt»: la pantalla dice que esa corrida no trae tabla CPM. El visor se prueba con un XER escrito por el helper de `tests/test_cpm.py`, en AppTest, no con un navegador. Siguen fuera: perfil, barra de progreso, pestañas y biblioteca desde la UI. Eso no es el e2e completo de B-01. El detalle está en I-32.

El baseline no se asocia. La pantalla lo dice: «El baseline no se asocia en esta pantalla.» El lote repite que no asocia un baseline. El test afirma la primera frase. R-120 no está en verde. El detalle está en I-33.

R-051 queda abierto. `test_localhost_config_disables_usage_stats` lee `.streamlit/config.toml`. El archivo tiene `address = "localhost"` y `gatherUsageStats = false`. No abre un socket. No demuestra que un proceso esté escuchando. El detalle está en I-34.

No hay crítico de telemetría medida. El archivo de configuración apaga las estadísticas de uso y G8 informa sin red. No se observó una red. Eso no cierra R-051 como prueba de proceso.

`tests/test_e5_manifest.py` comprueba que los bytes de la entrada no cambian y que el PDF, el zip Parquet y el manifiesto salen de las funciones. No es una corrida de la UI. No completa el e2e.

E5 queda condicional a I-3 y al bloqueo ya registrado de E0, E1, E2, E3 y E4, cada una tras su tercer rechazo, sin cuarto ciclo. Esta revisión no les cambia el estado y no las reabre. No se leyeron datos reales. No se bajaron umbrales. No se copió un kill score. El detalle está en `docs/qa/E5/hallazgos.md`.

No hay críticos. Importantes abiertos de este ciclo, y bloquean el cierre: I-30 (G4), I-31 (G13 no medido), I-32 (e2e incompleto), I-33 (baseline no asociado) e I-34 (la prueba de localhost no abre un socket). Heredados que siguen abiertos y no se cierran ni se reabren: I-3 y los de E1 a E4, I-11 a I-29.
