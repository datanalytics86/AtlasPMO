# Decisiones

## ADR-001 — Mecánica de Grok Build

Verificado el 2026-10-20 con `grok inspect --json`. Grok Build 1.0.62 stable.
Revalidado el 2026-10-21 al abrir E0: la rama de trabajo es `v2` y `spawn_subagent` sigue sin `subagent_type`. Los 13 agentes se lanzan con el rol escrito en el brief.
El comando corrió con cwd en el home, antes de existir este checkout.
La guía vigente manda cuando difiere del megaprompt.

- Built-ins cargados: `general-purpose`, `explore`, `plan`. No había `~/.grok/agents`.
- `spawn_subagent` en esa sesión acepta `prompt`, `description`, `background`,
  `isolation`, `resume_from` y `cwd`. No acepta `subagent_type` ni `capability_mode`.
- La guía dice que `subagent_type` aparece cuando ya existen agentes de
  proyecto, de usuario o de plugin. `capability_mode` no es un argumento de
  spawn: lo fija el tipo de agente o un rol.
- Un subagente no puede lanzar otro. La orquestación queda en la sesión principal.
- No está documentado que un subagente cargue `AGENTS.md`. Cada brief repite
  las reglas críticas.
- `.grok/config.toml` de proyecto solo aplica `[mcp_servers]`, `[plugins]`,
  `[permission]` y `[mcp] max_output_bytes`. `permission_mode` y `[subagents]`
  viven en la config del usuario.
- Los nueve agentes declaran solo `name` y `description`. No se usó `tools`:
  un nombre de herramienta no confirmado puede dejar al agente sin herramientas.
- Sí hay denegación de rutas. Este repo niega `Read`, `Edit` y `Grep` sobre
  `**/data/real/**`.

## ADR-002 — Lock parcial en la Fase 0

`uv.lock` fija lo que esta fase importa: pydantic, pandas, pyyaml, streamlit,
y el grupo dev (pytest, ruff, mypy, pre-commit). numba, DuckDB, reportlab,
Plotly, lxml y el extra `[mpp]` entran en la fase que los use, después de
comprobar que hay wheel para Windows.

## ADR-003 — always-approve

El 2026-10-20 Nicolás decidió mantener `permission_mode = "always-approve"`
en su `~/.grok/config.toml`. Este repositorio no edita ese archivo.
Los commits de la fase van a `fase-0`. No hay push a `main` sin su aprobación.

## Limitación — ATLASPMO_GOLDEN_DIR

La ruta no está en el repositorio y aquí no se conoce. El deny del proyecto
no puede cubrirla. Cuando la ruta exista, Nicolás puede añadir en su config
de usuario reglas `Read`, `Edit` y `Grep` con esa ruta absoluta.
Las reglas se leen al abrir la sesión. Los tests contra cronogramas reales
los ejecuta él, y la salida tiene que ir anonimizada.

## Supuesto — firmas XML del hook

Fuera de `tests/fixtures/`, el hook rechaza un XML que contenga
`APIBusinessObjects` o `http://schemas.microsoft.com/project`.
Son firmas para reconocer un export de P6 o un MSPDI, no un parser.


## ADR-004 — Lanzar con python -m en este equipo

`uv run pytest` y `uv run streamlit` fallan con `Failed to spawn` / `os error 5`
(acceso denegado). El intérprete sí arranca. El bat queda así:

```
uv run python -m streamlit run src/atlaspmo/ui/app.py
```

Los tests de esta fase se ejecutaron con `uv run python -m pytest`.
Si en otra máquina el .exe del venv no está bloqueado, `uv run pytest` vuelve a servir.
El texto de `AGENTS.md` no se cambió: sigue citando `uv run pytest`, que es el comando del megaprompt.

## ADR-005 — Campos y baseline de la fase 1

Los nombres leídos están en `docs/XER_SPEC.md`, con la marca de que no hay un export de Nicolás.

- Si `TASK` trae `float_path`, el modo A y el CPLI usan esa columna. Si no, usan `int_path` / `int_path_order`, que es lo que lee PyP6Xer, y el resultado lo dice.
- `TASKPRED.float_path` no se usa como holgura libre. El modo A no marca vínculos driving.
- El fin baseline es `target_end_date` del proyecto `baseline_proj_id`, emparejado por `task_code`. No hay un campo de baseline por actividad citado.
- El conjunto de restricciones duras es una decisión de producto. Está en cada perfil.
- `scripts/gen_synthetic.py` sigue escribiendo solo el fixture mínimo `SYNTH`. Los casos con esperado a mano los escribe `scripts/build_cases.py`.
- En esta fase entraron wheels de Windows para `lxml` 6.1.3, `xlsxwriter` 3.2.9 y `reportlab` 5.0.1. numba, DuckDB, Plotly y el extra `[mpp]` siguen fuera.

