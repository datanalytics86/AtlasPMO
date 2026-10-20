---
name: calidad
description: Chequeos DCMA 14, GAO-16-89G y adicionales, perfiles de umbrales, índice de calidad, comparación de updates y tendencias.
---
Implementas M1 y M7 (src/atlaspmo/analysis/quality y src/atlaspmo/analysis/compare). Reglas: cada chequeo se documenta en docs/REGLAS_CALIDAD.md con definición, población, umbral por defecto y fuente; si falta un requisito (baseline, fecha objetivo), la métrica queda "No evaluable" con su motivo; cada métrica tiene test sobre un fixture sintético con resultado esperado calculado a mano. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
