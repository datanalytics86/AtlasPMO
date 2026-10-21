# QC-1 — Contrato E3

Escrito antes del código nuevo de E3. Fecha 2026-10-21. Los resultados quedan condicionales a I-3 y a E0 y E1 RECHAZADA-BLOQUEADA. Si E2 también queda bloqueada, E3 queda condicional a ese bloqueo.

No se lee `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No hay contraste con P6.

| Id | Qué debe quedar | Prueba | Al escribir este contrato |
|---|---|---|---|
| B-11 / R-030 | CPLI con tiempo laboral del calendario, no la suma de remanentes. Un caso ya está. Falta un caso con feriado o con SS si entra en este ciclo. | `tests/test_e3_cpli.py`, `tests/oracle/span.py` | El caso de 24 h y 16 h está. El oráculo no cubre feriado ni SS. |
| B-12 / R-031 | BEI cuenta completadas antes de tiempo. | `tests/test_e3_bei.py` | Está. No es doble firma. |
| B-13 / R-032 | Bandas de holgura configurables y una cadena driving documentada. | `tests/test_e3_paths.py` | No implementado. Las bandas de modo A están fijas en código. |
| R-033 | DCMA sobre 30k bajo 10 s, o la cifra medida. | `tests/perf/test_quality.py` | No medido. |

QC-2 sigue incompleto fuera del caso de CPLI de ADR-017. No se inventa un oráculo de P6.