## ADR-006 — Motor de la fase 2

- El texto de calendario que se interpreta está citado en `XER_SPEC.md`. Un calendario sin `clndr_data` y sin base no recibe un horario inventado.
- Retained logic, progress override y actual dates son argumentos. También lo son el calendario del lag (predecesora por defecto, sucesora, transcurrido o el del proyecto) y la holgura (la menor entre inicio y fin, por defecto).
- Una restricción "en o después" atrasa. Una "en o antes", o un "exactamente" más temprano que la lógica, no adelanta las fechas tempranas: la holgura sale negativa. ALAP sin sucesoras se mueve a sus fechas tardías. ALAP con sucesoras se anota y no se mueve.
- LOE y WBS summary se arman después del pase y no marcan la ruta crítica. `TT_Rsrc` usa el calendario de la actividad.
- La redundancia no usa reducción transitiva ni el criterio "hoy no es driver".

## ADR-007 — Riesgo y EVM de la fase 3

- Los rangos, la correlación y los eventos no se leen del XER. Son argumentos del módulo.
- Monte Carlo queda en Python puro. numba no entró: no hay una medición que justifique el extra, y la invariante de varianza cero ya corre sin él.
- Iman-Conover suma 1e-8 a la diagonal. Si Cholesky falla, la correlación se omite y queda anotada.
- El PV es lineal en tiempo laboral. No se inventa una curva de recurso.
- `CP_Units` y el tope de `RSRCRATE` quedan `no_evaluable`. No se inventan esos campos.
- `CP_Phys` mayor que 1 se interpreta como porcentaje 0–100. Es un supuesto y queda anotado.
- La semilla va en `RunMetadata.seed` y en la clave `seeds` del manifiesto.

## ADR-008 — Integración de la fase 4

- MSPDI se lee con los elementos citados en `XER_SPEC.md`. No se inventan códigos `CS_*` desde `ConstraintType`.
- DuckDB 1.5.6 entró desde el wheel `cp312-win_amd64`. El Parquet lo escribe DuckDB. No se agregó pyarrow.
- La biblioteca guarda corridas, métricas y hallazgos. Las actividades solo entran si `store_schedule` es verdadero.
- `fact_timephased` se escribe vacío. No hay curva de recurso que repartir.
- El extra `[mpp]` queda en el lock como `mpxj` 16.10.0 (wheel puro). `uv sync` sin el extra no lo instala. Sin Java, `read_mpp` no abre el archivo.
- El PBIP sigue el formato de Microsoft Learn revisado el 2026-10-20: `definition.pbism` 4.2, TMDL en `definition/`, y el `.pbip` apunta al reporte. No se abrió en Power BI Desktop.

## ADR-009 — Cierre de la fase 5

La revisión de aproximaciones no reescribió el motor. Lo que calculaba sin nota ahora queda en `ModuleResult.approximations`:

- El modo A omite actividades sin holgura total o sin horas por día, y lo dice.
- `hours_per_day` del llamado reemplaza el del perfil, y calidad y modo A lo dicen.
- Las `parse_notes` del lector llegan a modo A, modo B, lógica, limpieza, riesgo, EVM y comparación. Antes solo llegaban a calidad.
- El modo B nombra la sonda del CP Test: 8 horas en la primera actividad crítica por `task_code`.
- P50, P80 y P90 nombran el índice `ceil(p * n) - 1`.
- EVM nombra que `scurve` es un solo punto en la fecha de corte.

No hubo ajuste de rendimiento. No se midieron la redundancia bajo 3 minutos, el Monte Carlo de 30 000 por 1 000 bajo 5 minutos, ni el 99,5 % contra P6. Cambiar el motor sin esa medición sería un supuesto.

## ADR-010 — Reglas de ruff de la sección 8.1

En E0 se activan E, F, I, UP, B, BLE, S110, E722, SIM, PT, RET y PL.

Se ignoran PLR2004, PLR0911, PLR0912, PLR0913, PLR0915 y PLR0917. Esas reglas chocan con el motor CPM y con DCMA: comparaciones con 0 y con 8 horas, y firmas con varias fechas. PT solo aplica a `tests/`. `docs/` y `powerbi/` quedan fuera de ruff: no son código Python y formatear el megaprompt reescribiría la spec.

## ADR-011 — Gate y rutas protegidas de E0

`scripts/qa_gate.py`, `docs/qa/skips.toml` y el patrón de perfiles de usuario nacen en E0. G11 exige que el commit que los toca cite este ADR.

