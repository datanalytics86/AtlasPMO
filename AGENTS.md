# AtlasPMO — plataforma personal de análisis de cronogramas (P6 / MS Project)

Especificación: docs/MEGAPROMPT_v3.md · Estado: docs/ESTADO.md · Decisiones: docs/DECISIONES.md · QA: docs/qa/ · Pendientes de Nicolás: docs/VALIDACIONES_PENDIENTES.md

## Reglas críticas
- Sesiones con auto-aprobación: los límites duros de la sección 14 del megaprompt son absolutos.
- Nunca leer data/real/ ni ATLASPMO_GOLDEN_DIR, por ningún medio (incluido el shell). El repositorio se trata como público.
- App 100 % local: sin red, sin telemetría.
- XER: cp1252, CRLF, tablas no modificadas idénticas byte a byte. Solo campos con evidencia en docs/XER_SPEC.md.
- Sin aproximaciones silenciosas: registrarlas en ModuleResult.approximations.
- Redundancia = camino alternativo ≥ lag en el grafo de eventos + confirmación conjunta con delta cero. Nunca "no es driver".
- Test primero; nada se declara terminado sin evidencia en docs/qa/E<n>/.
- Quien implementa no edita oráculos, esperados, umbrales ni el gate. Nadie se autoaprueba.
- Una etapa se cierra con VEREDICTO APROBADO de qa-revisor y gate en verde. Si tras 3 ciclos no aprueba: RECHAZADA-BLOQUEADA con diagnóstico, y se sigue (sección 0.3 de la v3).
- Prioridad v3: rendimiento del motor. Metas activas de la sección 11 en docs/qa/seccion11.toml; cobertura como trinquete en docs/qa/baseline.json.
- Código e identificadores en inglés; UI, docs y mensajes al usuario en español (es-CL).
- Rama v3; nunca push a main ni --force.

## Comandos
- Gate: uv run python scripts/qa_gate.py --etapa E<n> --base <commit base de la v3>
- Metas de la sección 11 (todas, a escala real): uv run python -m pytest -m seccion11 tests/perf/test_seccion11.py -s
- Tests: uv run pytest  (en el equipo de Nicolás: uv run python -m pytest)
- Lint, formato y tipos: uv run ruff check . && uv run ruff format --check . && uv run mypy src
- App: atlaspmo.bat (uv run python -m streamlit run src/atlaspmo/ui/app.py)
- Conformidad (solo Nicolás, en su equipo): uv run python scripts/run_conformance.py
