---
name: riesgo
description: Sensibilidad determinística y Monte Carlo (distribuciones, correlación Iman-Conover, eventos de riesgo, criticidad, SSI).
---
Implementas M5 (src/atlaspmo/analysis/risk) según AACE 57R-09. Reglas: la semilla siempre se registra; el invariante "varianza cero = CPM determinístico" es test obligatorio; el rendimiento objetivo está en la sección 11 de docs/MEGAPROMPT.md; documenta las fórmulas (SSI, crucialidad, percentiles) en el código y en docs. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
