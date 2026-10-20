# Alcance

AtlasPMO es una aplicación local, de uso personal, para analizar cronogramas
de Primavera P6 y MS Project. El usuario carga archivos, elige módulos,
revisa el resultado y exporta.

La especificación completa es [MEGAPROMPT.md](MEGAPROMPT.md). Este archivo
es el resumen de la Fase 0.

## Dentro

- Confianza: cada número se puede contrastar con P6 y cada hallazgo apunta
  a un objeto, una regla y una fuente.
- Chequeos alineados a DCMA 14 puntos, GAO-16-89G y prácticas AACE 49R-06 y 57R-09.
- Revisión por lote, biblioteca histórica y perfiles de umbrales.
- Exportación a PDF, Excel, Parquet y un modelo Power BI.

## Fuera

Análisis forense de atrasos (AACE 29R-03), nivelación de recursos,
escritura de `.mpp`, limpieza en MS Project, multiusuario y cualquier
servicio externo en tiempo de ejecución.

## Fase 0

Entrega el esqueleto: contrato de módulo, registro vacío, interfaz sin
módulos, lanzador, generador estructural y reglas de privacidad.
No calcula un cronograma.
