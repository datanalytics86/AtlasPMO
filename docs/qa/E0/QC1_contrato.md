# QC-1 E0 — contrato

Estado: aprobado para implementar. Ciclo 1.

| Brecha | Criterio ejecutable | Test | Oráculo |
|---|---|---|---|
| B-17 | `uv run python -m pytest` colecta `scripts` | tests/test_phase2.py::test_script_skips_missing_golden | pythonpath en pyproject.toml |
| B-18 | `ruff format --check` en verde | gate G1 | ruff |
| B-19 | AGENTS.md cita MEGAPROMPT_v2.md y hay 13 agentes | lectura de .grok/agents | sección 9.4 |
| B-22 | commits atómicos que citan B-xx; el gate no se autoaprueba | historial de v2 | sección 0 |

G4, G5, G6, G10 y G13 pueden quedar en línea base en E0. G1, G2, G3, G7, G8, G9 y G11 tienen que quedar en verde.