En E0, G4, G5, G6, G10 y G13 pueden quedar como línea base. No se declaran cumplidos.

G3 acepta que `uv run pytest` no arranque con `os error 5` (ADR-004) si `uv run python -m pytest` pasa.

G9 mira tablas P6 en todo `src/` y literales con forma de columna solo en `io/`, `model/` y `calendars/`. No trata códigos internos (`no_cumple`, `duplicate_task_id`) como campos XER.

## ADR-012 — Benchmarks fuera de la suite por defecto

Los tests marcados `perf` no entran en `addopts`. No son `skip` ni `xfail`: G6 los ejecuta con `pytest -m perf`. Deseleccionarlos no relaja un umbral. En E0 todavía no hay `tests/perf`; G6 queda en línea base, no medido.

## ADR-015 — El gate compara lo que la sección 8.3 nombra

El ciclo 2 de E0 rechazó G5, G7, G8 y G12 porque el control no aplicaba la regla completa. Este ADR precisa ADR-014.

- G5 lee `max_examples` del `register_profile("qa")`. Menos de 500 es fallo, aunque el nombre del perfil esté.
- G7 exige una fila de `skips.toml` por cada test que llama a `skip`, `skipif` o `xfail`. Una fila de otro test no cubre el resto.
- G8 trata como cronograma un `.xml` con `APIBusinessObjects` o el espacio de nombres MSPDI, fuera de `tests/fixtures/`.
- G12 compara, cuando las dos etapas los tienen, el conteo de tests, `coverage_percent` (baja de más de 0,5 puntos) y `benchmarks` (empeora más de 20 %). Si el número no existe, no se inventa.
- El pre-commit corre `check_g8` además del rechazo por archivo. El pre-push sigue igual.

## ADR-014 — Umbrales reales del gate, sin declararlos cumplidos en E0

El ciclo 1 de E0 rechazó la etapa porque los tests del gate no cubrían G1–G13 y porque G4 no aplicaba el umbral de la sección 8.1. Este ADR precisa ADR-011.

- G4 lee `coverage-gate.json` y aplica 90 % de líneas y 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y 80 % de líneas en el resto. Si no llega, el control falla. En E0 ese fallo sigue reescrito a línea base: no es un pass.
- G10 pasa solo cuando cada fila de la etapa cita un archivo `tests/*.py` que existe. El verde de esos tests lo mide G3. Una fila de una etapa futura puede apuntar a un test que todavía no existe; eso no se declara en verde.
- G13 pasa solo con `alcance: completo` y `kill_score` de al menos 70, y 85 en `engine`, `calendars` o `logic` si el informe los trae. Una muestra (`alcance: muestra`) no pasa.
- `gate.json` guarda `test_count` para G12.
- La herramienta de mutación de esta corrida es `scripts/qa_sabotage.py`. No se instaló un mutador de terceros.

## ADR-013 — Esta corrida no se detiene en el tercer rechazo

Nicolás pidió, el 2026-10-21, que una etapa que siga RECHAZADA tras 3 ciclos se registre como RECHAZADA-BLOQUEADA y que la corrida continúe. No se marca APROBADO. Las etapas que dependan de ella quedan condicionales. Esto precisa la sección 0.3 punto 4 para esta corrida.

## ADR-016 — Confirmación conjunta y XER que no se entrega si el delta no es cero

G5 exige las invariantes b, c y d para cerrar cualquier etapa, incluida E1. El código de `redundant.py::_confirm` unía subconjuntos que pasaban por separado. Dos vínculos pueden ser redundantes solo el uno por el otro. Desde esta corrida el conjunto final se acepta solo si, quitado entero, el CPM no cambia y ningún inicio o fin se queda sin vínculo.

`clean_document` devuelve el documento original cuando el CPM del archivo ya recortado no coincide. El módulo anota que no se escribió. La lista de hitos contractuales entra vacía: un hito no queda protegido solo por ser hito. La identificación por UDF no se lee: no hay columna UDF verificada.

Esto no relaja G5 ni G13. El filtro de candidatos sigue recorriendo el grafo por vínculo. El benchmark de 30k de redundancia queda para E2. B-02 no está cerrado.

## Nota local, fuera del repositorio

`~/.streamlit/config.toml` tenía un BOM y Streamlit no lo parseaba. Se reescribió
sin BOM, con el mismo contenido (`gatherUsageStats = false`).
`~/.streamlit/credentials.toml` se creó con email vacío para que el lanzador
no pregunte el correo ni lo envíe. Ninguno de los dos archivos está en el repo.
