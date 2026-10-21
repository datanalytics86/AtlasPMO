# logica-red — E2

El filtro de B-02 quedó en `src/atlaspmo/analysis/logic/redundant.py`. Un solo grafo, un solo orden topológico, candidatos agrupados por origen y limitados al rango hasta el destino más lejano. Si el grafo completo tiene ciclo, no hay candidatos. `_confirm`, `_join` y la limpieza no se reescribieron.

Comandos, en la rama `e2/logica-red`:

- `py -3.12 -m uv run python -m pytest tests/test_e2_chain.py tests/test_e2_joint.py tests/test_e2_clean.py tests/test_e2_guards.py tests/property/test_logic.py -q` — 8 passed.
- `py -3.12 -m uv run python -m pytest tests/perf/test_redundancy.py -m perf -q` — 1 passed in 1.42 s. Ese tiempo incluye escribir el archivo. El filtro solo, medido aparte, es 0.345 s.
- `py -3.12 -m uv run python -m ruff check` sobre los archivos tocados — limpio.

La confirmación de 30 000 no se corrió. La proyección está en `docs/qa/E2/perf.md` y no cumple 3 minutos. Los resultados siguen condicionales a I-3 y al bloqueo de E1.
