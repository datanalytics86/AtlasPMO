# Hallazgos E10

HEAD `5edd81e`. El gate de la etapa no corrió. No hay `gate.json` de E10. Esto no cierra la etapa.

Los tres puntos de `docs/VALIDACIONES_PENDIENTES.md` (E10) siguen abiertos y no los subo. El docstring y la nota dicen que las rutas no son un float path de P6. `resource_limit` queda en `None` y `no_evaluable`, con la nota de que no hay campo citado de tope. El reparto dice que es lineal en tiempo laboral.

## H-1 — importante

El segundo XER no entra en la corrida de calidad. La pantalla solo pisa la celda BEI. El test de R-387 está en verde y no prueba la asociación.

El par del test (LATE, OPEN, EARLY; corte 2026-02-01) pasado a `evaluate(actual, dcma_estricto, baseline)` da BEI 1.0 `cumple`, actividades perdidas 1.0 `no_cumple`, GAO-10 `cumple` e índice 60. Esa es la cuenta del contrato para el BEI.

`QualityModule.run` toma el baseline solo si `baseline_proj_id` viene puesto, y lo recorta del mismo cronograma. El segundo archivo viaja en `ctx.other`. La pantalla lo copia ahí y arma `QualityConfig` solo con el perfil. El módulo no lee `ctx.other`. La comparación de updates sí lo lee.

La misma llamada al módulo, con `other` ya cargado, da BEI `None` `no_evaluable`, perdidas `None` `no_evaluable`, GAO-10 `manual` e índice 66,666… El hallazgo dice «Falta el proyecto baseline.» El Excel de ese resultado escribe el índice 66,67 y ese texto.

Después de la corrida, el visor reemplaza únicamente la clave `bei` del dataframe por un `evaluate` aparte. `tests/test_e10_ui.py` lee esa celda y la compara con el oráculo. No lee perdidas, GAO-10, el índice ni el libro. «Informe completo», «Exportar Excel» y «Exportar PDF» usan `results`, sin el parche. El binario puede empezar con `PK` o `%PDF` y llevar el BEI no evaluable. El manifiesto hashea el primer archivo, no el segundo.

El rótulo «El segundo XER es el baseline.» afirma una asociación que la corrida de calidad no hace. Es desvío de la spec (sección 6 y R-387) y un test que no prueba lo que el requisito dice. Bloquea el cierre. No lo marco crítico: `evaluate` con el par sigue en 1.0. El número que no coincide es el de la corrida y el del informe, porque el baseline no les entra.

### H-1 — cerrado

HEAD `576ac59`, «fix(quality): el segundo XER entra en la corrida (H-1)». El diff es `f45a51f..HEAD`. El gate sigue sin correr. Esto no cierra la etapa.

`QualityModule.run` usa `ctx.schedule.select(baseline_proj_id)` si ese id viene puesto. Si no, y `ctx.other` es un `Schedule`, ese cronograma es el baseline de `evaluate`. Si no hay ninguno, el baseline queda en `None`. La pantalla ya no llama a `evaluate` ni reemplaza la clave `bei`: la tabla sale de `result.metrics`. El contexto sigue pasando `other=baseline` y `QualityConfig` sigue llevando solo el perfil. `check.py` no está en el diff.

Lo medí en los tres tests, 3 passed en 2,83 s. Sin id, el módulo y la corrida de la pantalla igualan a `evaluate(actual, perfil, baseline)` en `bei`, `missed_tasks`, `gao_10` y `quality_index`, valor y estado. El BEI del dataframe es el de ese resultado, no un cálculo aparte. «Falta el proyecto baseline.» no está en los hallazgos ni en `informe.xlsx`. Con `baseline_proj_id` `"2"`, el resultado iguala a `evaluate` contra `select("2")` del mismo archivo y no al segundo XER. H-2 y H-3 no se tocaron.

## H-2 — menor

La pestaña por módulo no muestra el módulo. Tras ejecutar se agrega una pestaña por corrida y el cuerpo es el nombre. Las métricas siguen juntas en «Resultados». El test comprueba la etiqueta. No cambia un número. No bloquea.

## H-3 — menor

`write_star` sigue buscando `spread_hours` para grabar el balde `corte`. La actividad de EVM ya no trae esa columna, así que `fact_timephased` queda vacío en el caso nuevo. Los días están en las tablas del módulo. `docs/MANUAL_USUARIO.md` sigue diciendo que la duración remanente va a ese balde y que no es una curva por periodo. No mueve el 8+8+8 ni el 8/16 del contrato. No bloquea.
