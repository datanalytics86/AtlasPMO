# Arquitectura

```
UI (Streamlit)  -- selector de módulos, configuración, resultados, exportación
Orquestación    -- registry, runner, run manifest
Análisis        -- calidad, rutas, redundancia, limpieza, riesgo, recursos, comparación
Motor           -- calendarios, CPM compatible con P6
Modelo          -- Schedule
E/S             -- XER, P6 XML, MSPDI, .mpp
Persistencia    -- DuckDB, Parquet, Excel, PDF, PBIP
```

El contrato vive en `src/atlaspmo/analysis/contract.py`.
El registro vive en `src/atlaspmo/registry.py`.
La UI solo presenta: `src/atlaspmo/ui/app.py`.

En la Fase 0 el registro no tiene módulos. Los paquetes `model`,
`calendars` y `engine` existen para fijar el límite y todavía no calculan.
Los perfiles YAML, la biblioteca y Power BI llegan en fases posteriores.
