# AtlasPMO — plataforma personal de análisis de cronogramas (P6 / MS Project)

Especificación completa: docs/MEGAPROMPT.md · Estado: docs/ESTADO.md · Decisiones: docs/DECISIONES.md

## Reglas críticas
- Nunca leer archivos de data/real/ ni de ATLASPMO_GOLDEN_DIR. Cronogramas reales = confidenciales. El repositorio se trata como público.
- App 100 % local: sin red, sin telemetría.
- XER: cp1252, CRLF, tablas no modificadas idénticas byte a byte. Solo se usan campos documentados con evidencia en docs/XER_SPEC.md.
- Sin aproximaciones silenciosas: registrarlas en ModuleResult.approximations.
- Redundancia = camino alternativo ≥ lag en el grafo de eventos + confirmación con delta cero. Nunca "no es driver".
- Nada se declara terminado sin ejecutar sus tests y mostrar la evidencia.
- Código e identificadores en inglés; UI, docs y mensajes al usuario en español (es-CL).
- Trabajo por fases con gate; no avanzar ni hacer push a main sin aprobación de Nicolás.

## Comandos
- Tests: uv run pytest
- Lint y tipos: uv run ruff check . && uv run mypy src
- App: atlaspmo.bat (o uv run streamlit run src/atlaspmo/ui/app.py)
- Conformidad (solo Nicolás, en su equipo): uv run python scripts/run_conformance.py
