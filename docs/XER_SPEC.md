# XER_SPEC

Registro de tablas y campos con evidencia. La Fase 0 no ha leído un XER
exportado por P6. No hay nombres de campo verificados.

## Estructura citada por el megaprompt

Pendiente de contrastar con un fixture real o saneado:

- La primera línea empieza por `ERMHDR`.
- Cada tabla usa `%T`, `%F` y `%R`.
- El archivo termina en `%E`.
- La escritura prevista es cp1252 y CRLF.

## Tablas previstas, sin campos

`PROJECT`, `CALENDAR`, `PROJWBS`, `TASK`, `TASKPRED`, `RSRC`, `TASKRSRC`,
`RSRCRATE`, `ACTVTYPE`, `ACTVCODE`, `TASKACTV`, `UDFTYPE`, `UDFVALUE`,
y la tabla de curvas de recurso. El nombre exacto de esa última tabla
no tiene evidencia.

## Códigos citados, sin fixture

Los tipos de vínculo, de actividad, los estados y las restricciones
están en la sección 5 de `MEGAPROMPT.md`. No se copian aquí como
especificación verificada.

## Lo que sí escribe el esqueleto

`scripts/gen_synthetic.py` emite una tabla `SYNTH` con columnas `col_a` y
`col_b`. Esos nombres no son campos de P6. Sirven para probar cp1252, CRLF,
el encabezado y `%E`.
