# Validaciones pendientes de Nicolás

La ejecución no se detiene por estos puntos. Cada uno trae la instrucción exacta.

## Antes de una sesión de Grok

En `~/.grok/config.toml`, además de las reglas del repositorio, una denegación con la ruta absoluta de la carpeta golden. No la escribo yo. Texto sugerido, con la ruta real en lugar del marcador:

```toml
[permission]
deny = [
  "Read(**/RUTA-ABSOLUTA-GOLDEN/**)",
  "Edit(**/RUTA-ABSOLUTA-GOLDEN/**)",
  "Grep(**/RUTA-ABSOLUTA-GOLDEN/**)",
]
```

Mantener los golden en una unidad o contenedor cifrado desmontado mientras Grok corre, y no definir `ATLASPMO_GOLDEN_DIR` en esa terminal.

## P6

1. Importar los sintéticos de `tests/fixtures/synthetic/` en un EPS de prueba, programar con retained logic, calendario de lag de la predecesora y holgura mínima, reexportar y pasarlos por `scripts/sanitize_fixture.py`. Dejarlos en `tests/fixtures/p6_verified/`.
2. Confirmar la semántica de `CS_MANDSTART` y `CS_MANDFIN` contra ese export. Hoy el caso queda `[VALIDAR]`.
3. Confirmar si un hito de inicio que cae a las 16:00 pasa al inicio laboral siguiente.
4. Correr `uv run python scripts/run_conformance.py` con `ATLASPMO_GOLDEN_DIR` definido y pegar solo la salida anonimizada.
5. Reimportar un XER limpio como proyecto nuevo, reprogramar y comprobar delta cero.
6. Abrir `powerbi/AtlasPMO.pbip` en Power BI Desktop y refrescar.
7. Para `.mpp`: Java en el PATH y `uv sync --extra mpp`.

## Historia

B-23 sigue en los commits de `fase-1` a `fase-5`. Limpiarlo reescribe historia publicada. Lo decide Nicolás. La rama `v2` no lo reescribe.
