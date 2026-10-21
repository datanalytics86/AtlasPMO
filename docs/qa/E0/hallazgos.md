# Hallazgos E0 — ciclo 1

Revisión de QC-4 y QC-6 sobre `docs/qa/E0/gate.json` (exit_code 0), `gate.md`, `QC1_contrato.md`, ADR-010 a ADR-013 y las secciones 8.4, 8.5 y 10.2 de `docs/MEGAPROMPT_v2.md`. No se reejecutó la suite. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`.

## Crítico

No hay hallazgos críticos.

## Importante

Abiertos. Cada uno bloquea el cierre (sección 8.5).

### I-1 — Los tests del gate no cubren cada control

La sección 8.3 pide, para `scripts/qa_gate.py`, un caso que pase y uno que falle por cada control G1–G13. El alcance de E0 pide ese script y sus tests. `tests/test_qa_gate.py` abre diciendo que cada control tiene esos dos casos. No es así:

- G7 y G8 tienen fallo y pase.
- G9 solo tiene fallo (`test_g9_fails_when_a_table_is_missing_from_the_spec`). No hay caso que pase.
- G1, G2, G3, G4, G5, G6, G10, G11, G12 y G13 no tienen ni el caso que pasa ni el que falla.

Esto no es la línea base. G4, G5, G6, G10 y G13 pueden quedar sin cumplir sobre el código heredado. Los tests del propio gate no son código heredado y no están.

### I-2 — No está la herramienta de mutación

El alcance de E0 incluye la herramienta de mutación (sección 0.2 y 10.2): una dependencia que funcione en Windows o, si ninguna sirve, `scripts/qa_sabotage.py`. En `pyproject.toml` están `hypothesis`, `pytest-benchmark` y `pytest-cov`. No hay herramienta de mutación. `scripts/qa_sabotage.py` no existe. G13 está en `linea_base` con el detalle «no medido: falta el informe de qa-sabotaje». Ese estado no es pass y no sustituye la herramienta.

### I-3 — La trazabilidad no es la de toda la spec, y dos filas de E0 no prueban lo que dicen

E0 pide `docs/qa/TRAZABILIDAD.md` con un R-xxx por cada requisito de las secciones 2, 5, 6, 7 y 11. El archivo tiene un resumen por etapa (8 filas de E0: R-001 a R-007 y R-063). No hay fila para el formato XER de la sección 5, para cada métrica DCMA de la sección 6 ni para cada caso borde de la sección 7. G10 en `linea_base` («8 requisitos de E0; el verde se exige desde E1») no se declara cumplido y no tapa este hueco.

Además, el test citado no prueba el requisito:

- R-002 (ruff check y format) apunta a `tests/test_qa_gate.py`, que no ejecuta ruff. Quien lo hace es G1.
- R-063 (instalación sin administrador) apunta a `tests/test_gen_scale.py`, que solo comprueba tablas P6 y una cadena en serie. La instalación queda en `docs/qa/E0/acciones.md`, no en ese test.

Eso es un test que no prueba lo que dice (sección 8.5).

### I-4 — El pre-push no exige el remoto `origin`

La sección 14.2 pide que el pre-push rechace cualquier destino distinto de `origin/v2`. `scripts/hooks/pre_push.py` rechaza un ref remoto distinto de `refs/heads/v2` y corre G8. No lee el nombre del remoto. Un push de la rama `v2` a otro remoto no queda rechazado por ese script.

### I-5 — La config del proyecto no niega `.env`

La sección 14.2 pide negar `**/.env` además de `**/data/real/**`. `.grok/config.toml` solo niega Read, Edit y Grep sobre `**/data/real/**`. ADR-001 no dispensa `.env`.

## Menor

No bloquean.

### M-1 — No quedó la salida en rojo previa al arreglo de B-17

La sección 8.4 (QC-3) y la regla 2 de la sección 0 piden guardar la salida en rojo del test antes del arreglo. En `docs/qa/E0/` no está esa salida. La brecha sí está descrita en el megaprompt (sección 10.1, B-17: la colección fallaba con `No module named 'scripts'`). Hoy `pyproject.toml` tiene `pythonpath = [".", "src"]` y `tests/test_phase2.py` importa `scripts.run_conformance`. Aceptable como menor.

### M-2 — `docs/ESTADO.md` sigue en QC-3

Sigue diciendo que E0 está en el ciclo 1, control QC-3. El gate de la etapa ya está escrito. No cambia resultados.

## Línea base — no cumplida

G4, G5, G6, G10 y G13 están en `linea_base`. No son pass. La excepción de la sección 10.2 permite cerrar E0 con ese estado y, por sí sola, no rechaza la etapa. El rechazo de este ciclo sale de I-1 a I-5.

| Control | Estado en `gate.json` | Qué muestra el detalle |
|---|---|---|
| G4 | linea_base | Cobertura medida (total 83 % en el recorte). El umbral de la sección 8.1 no se declara cumplido. La misma salida dice `93 passed in 6.11s`. |
| G5 | linea_base | No existe `tests/property`. |
| G6 | linea_base | No medido: no hay `tests/perf`. |
| G10 | linea_base | 8 requisitos de E0. El verde se exige desde E1. |
| G13 | linea_base | No medido: falta el informe de qa-sabotaje. |

## Gate bloqueante

En verde, y no alcanza para aprobar mientras I-1 a I-5 sigan abiertos.

- Exit code: 0.
- Pass: G1, G2, G3, G7, G8, G9, G11. G12 también está en pass («sin etapa anterior; no hay regresion que medir»).
- G3 no ejecutó `uv run pytest`: en este equipo no arranca (ADR-004). El detalle dice `python -m pytest exit 0` y, por ADR-011, eso se acepta. Los 93 passed salen del recorte de pytest dentro de G4, no de una corrida nueva de esta revisión.
