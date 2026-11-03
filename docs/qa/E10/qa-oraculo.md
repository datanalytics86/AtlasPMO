# qa-oraculo — E10

Segunda firma de R-395 y R-396. HEAD de partida `b24b315`, rama `v3`. No se leyó `data/real/` ni `ATLASPMO_GOLDEN_DIR`. No se usó red. No se editó `tests/test_phase1.py`, `tests/oracle/span.py`, `tests/test_e3_cpli.py`, `tests/test_e3_bei.py`, `tests/test_e3_oracle.py`, `analysis/quality/check.py` ni `engine/`. El 4/3 y el 2/2 se escribieron desde el contrato, no desde una corrida previa de `evaluate`.

## R-395

`tests/oracle/span_holiday.py` recorre turnos de lunes a viernes 08:00–16:00, se salta el 2026-01-07 y no importa `atlaspmo`. El miércoles 08:00–16:00 aporta 0 minutos. Del lunes 2026-01-05 08:00 al jueves 2026-01-08 16:00 hay 24 h (lunes, martes y jueves). Del jueves 16:00 al viernes 2026-01-09 16:00 hay 8 h. `(24+8)/24` es `1.3333333333333333`, el mismo flotante que `(1440+480)/1440`. `cpli_ss.yaml` trae `file: cpli_ss.xer`, `calculado_por`, `verificado_por: tests/oracle/span_holiday.py`, `metodo` y `expect.cpli` con ese valor y `status: cumple`. `evaluate` sobre el XER iguala el retorno del oráculo y el estado `cumple`. No se tocó el `(24+16)/24` del caso viejo.

## R-396

`tests/oracle/bei.py` no importa `atlaspmo`. Recibe las tres tuplas (código, estado, fin real, fin baseline) y la fecha de corte 2026-02-01 00:00. Vencidas: LATE y OPEN. Completadas al corte: LATE y EARLY. El retorno es `2/2`. `bei.yaml` trae `file: bei.xer`, `proj_id: "1"`, `baseline_proj_id: "2"`, `calculado_por`, `verificado_por: tests/oracle/bei.py`, `metodo` y `expect.bei` con `value: 1.0` y `status: cumple`. `evaluate` del proyecto 1 contra el baseline 2 iguala ese retorno. El assert `2 / 2` de `tests/test_e3_bei.py` no se movió.

## CPM de referencia

Sí reprodujo el SS con feriado. `schedule_cpm` con `engine="reference"` sobre `cpli_ss.xer` da el término de A el jueves 2026-01-08 16:00 y el de B el lunes 2026-01-05 16:00. Esas fechas ya estaban escritas en el test y en el XER; no se cambiaron para calzar con el motor. No se abrió `engine/`. `analysis/quality/check.py` no hizo falta: con las fechas guardadas, `evaluate` ya devolvía 4/3 y 2/2.

## XER

`scripts/build_cases.py` solo suma `_cpli_ss`, `_bei` y su llamada desde `main` (82 inserciones, 0 borrados). `cpli_ss.xer`: `plan_end_date` 2026-01-09 16:00, corte 2026-01-05 08:00, días P6 2 a 6 de 08:00 a 16:00 y excepción `(d|46029)` sin turno. 46029 es 2026-01-07 contado desde 1899-12-30. A tiene `early_end_date` 2026-01-08 16:00 y `float_path` 1. B no está en la ruta 1, SS desde A con lag 0, `early_start` 2026-01-05 08:00 y `early_end` 2026-01-05 16:00. `bei.xer`: proyecto 1 con corte 2026-02-01 00:00 y proyecto 2 baseline. LATE completa, fin real 2026-01-12 08:00, fin baseline 2026-01-10 08:00. OPEN sin completar, fin baseline 2026-01-20 08:00. EARLY completa, fin real 2026-01-05 16:00, fin baseline 2026-03-01 08:00. Los códigos coinciden.

Correr el script reescribió `cpli.xer` (980 → 765 bytes): el generador viejo no reproduce el archivo ya versionado. Se restauró con `git checkout -- tests/fixtures/synthetic/cases/cpli.xer`. El resto de los XER viejos no cambió.

## Comandos

`git rev-parse --short HEAD`

```
b24b315
```

`.\.venv\Scripts\python.exe -c "print((24+8)/24 == (1440+480)/1440); print(repr((24+8)/24))"`

```
True
1.3333333333333333
```

`.\.venv\Scripts\python.exe -c "from datetime import date; print((date(2026,1,7)-date(1899,12,30)).days)"`

```
46029
```

`.\.venv\Scripts\python.exe scripts/build_cases.py`

Escribió `tests/fixtures/synthetic/cases`, incluido `cpli.xer`. Ese archivo se revirtió, como queda arriba.

`.\.venv\Scripts\python.exe -m pytest tests/test_e10_sign.py tests/test_e3_cpli.py tests/test_e3_bei.py tests/test_e3_oracle.py tests/test_phase1.py -q --tb=short`

```
.........................                                                [100%]
25 passed in 6.98s
```

Entran `test_hand_calculated_metrics` de los YAML nuevos y `test_round_trip_cases`.

## Archivos de esta firma

- `tests/oracle/span_holiday.py`
- `tests/oracle/bei.py`
- `tests/fixtures/synthetic/cases/cpli_ss.yaml`
- `tests/fixtures/synthetic/cases/bei.yaml`
- `tests/fixtures/synthetic/cases/cpli_ss.xer`
- `tests/fixtures/synthetic/cases/bei.xer`
- `scripts/build_cases.py`
- `tests/test_e10_sign.py`
- `docs/qa/E10/qa-oraculo.md`

`git status --porcelain` también muestra `src/atlaspmo/analysis/resources/evm.py`, `src/atlaspmo/analysis/resources/module.py`, `tests/test_e4_spreads.py` y `tests/test_e10_spread.py`. Esta firma no los editó.
