RECHAZADA-BLOQUEADA

Diagnóstico de esta corrida, después del tercer rechazo. No es APROBADO. G4 sigue bajo 8.1: calendars 85.2/70.9, engine 89.4/79.5, logic 88.6/75.3. G13 no está medido y no se copia un kill score de otra etapa. El e2e de B-01 no está completo: hay perfil, pestañas, ranking, biblioteca de métricas, filtro por código y tabla driving cuando el módulo la trae. El baseline no se asocia. La prueba de localhost lee el archivo de configuración y no abre un socket. No hay bandas de holgura ni filtro por WBS. No se abrió un navegador. No hay cuarto ciclo. Las etapas siguientes quedan condicionales a este bloqueo y a I-3.

Texto del revisor, que esta corrida no convierte en APROBADO:

Ciclo 3 de E5. Este es el rechazo 3 de 3. Esta revisión no marca la etapa bloqueada. El orquestador cambia la primera línea después, fuera de esta revisión. No cabe un cuarto ciclo. No se autoriza saltar el tope. HEAD `b323f41e268daef2c627d343e5e77464c04480e5` (`test(qa): gate E5 ciclo 3, salida 1 (B-01)`). El gate no está en verde: `docs/qa/E5/gate.json` trae exit_code 1, test_count 212 y coverage_percent 89.8. Fallan G4 y G13. Hay importantes abiertos. La etapa no se cierra.

El cierre no cabe. La regla de cierre de 8.4 exige gate en verde y cero críticos o importantes abiertos. Con este gate, la primera línea no puede ser de cierre.

La excepción de línea base de la sección 10.2 vale solo para E0. En E5, G4 y G13 en fail impiden el cierre. No se marcan pass. No se bajan umbrales.

Pass del gate, sin que alcancen: G1, G2, G3, G5, G6, G7, G8, G9, G10, G11 y G12. G3 es `python -m pytest` con exit 0; `uv run pytest` no arranca (ADR-004). G6 registra 4 passed in 4.60 s. Ese verde no es el e2e de B-01 ni una prueba de que un proceso escuche en localhost. G8 informa sin red. No es una telemetría medida en contra y no demuestra un proceso a la escucha. G10 dice que 5 requisitos de E5 citan un archivo de test que existe. El verde de la suite lo mide G3. No comprueba bandas de holgura, un filtro por WBS, la asociación del baseline ni un socket.

`b323f41` actualiza `docs/qa/E5/gate.json` y `docs/qa/E5/gate.md`, y toca `docs/ESTADO.md`. Esta revisión no editó ese archivo. La pantalla de este ciclo está en `3eafad8` (`feat(ui): perfil, pestanas, ranking y biblioteca (B-01)`), junto con `docs/qa/E5/ciclo3.md`. Ese archivo describe el corte y no imprime el hash. El contrato es `6498d00`, anterior al código. El veredicto del ciclo 2 es `9908957`. Esta revisión no reejecutó pytest, el gate ni la mutación. No se abrió un navegador.

G4 incumple 8.1. El umbral es 90 % de líneas y 85 % de ramas. Este gate: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. cobertura_total 89.8. Esas seis cifras no cruzan el umbral y no se movieron respecto del ciclo 2. El modelo en 100.0 / 100.0 y el resto en líneas 90.2 no compensan. No se marca pass. La línea base no se aplica a E5. El detalle está en I-30.

G13 no está medido. El detalle es «no medido: falta el informe de qa-sabotaje». No hay `docs/qa/E5/sabotaje.md`. No se inventa un kill score y no se copia el de otra etapa. No medido no es un pase. El detalle está en I-31.

El e2e de B-01 sigue incompleto. En `3eafad8` la pantalla manda el perfil elegido a Calidad, parte resultados y exportaciones en dos pestañas, pone la barra en 0 y la llena en 1 al terminar, y dice que no hay avance parcial. Si el multiselect tiene selección, el lote recibe esos ids y, con filas, ofrece el Excel del ranking. La biblioteca llama a `save_run` con `store_schedule=False` y no le pasa el cronograma. El visor filtra por igualdad exacta de `task_code`. Si hay tabla `driving_chain` no vacía, la muestra y dice que no es un float path de P6. Siguen fuera las bandas de holgura, la marca de ruta crítica, el filtro por WBS, el trazado de predecesoras, el botón «Informe completo» y un avance que no sea solo el salto final. La prueba del lote no elige módulos ni exige el botón del ranking. La prueba del visor no escribe un código ni exige la cadena driving. Eso no es el e2e completo de B-01. El detalle está en I-32.

El baseline no se asocia. La pantalla lo dice: «El baseline no se asocia en esta pantalla.» El lote repite que no asocia un baseline. El test afirma la primera frase. `AnalysisContext` de la pantalla y el del lote no llevan baseline. R-120 no está en verde. El detalle está en I-33.

R-051 queda abierto. `test_localhost_config_disables_usage_stats` lee `.streamlit/config.toml`. El archivo tiene `address = "localhost"` y `gatherUsageStats = false`. No abre un socket. No demuestra que un proceso esté escuchando. El detalle está en I-34.

No hay crítico de telemetría medida. El archivo de configuración apaga las estadísticas de uso y G8 informa sin red. No se observó una red. No se abrió un navegador. Eso no cierra R-051 como prueba de proceso.

`tests/test_e5_manifest.py` no cambió en `3eafad8`. No es una corrida de AppTest. No completa el e2e.

E5 queda condicional a I-3 y al bloqueo ya registrado de E0, E1, E2, E3 y E4, cada una tras su tercer rechazo, sin cuarto ciclo. Esta revisión no les cambia el estado y no las reabre. No se leyeron datos reales. No se bajaron umbrales. No se copió un kill score. El detalle está en `docs/qa/E5/hallazgos.md`.

No hay críticos. Importantes abiertos de este ciclo, y bloquean el cierre: I-30 (G4), I-31 (G13 no medido), I-32 (e2e todavía incompleto), I-33 (baseline no asociado) e I-34 (la prueba de localhost no abre un socket). Ninguno se cierra. Heredados que siguen abiertos y no se cierran ni se reabren: I-3 y los de E1 a E4, I-11 a I-29.
