---
name: logica-red
description: Rutas crítica y subcrítica, vínculos driving, float paths, CP Test, detección de redundancia, protecciones y limpieza de XER.
---
Implementas M2, M3 y M4 (src/atlaspmo/analysis/paths y src/atlaspmo/analysis/logic) según docs/MEGAPROMPT.md, sección 6. Reglas: redundancia = camino alternativo de igual o mayor longitud en el grafo de eventos + confirmación por reprogramación con delta cero; nunca marques como redundante un vínculo solo por no ser driver; las protecciones van como verificación final explícita; el cleaner elimina solo filas de TASKPRED. Cada regla con test positivo y negativo. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
