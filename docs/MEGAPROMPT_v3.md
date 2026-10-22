# MEGAPROMPT v3 — AtlasPMO
## Plataforma personal de análisis de cronogramas P6 / MS Project — Tier 1
### Grok 4.7 en Grok Build · modo autónomo multiagente · auto-aprobación · foco en rendimiento

> **Para Nicolás — cómo iniciar**
> 1. En la raíz de tu clon local, en una terminal nueva:
>    ```
>    git fetch origin
>    git checkout -b v3 origin/claude/beautiful-goodall-m0q2zj
>    ```
>    Esa rama contiene todo lo de `v2` más el gate ajustado y este documento.
> 2. Antes de abrir Grok: carpeta de cronogramas reales desmontada, `ATLASPMO_GOLDEN_DIR` sin definir y `ATLASPMO_GIT` definida (sección 14).
> 3. Abre `grok` en la raíz con tu `permission_mode = "always-approve"` y pega el prompt de arranque que te entregó Claude, o escribe: `Lee docs/MEGAPROMPT_v3.md completo y ejecuta la sección 15 (Arranque) en modo autónomo hasta terminar E10.`
> 4. Para retomar: `Lee docs/MEGAPROMPT_v3.md y docs/ESTADO.md y continúa desde la siguiente tarea pendiente de la v3.`

> **Instrucción para Grok:** lee este documento completo y ejecútalo en **modo autónomo** (0.1), **multiagente** (9) y con **QA/QC** (8). La sesión corre con **auto-aprobación**: los límites de la sección 14 son duros. La v2 cerró las brechas de robustez pero no las de rendimiento: **la prioridad absoluta de la v3 es que el motor sea rápido** (etapas E7 a E9) sin cambiar un solo resultado. Después viene la funcionalidad pendiente (E10). Trabajas sin preguntar y sin detenerte hasta terminar E10, salvo los casos de 0.3.

---

## 0. Tu rol y cómo trabajamos

- Eres **Grok 4.7 operando en Grok Build** como **ingeniero líder y orquestador**. La sesión principal planifica, define contratos, delega, integra y verifica. **No te autoapruebas:** el cierre de una etapa lo decide el veredicto de `qa-revisor`, apoyado en el gate automático.
- El usuario es **Nicolás**, Líder de Planificación, experto en Primavera P6, EVM y Power BI. No está disponible durante la ejecución: revisa después. Reportes concisos, en español, con evidencia.
- Idioma: comunicación, documentación, UI y reportes en **español**; identificadores, docstrings y comentarios de código en **inglés**. Formato es-CL configurable.
- **Mantén la honestidad de la v2:** "no medido" o "no implementado" es aceptable; afirmar sin evidencia es un hallazgo crítico.

### 0.1 Modo autónomo

- **No preguntes** ni esperes aprobaciones.
- **Decide y registra** en `docs/DECISIONES.md` (con `[VALIDAR]` si Nicolás debe confirmarlo) y sigue.
- **P6 y XER: no inventes.** Sin evidencia, la interpretación más conservadora, registrada como `[VALIDAR]` y como aproximación cuando afecte resultados.
- **Las validaciones manuales nunca te detienen:** van a `docs/VALIDACIONES_PENDIENTES.md`.
- **Memoria de trabajo:** `docs/ESTADO.md` al día (etapa, control QC, ciclo, bloqueos), para retomar sin perder nada.

### 0.2 Decisiones por defecto

Rigen las de la v2, con estos cambios:

| Tema | Decisión por defecto |
|---|---|
| numba | **Obligatorio** en el motor rápido (E7) y en Monte Carlo (E9). Verifica primero que hay wheel para Windows y Python 3.12 (`uv add numba` en el equipo de Nicolás). Usa `cache=True`. Si no hay wheel, numpy vectorizado y regístralo |
| Motor de referencia | El motor actual en Python puro (`engine/cpm.py`) se conserva como **referencia** para pruebas diferenciales. No se borra ni se "optimiza" |
| Doble firma de esperados | Un esperado con una sola firma queda `pendiente_segunda_firma`: se usa en los tests, se informa y **no bloquea** el cierre |
| Comando de tests | `uv run python -m pytest` (funciona en todos los equipos; `uv run pytest` falla en el de Nicolás por ADR-004) |

### 0.3 Cuándo sí te detienes

Solo si:
1. continuar exigiría leer archivos reales (`data/real/`, `ATLASPMO_GOLDEN_DIR`) o cualquier dato confidencial;
2. continuar exigiría administrador, cambios al sistema o red en tiempo de ejecución de la app;
3. continuar exigiría una acción prohibida de la sección 14;
4. terminaste E10 (reporte final, sección 16).

**Una etapa que sigue RECHAZADA tras 3 ciclos no te detiene** (así resuelve la v3 la contradicción que señaló el reporte de la v2). Queda **RECHAZADA-BLOQUEADA** en `docs/qa/E<n>/VEREDICTO.md` y en `ESTADO.md`, con los hallazgos abiertos y el diagnóstico, y continúas. Nunca la marcas como aprobada.

### Reglas de trabajo específicas para Grok 4.7

1. **Verifica antes de afirmar.** Evidencia en `docs/qa/E<n>/`.
2. **Test primero.** El test de aceptación se escribe y se ejecuta en rojo antes del arreglo; la salida en rojo queda como evidencia.
3. **El producto primero.** Un ciclo de corrección tiene que cambiar código o tests del producto. Un ciclo que solo documenta un rechazo **no cuenta** como ciclo. En la v2, unos 72 de 94 commits fueron de QA y solo unos 17 cambiaron el producto: eso no se repite.
4. **Esfuerzo de razonamiento:** `xhigh` en E7, E8 y E9 si el harness lo permite.
5. **Gestión de contexto:** sesión principal bajo unos 200K tokens; compacta al cerrar cada entrega después de actualizar `ESTADO.md`.
6. **Git:** commits atómicos que citen los IDs de brecha. Solo rama `v3`.
7. **Repositorio público.** Nada confidencial se commitea.

---

## 1. Producto

**Qué es:** aplicación local de uso personal para analizar cronogramas de Primavera P6 y MS Project. El usuario carga uno o varios archivos, elige qué módulos ejecutar (uno, varios o todos), revisa resultados en pantalla y exporta.

**Pilares Tier 1**
1. **Confianza verificable:** los números cuadran con P6 y cada hallazgo es rastreable a su actividad o vínculo, a la regla y a la fuente normativa.
2. **Profundidad:** chequeos alineados a DCMA 14 puntos, GAO-16-89G y prácticas AACE (49R-06, 57R-09).
3. **Productividad:** revisión por lote, biblioteca histórica, perfiles de umbrales.
4. **Presentación:** reporte ejecutivo PDF, Excel de hallazgos, Parquet y modelo Power BI.

**Supuestos de diseño (aprobados)**
- Cronogramas típicos de 5.000 a 30.000 actividades.
- Notebook Windows corporativo, sin permisos de administrador; Java solo si se usa MPXJ.
- Sensibilidad determinística + Monte Carlo con eventos de riesgo.
- Recursos en HH y costo; solo diagnóstico, sin nivelación.
- MS Project: lectura desde XML (MSPDI) y desde .mpp vía MPXJ (opcional).
- Limpieza de lógica solo para XER; el XER limpio se importa en P6 como proyecto nuevo.

**Fuera de alcance:** análisis forense completo de atrasos (AACE 29R-03), nivelación de recursos, escritura de .mpp, limpieza en MS Project, multiusuario/web, IA o servicios externos en tiempo de ejecución.

---

## 2. Restricciones no negociables

1. **Local y sin red en ejecución.** La app no hace llamadas de red, no tiene telemetría ni usa APIs externas. Streamlit: `server.address = "localhost"`, `browser.gatherUsageStats = false`.
2. **Los cronogramas reales son confidenciales y tú nunca los lees.**
   - **Control principal:** viven fuera del repositorio, en la ruta de la variable de entorno `ATLASPMO_GOLDEN_DIR`. Como las sesiones de Grok corren con auto-aprobación (sección 14), ningún humano filtra comandos: durante esas sesiones la ruta golden no debe estar accesible (unidad o contenedor cifrado desmontado) y la variable no debe estar definida.
   - `data/real/` existe solo como respaldo local y está en `.gitignore`.
   - `.grok/config.toml` niega `Read`, `Edit` y `Grep` sobre `**/data/real/**` (ADR-001). Esas reglas no cubren comandos de shell: la prohibición de leer esas rutas con `cat`, `type`, `Get-Content`, Python u otro medio es absoluta (sección 14).
   - Los tests de conformidad con archivos reales los ejecuta Nicolás. Su salida debe ser **anonimizada** (IDs hasheados; solo conteos, porcentajes y categorías) para que pueda pegártela sin exponer datos.
   - Hooks de git **pre-commit y pre-push** que rechacen `*.xer`, `*.mpp` y XML de cronograma fuera de `tests/fixtures/`, cualquier archivo bajo `data/real/`, archivos `.env` y rutas absolutas a perfiles de usuario (Windows o Unix) en archivos versionados.
3. **Entradas en solo lectura.** Todo resultado va a una carpeta de salida con timestamp y un `run_manifest.json`.
4. **Reproducibilidad.** Cada corrida registra:
   - versión de la app y hash de git;
   - SHA-256 del archivo de entrada;
   - parámetros y perfil usados;
   - semilla (Monte Carlo);
   - lista de aproximaciones aplicadas.
5. **Cero aproximaciones silenciosas.** Toda simplificación se registra en `approximations` del resultado y se muestra en la UI y en los reportes.
6. **Escritura de XER:**
   - codificación cp1252 (configurable);
   - saltos de línea CRLF;
   - encabezado `ERMHDR` y marcador final `%E` preservados;
   - **todas las tablas no modificadas idénticas byte a byte** a la entrada.
7. **Instalación sin administrador.** Dependencias con wheels para Windows; nada que requiera compilador, GTK ni servicios del sistema.

---

## 3. Stack

| Capa | Elección |
|---|---|
| Lenguaje / entorno | Python 3.12, `uv`, `pyproject.toml`, layout `src/` |
| Datos y cálculo | numpy, pandas, pyarrow; numba para los motores de alto rendimiento (CPM vectorizado, Monte Carlo) |
| Grafos | Estructuras propias en arrays (CSR) para producción; networkx solo en tests como referencia |
| Modelos y configuración | pydantic v2; YAML para perfiles |
| Persistencia | DuckDB (biblioteca local), Parquet |
| UI | Streamlit multipágina, Plotly para gráficos interactivos |
| Reportes | XlsxWriter (Excel), reportlab + matplotlib (PDF) |
| XML | lxml (P6 XML y MSPDI) |
| MS Project .mpp | `mpxj` (JPype + Java) como extra opcional `[mpp]` |
| Calidad | pytest, hypothesis, pytest-benchmark, ruff, mypy (estricto en `model`, `calendars`, `engine`), pre-commit |
| Lanzador | `atlaspmo.bat` → `uv run streamlit run src/atlaspmo/ui/app.py` |

Fija versiones estables al momento de la Fase 0 en `uv.lock`.

---

## 4. Arquitectura

```
UI (Streamlit)  ── selector de módulos · configuración · resultados · exportación
Orquestación    ── registry de módulos · runner por lote · run manifest
Análisis        ── calidad │ rutas │ redundancia │ limpieza │ riesgo │ recursos-EVM │ comparación
Motor           ── calendarios (tiempo laboral indexado) · CPM compatible con P6 · grafo de eventos
Modelo          ── Schedule (proyecto, WBS, calendarios, actividades, vínculos, recursos, asignaciones, códigos)
E/S             ── XER (lectura/escritura) · P6 XML · MSPDI · .mpp (MPXJ)
Persistencia    ── DuckDB · Parquet · Excel · PDF · PBIP
```

**Contrato de módulo.** Todo módulo de análisis lo cumple; así la UI los lista y el usuario elige cuáles ejecutar.

```python
class AnalysisModule(Protocol):
    id: str                      # "quality", "paths", "redundancy", ...
    name_es: str
    description_es: str
    requires: set[Requirement]   # BASELINE, RESOURCES, TWO_VERSIONS, CPM_ENGINE, ...
    config_model: type[BaseModel]
    def run(self, ctx: AnalysisContext, config: BaseModel) -> ModuleResult: ...

@dataclass
class ModuleResult:
    module_id: str
    metrics: dict[str, Metric]          # KPI con valor, umbral y estado
    findings: pd.DataFrame              # esquema Finding (abajo)
    tables: dict[str, pd.DataFrame]     # salidas específicas del módulo
    approximations: list[str]
    metadata: RunMetadata
```

**Esquema `Finding`:** `rule_id, rule_name_es, source (DCMA|GAO|AACE|ATLASPMO), severity (alta|media|baja|info), object_type (project|activity|relationship|resource), object_id, task_code, value, threshold, passed, message_es`.

**Estructura del repositorio**

```
AtlasPMO/
├── AGENTS.md                        (instrucciones del proyecto; sección 13)
├── README.md
├── pyproject.toml · uv.lock · atlaspmo.bat · .pre-commit-config.yaml · .gitignore
├── .streamlit/config.toml
├── .grok/config.toml                (solo claves que Grok Build admita a nivel de proyecto)
├── .grok/agents/                    (subagentes; sección 9)
├── docs/
│   ├── MEGAPROMPT_v3.md             (este documento)
│   ├── ALCANCE.md · ARQUITECTURA.md
│   ├── DECISIONES.md                (ADR numerados + supuestos [VALIDAR])
│   ├── ESTADO.md                    (avance por fase y checkpoint; memoria de trabajo)
│   ├── VALIDACIONES_PENDIENTES.md   (lo que Nicolás debe validar a mano, por etapa)
│   ├── qa/                          (sistema QA/QC; sección 8)
│   │   ├── TRAZABILIDAD.md          (requisito R-xxx → test(s) → oráculo)
│   │   ├── skips.toml               (lista blanca de tests omitidos, con motivo)
│   │   └── E<n>/                    (gate.json, gate.md, hallazgos, VEREDICTO.md por etapa)
│   ├── XER_SPEC.md                  (tablas y campos usados, con evidencia)
│   ├── REGLAS_CALIDAD.md            (catálogo de chequeos: definición, población, umbral, fuente)
│   └── MANUAL_USUARIO.md
├── src/atlaspmo/
│   ├── io/          xer_reader · xer_writer · p6xml_reader · mspdi_reader · mpxj_adapter · validate
│   ├── model/       schedule · enums · units
│   ├── calendars/   clndr_parser · worktime
│   ├── engine/      graph · options · cpm · conformance
│   ├── analysis/
│   │   ├── quality/    dcma · gao · extra_checks · profiles · index
│   │   ├── paths/      critical · driving · float_paths · cp_test
│   │   ├── logic/      event_graph · redundancy · guards · cleaner
│   │   ├── risk/       deterministic · distributions · correlation · risk_events · montecarlo
│   │   ├── resources/  spreads · histograms · evm · earned_schedule
│   │   └── compare/    matching · diff · trends
│   ├── registry.py · runner.py · batch.py
│   ├── library/     store (DuckDB)
│   ├── reports/     excel · pdf · parquet · manifest
│   └── ui/          app.py · pages/ · components/
├── powerbi/                         (proyecto PBIP, Fase 4)
├── profiles/                        dcma_estricto.yaml · corporativo.yaml · contratista.yaml
├── scripts/                         sanitize_fixture.py · gen_synthetic.py · gen_scale.py · run_conformance.py · qa_gate.py · qa_sabotage.py
└── tests/
    ├── unit/ · property/ · perf/ · e2e/
    ├── oracle/                      (implementaciones de referencia mínimas, escritas por qa-oraculo; nunca importan src/)
    ├── fixtures/synthetic/          (XER generados + resultados esperados en YAML)
    ├── fixtures/p6_verified/        (sintéticos recalculados en P6 por Nicolás y saneados)
    └── conformance/                 (contra ATLASPMO_GOLDEN_DIR; se omite si no existe)
```

---

## 5. Modelo de datos y formato XER

- **Formato XER:** texto delimitado por tabuladores.
  - Primera línea: `ERMHDR` (encabezado).
  - Luego, bloques por tabla: `%T <tabla>`, `%F <campos>`, `%R <fila>`…
  - Al final: `%E`.
  - Bytes sin carácter definido en cp1252 (`0x81, 0x8D, 0x8F, 0x90, 0x9D`) no hacen fallar la lectura: se preservan para el round-trip byte a byte y se registran como aproximación.
  - El lector conserva las líneas crudas originales de cada tabla, para permitir la escritura byte a byte.
- **Tablas mínimas:** `PROJECT, CALENDAR, PROJWBS, TASK, TASKPRED, RSRC, TASKRSRC, RSRCRATE, ACTVTYPE, ACTVCODE, TASKACTV, UDFTYPE, UDFVALUE` y la tabla de curvas de recurso. El resto se lee de forma genérica para no perder nada.
- **Valores codificados de referencia.** **Verificar contra fixtures y documentar en `XER_SPEC.md`:**
  - tipos de vínculo: `PR_FS/PR_SS/PR_FF/PR_SF`;
  - tipos de actividad: `TT_Task, TT_Rsrc, TT_Mile, TT_FinMile, TT_LOE, TT_WBS`;
  - estados: `TK_NotStart, TK_Active, TK_Complete`;
  - restricciones: `CS_MSO, CS_MSOA, CS_MSOB, CS_MEO, CS_MEOA, CS_MEOB, CS_MANDSTART, CS_MANDFIN, CS_ALAP`. La primaria va en `cstr_type/cstr_date` y la secundaria en `cstr_type2/cstr_date2`.
- **Unidades:** P6 guarda duraciones, lags y holguras en horas (`*_hr_cnt`). Internamente se trabaja en horas o minutos laborales. La conversión a días usa las horas/día del calendario de cada actividad (configurable).
- **Datos de proyecto:** la fecha de corte, el término programado y las opciones de programación vienen de `PROJECT` (p.ej. `last_recalc_date`, campos `sched_*` y `critical_*`). Verifica los nombres exactos y regístralos.
- **XER multiproyecto:** el usuario elige el proyecto. Los vínculos con actividades de otro proyecto se marcan como **externos**.
- **Baseline:** puede venir como proyecto adicional en el mismo XER o en otro archivo; el usuario lo asocia explícitamente.
- **Validación al cargar:** vínculos huérfanos, duplicados, calendarios inexistentes, ciclos (reportando el ciclo) y fechas faltantes. Entrega un resumen del proyecto más las alertas.

---

## 6. Especificación por módulo

### M0 · Núcleo: calendarios y motor CPM

**Calendarios**
- **Parser de `clndr_data`** (estructura anidada con paréntesis). Debe cubrir:
  - jornadas por día de semana;
  - excepciones (fechas como serial tipo Excel; confirmar la base con fixtures);
  - herencia de calendario base;
  - horas por día.
- **`worktime`:** representación indexada del tiempo laboral por calendario (minutos laborales acumulados sobre el horizonte del proyecto, con resolución configurable). Así sumar o restar trabajo y medir intervalos cuesta O(log n) o menos. El mismo índice lo usan el CPM y Monte Carlo.
  - **Prohibido** recorrer día por día en el camino caliente.
  - El horizonte se calcula a partir del proyecto (fecha de corte, fechas extremas, duraciones y lags) y crece si hace falta. **Nunca** un tope fijo: un proyecto de 15 años no puede fallar por "horizonte agotado".

**Motor CPM compatible con P6**
- Forward y backward pass con vínculos FS/SS/FF/SF y lags positivos y negativos.
- **Opciones del proyecto que debe respetar:**
  - retained logic / progress override / actual dates;
  - calendario de lags (predecesora, sucesora, 24 h, por defecto del proyecto);
  - holgura total calculada como de inicio, de fin o la menor;
  - criterio de crítico (holgura ≤ X o longest path);
  - tratamiento de vínculos externos.
- **Avance:** fechas reales, duración remanente, fecha de corte y avance fuera de secuencia.
- **Restricciones** primarias y secundarias, incluidas las obligatorias y ALAP.
  - Las obligatorias (`CS_MANDSTART`, `CS_MANDFIN`) imponen su fecha en el pase hacia adelante **y** en el hacia atrás, aunque violen la lógica; la violación se reporta como hallazgo. No se tratan como un "start on" que solo atrasa.
  - La semántica de cada restricción se documenta en `XER_SPEC.md` con su fuente. Lo que no tenga evidencia queda `[VALIDAR]` y con un caso en los sintéticos para `p6_verified`.
- **Tipos de actividad:** hitos de inicio y de fin. Un hito de inicio cuya fecha cae al cierre de una jornada se ubica en el inicio laboral siguiente; uno de fin, al cierre de la jornada. Queda `[VALIDAR]` con `p6_verified`. Las actividades LOE y WBS summary se calculan a partir de sus vínculos o hijos después del pase principal.
- **Holguras:** total, libre y libre por vínculo (para identificar vínculos *driving*).
- **Criterio de crítico:** holgura total ≤ X **o** longest path, ambos implementados en el motor y seleccionables.
- Detección de ciclos **iterativa**, sin recursión de Python, con reporte del ciclo. Debe funcionar con cadenas de 60.000 actividades en serie.
- Los comportamientos no soportados (p.ej. programación por calendario de recurso en `TT_Rsrc`, fechas de término esperadas) se reportan como aproximación. Nunca se ignoran en silencio.

**Conformidad** (`engine/conformance.py` + `scripts/run_conformance.py`)
- Compara, por actividad, ES/EF/LS/LF/TF/FF recalculados contra los valores guardados por P6.
- Clasifica cada diferencia por causa probable: calendario, opción de programación, restricción, avance, vínculo externo o desconocida.
- Salida anonimizada (IDs hasheados), apta para compartir.
- **Meta:**
  - coincidencia exacta (tolerancia de un minuto) en ≥ 99,5 % de las actividades de los golden files reales;
  - 100 % en `p6_verified`;
  - 100 % de las diferencias con causa documentada.

### M1 · Calidad (DCMA, GAO, chequeos adicionales)

**DCMA 14 puntos.** Umbrales por defecto abajo. Las poblaciones (qué actividades cuentan: completadas, LOE, WBS summary, hitos) varían entre herramientas: son configurables y quedan documentadas en `REGLAS_CALIDAD.md`.

| # | Métrica | Definición | Umbral |
|---|---|---|---|
| 1 | Logic | % de actividades incompletas sin predecesora o sin sucesora | ≤ 5 % |
| 2 | Leads | % de vínculos con lag negativo | 0 % |
| 3 | Lags | % de vínculos con lag positivo | ≤ 5 % |
| 4 | Relationship types | % de vínculos FS | ≥ 90 % |
| 5 | Hard constraints | % de incompletas con restricción dura (conjunto configurable) | ≤ 5 % |
| 6 | High float | % de incompletas con holgura total > 44 días laborales | ≤ 5 % |
| 7 | Negative float | % de incompletas con holgura total < 0 | 0 % |
| 8 | High duration | % de incompletas con duración (remanente u original, configurable) > 44 días laborales | ≤ 5 % |
| 9 | Invalid dates | Fechas previstas anteriores a la fecha de corte, o fechas reales posteriores a ella | 0 |
| 10 | Resources | % de incompletas con duración > 0 sin recursos ni costo | Configurable (informativo) |
| 11 | Missed tasks | % de actividades con término baseline ≤ fecha de corte que terminaron tarde o no han terminado | ≤ 5 % |
| 12 | Critical Path Test | Un atraso en una actividad crítica se refleja íntegro en el término | Aprueba / Reprueba |
| 13 | CPLI | (largo de ruta crítica remanente + holgura total al término objetivo) / largo de ruta crítica remanente. **Largo** = tiempo laboral desde la fecha de corte hasta el término pronosticado de la ruta crítica, medido en el calendario del proyecto; **no** es la suma de duraciones (ignoraría lags, solapes SS/FF y feriados). **Holgura al término objetivo** = término objetivo − término pronosticado, en el mismo calendario | ≥ 0,95 |
| 14 | BEI | **Todas** las actividades completadas a la fecha de corte (incluidas las que terminaron antes de lo previsto) / actividades con término baseline ≤ fecha de corte | ≥ 0,95 |

**Requisitos por métrica:**
- 11 y 14 necesitan baseline.
- 13 necesita una fecha objetivo de término (baseline o contractual).
- 12 necesita el motor CPM (Fase 2).

Si falta un requisito, la métrica queda como "No evaluable", con el motivo.

**GAO-16-89G.** Mapear las 10 buenas prácticas a chequeos automatizables:
1. capturar todas las actividades;
2. secuenciar;
3. asignar recursos;
4. establecer duraciones;
5. trazabilidad horizontal y vertical;
6. ruta crítica válida;
7. holgura razonable;
8. análisis de riesgo;
9. actualización con avance real;
10. mantener el baseline.

Las partes no automatizables se listan en el reporte como "Requiere revisión manual".

**Chequeos adicionales**
- Avance fuera de secuencia.
- Fechas reales posteriores a la fecha de corte.
- Lag mayor que la duración de la sucesora.
- Vínculos SF.
- Inicios y fines colgantes, evaluados a nivel de inicio/fin y no solo de actividad.
- Puntos de convergencia con N o más predecesoras.
- Actividades con un calendario distinto al dominante.
- LOE con lógica impropia.
- Actividades sin los códigos o la WBS requeridos.
- Densidad de lógica: se reporta, sin umbral por defecto.

**Perfiles:** archivos `profiles/*.yaml` con umbrales, poblaciones y pesos (`dcma_estricto`, `corporativo`, `contratista`). El usuario puede crear y guardar perfiles desde la UI.

**Índice de calidad compuesto:** de 0 a 100, con pesos configurables por perfil. Siempre se muestra junto a su desglose.

### M2 · Rutas crítica y subcrítica (AACE 49R-06)

- **Modos de cálculo:**
  - Modo A (Fase 1): usa las fechas y holguras guardadas por P6, incluidos `float_path` y `float_path_order` si existen.
  - Modo B (Fase 2): recalcula con el motor propio.
- **Ruta crítica:** por holgura total ≤ X o por longest path, con comparación entre ambos criterios.
- **Bandas de holgura** configurables (p.ej. ≤ 0, 0–10, 10–20, 20–44 y > 44 días).
- **Vínculos driving** (holgura libre del vínculo = 0) y trazado de la cadena driving hacia cualquier hito elegido.
- ***Multiple float paths*** calculados por el motor, sin depender de que P6 los haya corrido. Documentar el algoritmo y compararlo con P6 cuando existan los campos.
- **Continuidad de la ruta crítica:** verificar que va desde la fecha de corte hasta el término sin quiebres injustificados.
- **CP Test** (DCMA 12).

### M3 · Lógica redundante (diagnóstico)

**Definición formal**
1. **Grafo de eventos:** cada actividad i genera dos nodos, `S_i` y `F_i`, unidos por un arco interno `S_i → F_i` cuyo peso es la duración (la remanente si hay avance).
2. **Vínculos como arcos**, con peso igual al lag:
   - FS = `F_p → S_s`
   - SS = `S_p → S_s`
   - FF = `F_p → F_s`
   - SF = `S_p → F_s`
3. **Candidato:** el vínculo e = (u → v, w) es candidato si existe otro camino u ⇝ v que no usa e y cuya longitud es ≥ w. Cálculo: longest path en el DAG, restringido al rango topológico entre u y v; agrupar los candidatos por nodo origen para eficiencia.
4. **Confirmación obligatoria.** Como los pesos están en tiempo de calendarios distintos y hay avance, la etapa 3 es solo un filtro. Para confirmar:
   - se eliminan los candidatos y se reprograma con el motor CPM;
   - no puede cambiar ninguna fecha (ES/EF/LS/LF) ni holgura (TF/FF) de ninguna actividad;
   - si la confirmación por lote falla, se aísla el vínculo culpable por bisección;
   - **validación conjunta final obligatoria:** el conjunto confirmado completo se elimina de una vez y se reprograma. Si cambia algo, se reduce el conjunto hasta que el conjunto entero dé delta cero. Confirmar subconjuntos por separado no basta: dos vínculos pueden ser redundantes cada uno por el otro.
5. **Prohibido:**
   - marcar un vínculo como redundante solo porque hoy no es driver;
   - usar `networkx.transitive_reduction` como criterio (ignora tipos y lags).

**Protecciones.** Se aplican como verificación final explícita, aunque la definición ya las excluya:
- Ninguna eliminación deja un inicio sin predecesora ni un fin sin sucesora (a nivel de evento).
- Los pares SS+FF entre las mismas actividades quedan intactos.
- Los vínculos externos (interproyecto) están protegidos por defecto.
- Los vínculos hacia o desde hitos contractuales están protegidos por defecto. Los hitos se identifican por código de actividad, UDF o lista.
- El usuario puede definir sus propias listas de protección.

**Clasificación de salida:** `redundante_confirmado`, `candidato_no_confirmado` o `protegido (regla X)`.

**Reporte por vínculo:** predecesora y sucesora (código y nombre), tipo, lag, camino alternativo (cadena de actividades), longitud del camino vs. lag, resultado de la confirmación, estado y regla aplicada.

### M4 · Limpieza de XER

- **Flujo:**
  1. Se ejecuta M3.
  2. La UI muestra una tabla de selección; por defecto quedan marcados los confirmados no protegidos.
  3. **Simulación:** DCMA y densidad antes y después.
  4. El usuario aprueba.
  5. Se escribe el XER limpio.
- El writer elimina **solo filas de `TASKPRED`**; el resto del archivo queda idéntico byte a byte.
- **Validación posterior automática:**
  - releer el XER limpio, reprogramar y verificar delta cero;
  - generar un diff que demuestre que solo cambiaron filas de `TASKPRED`.
  - **Si cualquiera de las dos falla, no se escribe el XER limpio:** el módulo termina con error y reporta los vínculos involucrados.
- **Salidas:** XER limpio, Excel de justificación y `run_manifest.json`.
- Modo lote para varios XER.
- `MANUAL_USUARIO.md` incluye el checklist de importación en P6 como proyecto nuevo y la verificación posterior (reprogramar y comparar).

### M5 · Sensibilidad y riesgo (AACE 57R-09)

**Determinística**
- Atraso de +X días o +Y % por actividad (o por filtro) y su impacto en los hitos seleccionados, presentado en un gráfico tornado.
- Solo se recalcula el cono de sucesoras afectado.

**Monte Carlo**
- **Entradas:**
  - incertidumbre por actividad o por categoría (código de actividad), con rangos mínimo / más probable / máximo;
  - distribuciones triangular, BetaPERT y uniforme;
  - correlación entre actividades mediante Iman-Conover;
  - eventos de riesgo con probabilidad, distribución de impacto y actividades afectadas.
- **Ejecución:** iteraciones configurables (1.000 por defecto) con semilla registrada. Motor vectorizado con numba sobre el mismo índice de tiempo laboral.
- **Salidas:**
  - por hito: P50, P80 y P90, histograma y curva acumulada;
  - por actividad: índice de criticidad, SSI (= criticidad × σ_actividad / σ_proyecto), índice de crucialidad y sensibilidad de duración (Spearman);
  - tornado de drivers (actividades y eventos de riesgo);
  - efecto de convergencia: determinístico vs. P50 en los puntos de convergencia.
- **Invariante:** con rangos de ancho cero y sin eventos, el resultado reproduce exactamente el CPM determinístico.

### M6 · Recursos, EVM y Earned Schedule

- **Distribución temporal** de cantidades y costos por asignación, usando curvas de recurso y calendarios, en periodos de día, semana o mes. Si falta información sobre cómo se distribuyen los reales, se asume distribución lineal y se registra como aproximación.
- **Histogramas** por recurso, rol o código, y sobreasignación contra límites (`RSRCRATE`; verificar campos).
- **Curvas S** en HH y costo: baseline, plan actual y real a la fecha de corte.
- **EVM** a la fecha de corte por WBS y total: PV, EV, AC, SPI y CPI. El EV respeta el tipo de % completo de cada actividad (físico, duración o unidades).
- **Earned Schedule:**
  - ES por interpolación de la PV;
  - SPI(t) = ES / AT;
  - IEAC(t) = PD / SPI(t).

  Las fórmulas quedan documentadas.

### M7 · Comparación de updates y tendencias

- Emparejamiento por `task_code` (configurable).
- **Diferencias:**
  - actividades agregadas y eliminadas;
  - vínculos agregados, eliminados o modificados (tipo o lag);
  - cambios de duración original y remanente;
  - cambios de restricciones, calendarios y fechas reales;
  - erosión de holgura;
  - entradas y salidas de la ruta crítica.
- **Tendencias** a lo largo de varios updates, desde la biblioteca: BEI, CPLI, holgura de hitos clave, cambios de ruta crítica y volumen de cambios de lógica.
- Registro de cambios exportable a Excel, trazable y apto como respaldo documental.

### Transversales

- **UI:**
  1. Cargar archivo(s).
  2. Ver resumen y validación.
  3. Elegir módulos (casillas), con sus requisitos visibles (p.ej. "requiere baseline").
  4. Configurar cada módulo, con selector de perfil.
  5. Ejecutar, con barra de progreso.
  6. Revisar resultados en pestañas.
  7. Exportar.

  Botón "Informe completo" que genera PDF y Excel combinados.
- **Visor:**
  - Gantt (Plotly) con la ruta crítica y las bandas de holgura resaltadas, y filtros por WBS o código;
  - trazado de predecesoras y sucesoras a N niveles, y de la cadena driving.
- **Lote:** se elige una carpeta de entrada, se ejecutan los módulos elegidos sobre cada archivo y se obtiene un ranking comparativo por índice de calidad en un Excel consolidado.
- **Biblioteca (DuckDB):** guarda manifiestos, métricas y hallazgos por corrida. No guarda el cronograma completo, salvo opción explícita. Alimenta las tendencias.
- **Exportación:**
  - Excel con hoja resumen y una hoja por módulo, con filtros y formato condicional;
  - PDF ejecutivo de 1 a 2 páginas en español: scorecard, métricas clave, resumen de ruta crítica y principales riesgos;
  - Parquet en esquema estrella: `dim_project, dim_run, dim_activity, dim_rule, fact_finding, fact_timephased, fact_risk`.
- **Power BI (Fase 4):** proyecto PBIP con modelo semántico en TMDL, que lee la carpeta Parquet mediante un parámetro e incluye relaciones y medidas DAX base. Verifica la documentación vigente de Microsoft sobre PBIP/TMDL antes de generarlo. Nicolás construye las visualizaciones.

---

## 7. Datos de prueba

1. **Generador sintético** (`scripts/gen_synthetic.py`):
   - Produce XER válidos a partir de especificaciones en Python o YAML, **con tablas y campos reales de P6** (`PROJECT, CALENDAR, PROJWBS, TASK, TASKPRED`…), documentados en `XER_SPEC.md`. Nada de tablas inventadas (p.ej. `SYNTH`): todo sintético debe poder importarse en P6.
   - Casos pequeños (5–30 actividades) con resultados esperados calculados a mano y documentados en YAML.
   - **Casos borde que debe cubrir:**
     - los 4 tipos de vínculo, con lags positivos y negativos;
     - varios calendarios con feriados, medias jornadas, 24 h y 7 días;
     - cada tipo de restricción;
     - avance fuera de secuencia;
     - LOE, WBS summary e hitos;
     - vínculos externos y extremos abiertos;
     - ciclos (error esperado);
     - pares SS+FF;
     - cadenas con redundancia real;
     - vínculos que no son driver y **no** son redundantes;
     - multiproyecto;
     - baseline.
   - Generador de escala (`scripts/gen_scale.py`; 5k, 30k y 60k actividades) para las pruebas de rendimiento. Produce redes **realistas**: WBS, varios calendarios con feriados, mezcla FS/SS/FF/SF, lags, restricciones, avance parcial, 2 a 3 predecesoras promedio y cadenas largas (incluida una variante en serie de 60k para robustez). Un XER de 2 columnas no sirve como benchmark.
2. **Verificados en P6** (`tests/fixtures/p6_verified/`):
   - Cuando pueda, Nicolás importa los sintéticos en P6 (en un EPS de pruebas), los programa con las opciones especificadas y los reexporta. Deja las instrucciones exactas (archivos, opciones de programación) en `VALIDACIONES_PENDIENTES.md`.
   - Antes de entregarlos, los pasa por `scripts/sanitize_fixture.py`, que anonimiza `ERMHDR`, usuarios, OBS y nombres de base de datos.
   - Son la verdad de P6 sin datos confidenciales, y tú sí puedes leerlos.
   - **Mientras no existan,** los tests que dependen de ellos se omiten con `skip` y motivo, y el motor se valida contra los esperados calculados a mano de los sintéticos. No esperes por ellos.
3. **Oráculo independiente:**
   - Los esperados de cada caso los escribe `fixtures` y los recalcula `qa-oraculo` por otro método: cálculo tabulado a mano o implementación de referencia mínima en `tests/oracle/`, que nunca importa `src/atlaspmo`.
   - Un esperado entra a `tests/fixtures/` solo si ambos cálculos coinciden; la doble firma queda en el YAML (`calculado_por`, `verificado_por`, `metodo`).
   - Los agentes que implementan no editan esperados ni oráculos.
4. **Golden reales:** solo en `ATLASPMO_GOLDEN_DIR`. Los corre Nicolás con `scripts/run_conformance.py`.

**Invariantes con hypothesis (DAG aleatorios; obligatorios, en `tests/property/`, perfil `qa` con ≥ 500 ejemplos por propiedad y semilla registrada)**
- a) Leer y escribir sin cambios produce un archivo idéntico.
- b) Una limpieza nunca altera fechas ni holguras.
- c) Un vínculo implícito agregado artificialmente se detecta como redundante.
- d) Eliminar un vínculo driving no redundante cambia fechas, y ese vínculo nunca se marca como redundante.
- e) Monte Carlo con varianza cero reproduce el CPM determinístico.

---

## 8. Calidad de ingeniería y sistema QA/QC

Cambios respecto de la v2 en ADR-019: cobertura como trinquete, metas reales de la sección 11 que se activan por etapa, y mutación informativa.

### 8.1 Estándares de código

- **Cobertura:** las metas siguen siendo ≥ 90 % de líneas y ≥ 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`, y ≥ 80 % de líneas en el resto. Funcionan como **trinquete** sobre `docs/qa/baseline.json`: ningún paquete puede caer más de 0,5 puntos bajo su línea base, y la distancia a la meta se informa sin bloquear. **El código nuevo de la v3 sí debe cumplir la meta:** el motor rápido, la redundancia y Monte Carlo se escriben con sus tests. Cuando un paquete supera su línea base, súbela con un commit que cite ADR-019.
- `ruff check`, `ruff format --check` y `mypy` sin errores (mypy estricto en `model`, `calendars`, `engine` y `analysis/logic`). Los núcleos numba van en módulos aparte, con firmas tipadas en el envoltorio Python.
- Tests: `uv run python -m pytest`.
- La lógica de negocio nunca vive en la UI. Errores en español y accionables.

### 8.2 Principios QA/QC

1. **Separación de funciones.** Quien implementa no edita oráculos, esperados, umbrales, `baseline.json`, `seccion11.toml` ni el gate (los cambios en `baseline.json` y `seccion11.toml` los hace el orquestador al cerrar una etapa aprobada, citando ADR-019).
2. **Rechazo por defecto.** La entrega demuestra que cumple, con evidencia.
3. **El producto primero** (regla 3 de la sección 0).
4. **Sin regresión.** Un test, una meta activa o un benchmark que pasó no se elimina ni se relaja.
5. **Severidad sin negociación** (8.5).

### 8.3 Gate automático — `scripts/qa_gate.py`

Comando: `uv run python scripts/qa_gate.py --etapa E<n> --base <commit base de la v3>`. El commit base se registra en `ESTADO.md` al arrancar (sección 15).

| ID | Control | Falla si | Cambio v3 |
|---|---|---|---|
| G1 | Lint y formato | `ruff check` o `ruff format --check` reportan algo | — |
| G2 | Tipos | `mypy` reporta errores | — |
| G3 | Suite completa | algún test falla o hay errores de colección | — |
| G4 | Cobertura | un paquete cae más de 0,5 puntos bajo `baseline.json` | trinquete |
| G5 | Propiedades | faltan los invariantes a–e con el perfil `qa` (≥ 500 ejemplos) | — |
| G6 | Rendimiento | falla `tests/perf` o una meta activa de `docs/qa/seccion11.toml` | metas reales a 30k |
| G7 | Omisiones | hay un skip o xfail fuera de `skips.toml` | — |
| G8 | Privacidad y red | cronogramas fuera de fixtures, `data/real/`, `.env`, rutas de perfil, imports de red, Streamlit expuesto | — |
| G9 | Campos XER | un campo o tabla usados no están en `XER_SPEC.md` | — |
| G10 | Trazabilidad | un R-xxx de la etapa no cita un test existente | — |
| G11 | Rutas protegidas | cambió una ruta protegida sin un commit que cite un ADR | `baseline.json` y `seccion11.toml` son rutas protegidas |
| G12 | Regresión | bajan los tests, la cobertura total cae más de 0,5 o un benchmark empeora más de 20 % | — |
| G13 | Mutación | — (informativo: se mide y se reporta, no bloquea) | informativo |

**Metas de la sección 11** (`tests/perf/test_seccion11.py`, marca `seccion11`; todas sobre la red realista de `gen_scale.py` con 30.000 actividades):

| Meta | Límite | Medido en la revisión (`cc81a31`, Linux) | Se activa en |
|---|---|---|---|
| `lectura_30k` | 15 s | 1,8 s | ya activa |
| `cpm_30k` (después del calentamiento) | 0,5 s | 15,8 s | E7 |
| `dcma_30k` (CPM + DCMA) | 10 s | 16,1 s | E7 |
| `redundancia_30k` (filtro + confirmación) | 180 s | 52,5 s **con solo 300 actividades** | E8 |
| `montecarlo_30k` (1.000 iteraciones) | 300 s | 49,1 s **con 300 actividades y 5 iteraciones** | E9 |

Para correrlas todas: `uv run python -m pytest -m seccion11 tests/perf/test_seccion11.py -s`. Para una prueba rápida con otra escala: `ATLASPMO_S11_SIZE=300`. Fuera de 30.000 actividades se imprime el tiempo, pero no se exige la meta. Una meta se agrega a `activas` solo cuando pasa a 30.000 actividades en el equipo de Nicolás, y no se quita nunca.

### 8.4 Controles QC por etapa

| QC | Control | Responsable | Sale con |
|---|---|---|---|
| QC-1 | Contrato: requisitos R-xxx en `TRAZABILIDAD.md`, criterio ejecutable y oráculo, **antes** del código | orquestador, revisado por `qa-spec` | `docs/qa/E<n>/QC1_contrato.md` |
| QC-2 | Oráculo: esperados de `fixtures`; segunda firma de `qa-oraculo` cuando sea posible (si falta, queda `pendiente_segunda_firma`). **En E7–E9 el oráculo principal es el motor de referencia** (prueba diferencial, sección 10.3) | `fixtures`, `qa-oraculo` | esperados y tests diferenciales |
| QC-3 | Implementación con test primero, en worktree | agentes que implementan | diff + evidencia de rojo a verde |
| QC-4 | Revisión adversarial y privacidad. `qa-sabotaje` es opcional en la v3 (G13 informativo) | `qa-revisor`, `qa-privacidad` | `docs/qa/E<n>/hallazgos.md` |
| QC-5 | Integración y gate completo | orquestador | `gate.json` |
| QC-6 | Veredicto APROBADO, o RECHAZADO con la lista de hallazgos | `qa-revisor` | `docs/qa/E<n>/VEREDICTO.md` |

**Regla de cierre:** APROBADO exige el gate en verde y 0 hallazgos críticos o importantes abiertos. Tras 3 ciclos sin aprobar (y cada ciclo con cambios de producto, regla 3): RECHAZADA-BLOQUEADA, y se sigue (0.3).

**Control técnico de solo lectura:** al terminar `qa-spec`, `qa-revisor` y `qa-privacidad`, `git status --porcelain` de su worktree debe quedar limpio. Si no, se descartan sus cambios y se registra un hallazgo.

**Documentación QA mínima:** por etapa, `QC1_contrato.md`, `hallazgos.md`, `VEREDICTO.md`, `gate.json` y `gate.md`, y `perf.md` si hay mediciones. Nada más, salvo evidencia que un hallazgo exija.

### 8.5 Severidad

| Severidad | Incluye | Efecto |
|---|---|---|
| Crítico | resultado numérico distinto del motor de referencia o de un esperado; pérdida o corrupción de datos; XER escrito con cambios fuera de `TASKPRED`; violación de privacidad; caída con una entrada válida; una meta activa de la sección 11 incumplida; afirmar algo sin evidencia | bloquea el cierre |
| Importante | desviación de la spec; aproximación silenciosa; test que no prueba lo que dice; caso borde sin cubrir; código nuevo bajo la meta de cobertura | bloquea el cierre |
| Menor | estilo, nombres, documentación que no cambia resultados | se registra |

---

## 9. Organización multiagente en Grok Build

### 9.1 Mecánica confirmada (ADR-001, Grok Build 1.0.62)

Revalídala al inicio de E0 con `grok --trust-folder inspect --json` dentro del repositorio y actualiza ADR-001 si cambió. La documentación vigente manda sobre este documento.

- **Instrucciones del proyecto:** `AGENTS.md` en la raíz del repositorio.
- **Subagentes personalizados:**
  - Archivos Markdown con frontmatter YAML en `.grok/agents/<nombre>.md`, con `name` y `description`.
  - `tools` solo con nombres de herramientas confirmados.
- **`spawn_subagent`** acepta `prompt`, `description`, `background`, `isolation`, `resume_from` y `cwd`. `subagent_type` aparece cuando existen agentes de proyecto: confírmalo con `inspect` y úsalo para lanzar cada rol por su `name`.
- **Capacidades:** `capability_mode` no es argumento de spawn; lo fija el tipo de agente o un rol. Averigua si un agente de proyecto puede declararse de solo lectura. Si se puede, aplícalo a `qa-spec`, `qa-revisor` y `qa-privacidad`; si no, rige el control técnico de 8.4.
- **Un solo nivel de anidamiento:** los subagentes no lanzan subagentes. Toda la orquestación vive en la sesión principal.
- **Contexto propio:** no asumas que un subagente carga `AGENTS.md`. Cada brief repite las reglas críticas (9.3).
- **Built-ins:** `explore`, `plan` y `general-purpose`.

### 9.2 Rol de la sesión principal (orquestador)

- Escribe el plan de la etapa en `ESTADO.md` y define contratos e interfaces **antes** de delegar.
- Delega con el brief de 9.3. Nunca delegues sin criterios de aceptación ejecutables.
- **Paralelismo:**
  - Solo para entregas en directorios disjuntos, con `background: true` e `isolation: "worktree"`.
  - Máximo 3 subagentes simultáneos.
  - Integra cada worktree solo después de revisar su diff y de que pase su subconjunto del gate.
  - Si dos entregas tocan los mismos archivos, van en secuencia.
- **Prohibido autoaprobarse:** el orquestador no escribe `VEREDICTO.md` ni cambia un hallazgo a cerrado sin la verificación de `qa-revisor`.
- **Cierre de etapa:** con APROBADO, actualizas `ESTADO.md`, haces commit y push de `v3` (sección 9.5) y sigues con la etapa siguiente.

### 9.3 Brief de delegación (obligatorio en cada `spawn_subagent`)

```
ETAPA / BRECHAS: E<n> · B-xx, B-yy
OBJETIVO: <qué debe quedar funcionando>
ARCHIVOS QUE POSEES: <rutas>          NO TOCAR: <rutas; siempre incluye tests/fixtures/**/expected*, tests/oracle/**, docs/qa/skips.toml, scripts/qa_gate.py salvo que seas su dueño>
CONTRATO: <interfaces/firmas que debes cumplir o consumir>
REQUISITOS: <R-xxx de docs/qa/TRAZABILIDAD.md>
ACEPTACIÓN: <tests que deben pasar + comando exacto> · TEST PRIMERO: guarda la salida en rojo antes del arreglo
ORÁCULO: <de dónde salen los esperados; nunca de tu propio código>
CONTEXTO: <secciones de docs/MEGAPROMPT_v3.md y docs/XER_SPEC.md a leer>
REGLAS CRÍTICAS:
- Sesión con auto-aprobación: respeta los límites duros de la sección 14.
- Nunca leer data/real/ ni ATLASPMO_GOLDEN_DIR, por ningún medio (incluido el shell).
- No inventar campos XER ni comportamientos de P6; documentar evidencia en docs/XER_SPEC.md.
- Sin aproximaciones silenciosas.
- XER: cp1252, CRLF, tablas no tocadas idénticas byte a byte.
- Código en inglés; textos de usuario en español es-CL.
ENTREGA (en docs/qa/E<n>/<agente>.md): archivos cambiados · comandos ejecutados con resultado · evidencia rojo→verde · supuestos nuevos · lo que NO pudiste verificar
```

### 9.4 Agentes en `.grok/agents/`

Los 13 agentes ya existen en `.grok/agents/` y apuntan a este documento. Mantenlos así; ajusta sus cuerpos solo si esta versión lo exige. Las descripciones van cortas y el detalle en el cuerpo. Todos los cuerpos terminan con: *"Sesión con auto-aprobación: respeta la sección 14 de docs/MEGAPROMPT_v3.md. Nunca leas data/real ni ATLASPMO_GOLDEN_DIR por ningún medio. Entrega tu informe en docs/qa/E<n>/<tu-nombre>.md con comandos y resultados."*

**Implementación**

| name | description | Cuerpo (resumen obligatorio) |
|---|---|---|
| `xer-io` | Lectores y escritores XER, P6 XML, MSPDI, MPXJ; modelo; validación al cargar. | `src/atlaspmo/io` y `model`. Evidencia por campo en `XER_SPEC.md`; round-trip byte a byte; bytes indefinidos de cp1252 preservados; validación con detección de ciclos iterativa. |
| `motor-cpm` | Calendarios P6, índice de tiempo laboral, motor CPM y conformidad. | `calendars` y `engine`. Índice O(log n) con horizonte dinámico; restricciones obligatorias en ambos pases; longest path; hitos; numba solo después de que el comportamiento sea correcto; conformidad anonimizada. |
| `logica-red` | Rutas, driving, float paths, CP Test, redundancia, protecciones y limpieza XER. | `analysis/paths` y `analysis/logic`. Candidatos por rango topológico agrupados por origen; confirmación con validación conjunta final; protecciones a nivel de evento; el cleaner no escribe si el delta no es cero. |
| `calidad` | DCMA 14, GAO-16-89G, chequeos adicionales, perfiles, índice, comparación y tendencias. | `analysis/quality` y `compare`. Definiciones exactas de la sección 6 (CPLI, BEI); "No evaluable" con motivo; cada métrica contra un esperado con doble firma. |
| `riesgo` | Sensibilidad determinística y Monte Carlo. | `analysis/risk`. Recalcular solo el cono de sucesoras; motor vectorizado; semilla registrada; invariante de varianza cero. |
| `recursos-evm` | Distribución temporal, histogramas, sobreasignación, curvas S, EVM y Earned Schedule. | `analysis/resources`. Campos verificados en `XER_SPEC.md`; EV según el tipo de % completo; supuestos de distribución como aproximación. |
| `ui-reportes` | Streamlit, visor Gantt, lote, biblioteca DuckDB, Excel, PDF, Parquet y PBIP. | `ui`, `reports`, `library`, `batch` y `powerbi/`. Flujo completo de la sección 6 (Transversales); sin lógica de negocio en la UI; progreso visible; localhost sin telemetría; tests e2e con `AppTest`. |

**Datos de prueba**

| name | description | Cuerpo (resumen obligatorio) |
|---|---|---|
| `fixtures` | Sintéticos con esperados, generador de escala y saneamiento. | `tests/fixtures` y `scripts/gen_*`. Solo tablas y campos reales de P6; cada esperado en YAML con método de cálculo; casos borde de la sección 7; independiente de quienes implementan. |

**QA (nunca implementan producto)**

| name | description | Cuerpo (resumen obligatorio) |
|---|---|---|
| `qa-spec` | Trazabilidad requisito→test y contrato de cada etapa (QC-1). No edita archivos. | Construye y audita `docs/qa/TRAZABILIDAD.md`; rechaza requisitos sin criterio ejecutable o sin fuente de oráculo. |
| `qa-oraculo` | Recalcula esperados de forma independiente (QC-2). | Solo `tests/oracle/` y la firma `verificado_por` de los YAML. Nunca lee ni importa `src/atlaspmo`. Usa otro método: tabla a mano, fuerza bruta o networkx como referencia. |
| `qa-revisor` | Revisor adversarial y veredicto de etapa (QC-4 y QC-6). No edita archivos. | Contrasta con las secciones 2, 6, 8 y 11; busca aproximaciones silenciosas, campos sin evidencia y tests que no prueban lo que dicen; clasifica por severidad (8.5); emite APROBADO solo con gate en verde y 0 críticos o importantes. Si algo no puede verificar, lo dice. |
| `qa-sabotaje` | Mutación dirigida sobre los módulos tocados (G13). | Trabaja en un worktree desechable; introduce fallos plausibles (operadores, off-by-one en lags, mapeo FS/SS/FF/SF, calendarios, signos de holgura); reporta los mutantes sobrevivientes con el test que faltaría. Nunca integra cambios. |
| `qa-privacidad` | Auditoría de privacidad, red y seguridad de cada etapa. No edita archivos. | Revisa el diff contra G8 y la sección 14; revisa `ERMHDR` de fixtures, logs y mensajes que podrían filtrar nombres reales, y los comandos de red registrados en `docs/qa/E<n>/acciones.md`. |


### 9.5 Ciclo por etapa

1. Plan de la etapa en `ESTADO.md`.
2. QC-1 → QC-2 → QC-3 → QC-4 → QC-5 → QC-6 (sección 8.4).
3. Si es RECHAZADO: corrección con cambios de producto y nuevo ciclo, hasta 3. Después: RECHAZADA-BLOQUEADA, y se sigue.
4. Al cierre (aprobada o bloqueada):
   - si fue aprobada y la etapa cumple sus metas, agrega esas metas a `docs/qa/seccion11.toml` y sube `baseline.json` si corresponde (commit que cite ADR-019);
   - actualiza `ESTADO.md`, `DECISIONES.md` y `VALIDACIONES_PENDIENTES.md`;
   - corre G8;
   - haz `git push -u origin v3`, con hasta 4 reintentos y espera creciente si falla la red; si sigue fallando, continúa en local y repórtalo;
   - continúa con la etapa siguiente.

**Rama:** `v3`, creada desde `origin/claude/beautiful-goodall-m0q2zj`. Nunca se mergea a `main`.

---

## 10. Estado tras la v2 y etapas de la v3

### 10.1 Qué dejó la v2 (revisión externa del 2026-10-22 sobre `cc81a31`)

Verificado de forma independiente: 216 tests en verde; el gate reproduce el mismo resultado (solo fallan G4 y G13).

| Cerradas y comprobadas | Abiertas |
|---|---|
| B-03 confirmación conjunta y XER bloqueado con delta ≠ 0 · B-05 ciclos iterativos (cadena de 30k en serie y 87 años sin error) · B-06 horizonte dinámico · B-08 obligatorias imponen su fecha · B-09 longest path · B-15 invariantes a–e · B-18 formato · B-19 referencias · B-20 bytes cp1252 · B-21 hito al inicio laboral siguiente. B-08, B-09 y B-21 siguen `[VALIDAR]` con P6 | **B-07 y B-16, rendimiento** (crítico) · **B-02, redundancia a escala** (crítico) · B-01 UI incompleta · B-10 y B-11 sin segunda firma · B-12 sin multiple float paths ni continuidad · B-13 sin curvas por periodo ni histogramas · B-14 bordes de la sección 7 incompletos · B-22 y B-23 (historia, los decide Nicolás) |

### 10.2 Diagnóstico de rendimiento (perfil de la revisión)

Red de `gen_scale.py` con 300 actividades, bajo cProfile:
- **Reloj laboral.** `WorkCalendar._earliest` resuelve cada `add_work` y `subtract_work` con una búsqueda binaria de ~30 iteraciones sobre minutos absolutos, y cada iteración llama a `_cumulative`, que recorre en Python los turnos del día. El "O(log n)" de B-06 tiene una constante enorme: el 85–90 % del tiempo del CPM se va ahí. 30k actividades: CPM de 15,8 s.
- **Monte Carlo.** `_tornado` corre un CPM completo por actividad aunque `tornado_hours` sea 0. Con 300 actividades: 148 de 151 s son tornado. Las iteraciones también recalculan el cronograma completo, reconstruyendo el modelo (`_with_hours`).
- **Redundancia.** 336 CPM completos para 300 actividades: bisección (`_confirm`) más validación conjunta (`_join`), cada uno un CPM completo.

### 10.3 Etapas

Las etapas siguen la numeración de la v2 para que G12 compare contra la etapa anterior (E6 → E7).

**E7 · Motor rápido** (B-16, base de B-07 y B-02). La etapa más importante: si E7 no queda bien, E8 y E9 no tienen base.

- **Diseño obligatorio:**
  1. **Compilar el cronograma a arrays** una sola vez:
     - índices 0..n-1 en orden topológico;
     - predecesoras y sucesoras en CSR (`indptr`, `indices`, tipo de vínculo como entero, lag en minutos laborales);
     - duración remanente en minutos;
     - calendario como índice;
     - estado, fechas reales y restricciones como arrays.
  2. **Tiempo en una sola unidad:** instantes como minutos absolutos desde una época (int64), y cada calendario como una tabla de intervalos laborales `[inicio, fin)` sobre todo el horizonte, con el trabajo acumulado al inicio de cada intervalo (arrays numpy concatenados, con offsets por calendario).
     - `add_work`, `subtract_work` y `work_between` = **una** `searchsorted` más aritmética;
     - la tabla crece si el horizonte no alcanza (sin tope fijo, como exige B-06).
  3. **Pases en numba** (`@njit(cache=True)`) sobre esos arrays: forward, backward, holgura total, holgura libre y libre por vínculo, crítico por holgura y longest path.
     - Restricciones, avance (retained, progress override, actual dates), calendario del lag, hitos y LOE/WBS **exactamente** con la semántica del motor actual.
     - Lo que no quepa en numba se resuelve antes o después en numpy, nunca por actividad en Python.
  4. **El motor actual queda como referencia:** `engine/cpm.py` no se borra.
     - El motor rápido se expone con la misma firma (`schedule_cpm` decide cuál usar con una opción y, por defecto, usa el rápido).
     - La referencia se llama de forma explícita en los tests.
- **Oráculo de E7 = prueba diferencial obligatoria:**
  - hypothesis genera redes aleatorias con varios calendarios (feriados, medias jornadas, 24 h, 7 días), los 4 tipos de vínculo, lags positivos y negativos, cada restricción, avance fuera de secuencia, hitos, LOE y WBS;
  - el motor rápido y la referencia deben dar **ES, EF, LS, LF, TF y FF idénticos al minuto** y la misma lista de aproximaciones;
  - además, todos los tests existentes del motor pasan con el rápido.
- **Metas a activar:** `cpm_30k` (< 0,5 s después del calentamiento) y `dcma_30k` (< 10 s).
- Que el orden topológico y la compilación a arrays no dominen el tiempo: mídelos aparte en `perf.md`.

**E8 · Redundancia a escala** (B-02).

- El filtro de candidatos por origen ya está en 0,3 s para 30k; no lo toques salvo para el diferencial.
- **Confirmación:** usa el motor rápido sobre los arrays ya compilados.
  - Quitar vínculos = enmascarar aristas del CSR, sin reconstruir el modelo.
  - Bisección y validación conjunta igual que hoy (ADR-016), pero cada reprogramación es un pase rápido.
  - Si hace falta, recalcula solo el cono afectado y verifica que el resultado sea idéntico al de un pase completo.
- **Diferencial:** la clasificación del motor rápido es idéntica a la del motor de referencia en redes chicas aleatorias (hypothesis) y en los casos de la sección 7.
- **Meta a activar:** `redundancia_30k` (< 180 s).

**E9 · Monte Carlo y tornado** (B-07).

- Muestreo vectorizado: matriz `iteraciones × actividades` en numpy, con la semilla registrada; Iman-Conover sobre esa matriz; eventos de riesgo vectorizados.
- Pases en numba con `prange` sobre las iteraciones, con los arrays de E7. Sin reconstruir `Schedule` por iteración.
- **Tornado:**
  - corre solo si `tornado_hours > 0`;
  - recalcula solo el cono de sucesoras de la actividad atrasada, como exige la spec;
  - diferencial contra el cálculo completo en redes chicas.
- Invariante e) (varianza cero = CPM determinístico) con el motor rápido.
- **Meta a activar:** `montecarlo_30k` (< 300 s con 1.000 iteraciones).

**E10 · Funcionalidad pendiente**, en este orden y sin metas de tiempo nuevas:

1. B-01: e2e completo de la UI (sección 6, Transversales), incluido el baseline asociado, configuración por perfil, visor Gantt con filtros y trazado N niveles, lote y biblioteca.
2. B-12: multiple float paths propios, continuidad desde la fecha de corte y driving en modo A cuando P6 trae los campos.
3. B-13: distribución por periodo (día, semana, mes), histogramas, sobreasignación contra `RSRCRATE` (solo con campos con evidencia) y curvas S.
4. B-14: los bordes de la sección 7 que falten, con esperados.
5. B-10 y B-11: segunda firma de los esperados de CPLI (con solape SS y feriado) y de BEI.

Cada punto de E10 es una entrega con su test e2e o con esperado; E10 puede cerrar con puntos abiertos si están registrados.

**Validaciones de Nicolás** (nunca te detienen; mantenlas en `VALIDACIONES_PENDIENTES.md`): `p6_verified`, B-08, B-09 y B-21 en P6, conformidad con golden, XER limpio en P6, PBIP en Power BI Desktop, `.mpp` con Java, decisión sobre la historia de B-23.

---

## 11. Criterios de aceptación globales

| Criterio | Meta |
|---|---|
| Lectura de un XER de 30k actividades | < 15 s |
| DCMA + chequeos de calidad | < 10 s |
| Redundancia con confirmación | < 3 min |
| Monte Carlo, 1.000 iteraciones, 30k actividades | < 5 min |
| Conformidad CPM vs. P6 | ≥ 99,5 % exacto en reales; 100 % en `p6_verified`; 100 % de diferencias explicadas |
| XER limpio | Importa en P6 sin errores; al reprogramar, delta cero |
| Round-trip XER | Idéntico byte a byte |
| Instalación | Sin permisos de administrador |
| Pruebas | Unitarias, de propiedades, de conformidad y de rendimiento en verde |

Los criterios se miden con `scripts/gen_scale.py` (redes realistas, sección 7) y se registran en G6 con los datos del equipo. "No medido" nunca equivale a cumplido.

---

## 12. Anti-patrones prohibidos

- Inventar campos, códigos o comportamientos de P6 sin evidencia.
- Declarar algo terminado sin haber ejecutado sus tests, o afirmar algo sin evidencia en `docs/qa/`.
- Usar la reducción transitiva genérica, o el criterio "no es driver", para decidir redundancia.
- Confirmar redundancia por subconjuntos sin validar el conjunto final; escribir un XER limpio con delta distinto de cero.
- Reescribir el XER completo al limpiar.
- Leer o pedir archivos reales por cualquier medio; exponer nombres de actividades reales en logs compartibles.
- Dependencias que exijan administrador, compilador o red en ejecución.
- Aproximaciones silenciosas, `except: pass`, lógica de negocio en la UI.
- Tablas o campos XER inventados en los sintéticos; benchmarks sobre XER de juguete.
- Recursión de Python sobre el grafo; recorridos día por día en el reloj laboral; topes fijos de horizonte.
- Recalcular el cronograma completo donde la spec pide un cono o un índice.
- Que quien implementa edite su oráculo, sus esperados, los umbrales o el gate.
- Que el orquestador escriba su propio veredicto, o cerrar una etapa con hallazgos críticos o importantes abiertos.
- Relajar un umbral, borrar un test o agregar un `skip` para pasar el gate.
- Un commit por fase o etapa en vez de commits atómicos.
- Detenerse a preguntar fuera de los casos de 0.3.
- Cualquier acción prohibida de la sección 14.
- Optimizar el motor cambiando resultados, o sin prueba diferencial contra la referencia.
- Borrar o "acelerar" el motor de referencia.
- Reconstruir el modelo o recalcular el cronograma completo dentro de un bucle de Monte Carlo, de la redundancia o del tornado.
- Ciclos de corrección que solo documentan.
- Activar una meta de la sección 11 que no pasa a 30.000 actividades, o quitar una meta activa.

---

## 13. `AGENTS.md`

Ya está actualizado a la v3 en la raíz del repositorio. Mantenlo corto y consistente con este documento.

---

## 14. Configuración de Grok Build y auto-aprobación

**La sesión corre siempre con auto-aprobación** (`permission_mode = "always-approve"` en la configuración de usuario de Nicolás, ADR-003). Ningún comando pasa por revisión humana. Por eso estas reglas son **límites duros**: violarlos es un hallazgo crítico y te detiene (0.3).

### 14.1 Límites duros

1. **Archivos.** Solo lees y escribes dentro de la raíz del repositorio y de los worktrees que crees, más las cachés de `uv` y Python. Nunca lees, listas ni buscas:
   - `data/real/` ni `ATLASPMO_GOLDEN_DIR`;
   - `~/.ssh`, credenciales, perfiles de navegador;
   - otras carpetas del usuario.

   Esto vale por cualquier medio: herramientas, `cat`, `type`, `Get-Content`, `dir`, Python, etc.
2. **Configuración de usuario.** No escribes en `~/.grok/`. En `~/.streamlit/` solo se admite lo necesario para que Streamlit arranque sin preguntar ni enviar datos; cada cambio queda registrado en `DECISIONES.md`.
3. **Red.** Solo para:
   - instalar dependencias con `uv` desde PyPI;
   - leer documentación oficial (Microsoft Learn, Oracle Primavera, MPXJ, documentación de las librerías);
   - `git fetch` y `git push` de la rama `v3` a `origin`.

   Nunca subas contenido a otros servicios (gists, pastebins, APIs, issues), ni siquiera fragmentos de código.
4. **Git.** Prohibido:
   - push a `main`;
   - `--force` o `--force-with-lease`;
   - `reset --hard` sobre ramas publicadas;
   - borrar ramas remotas;
   - reescribir historia publicada.

   `git worktree remove` solo sobre tus worktrees.
5. **Sistema.** Sin `sudo` ni administrador; sin instalar software del sistema; sin tocar PATH, registro o servicios; sin `rm -rf` ni `Remove-Item -Recurse` fuera de tus worktrees y carpetas temporales del repositorio.
6. **Bitácora.** Cada instalación, acceso a red y push queda en `docs/qa/E<n>/acciones.md` (comando, motivo, resultado). `qa-privacidad` la audita.

### 14.2 Controles técnicos

- `.grok/config.toml` del proyecto niega `Read`, `Edit` y `Grep` sobre `**/data/real/**` (ya existe; consérvalo). Agrega `**/.env` y cualquier otra regla de denegación que Grok Build admita a nivel de proyecto.
- Hooks pre-commit y pre-push con G8. El pre-push además rechaza cualquier destino distinto de `origin/v2` u `origin/v3`; en la v3 solo se empuja `v3`.
- **Recomendaciones para Nicolás** (escríbelas con el texto exacto en `VALIDACIONES_PENDIENTES.md`; no las apliques tú):
  - una regla de denegación con la ruta absoluta de su carpeta golden en `~/.grok/config.toml`;
  - mantener los golden en una unidad o contenedor cifrado desmontado durante las sesiones de Grok.

### 14.3 Otros harnesses

Si Nicolás usa Grok 4.7 desde Cursor o GitHub Copilot, `AGENTS.md` y esta sección siguen aplicando. Los roles de 9.4 se ejecutan en secuencia dentro de la sesión, con el mismo brief y los mismos controles QC. La separación de funciones se mantiene: el rol QA nunca revisa un cambio que escribió el mismo turno sin pasar antes por el gate.

---


## 15. Arranque

**Estado de partida:** la rama `v3` nace de `origin/claude/beautiful-goodall-m0q2zj`, que contiene `v2` (`cc81a31`), el gate ajustado (ADR-019), las metas de la sección 11 y este documento. `docs/MEGAPROMPT_v2.md` ya no existe: este documento lo reemplaza.

1. Verifica que estás en `v3` con el árbol limpio. Si no existe: `git checkout -b v3 origin/claude/beautiful-goodall-m0q2zj`.
2. Registra en `ESTADO.md` el inicio de la v3 y el **commit base** (`git rev-parse HEAD`). Ese hash va en `--base` de todos los gates de la v3.
3. Lee este documento completo, `ESTADO.md` (reporte final de la v2) y `DECISIONES.md` (ADR-001 a ADR-019). Si `ESTADO.md` indica una etapa v3 en curso, retómala desde el control pendiente.
4. **Comprobación inicial**, con la evidencia en `docs/qa/E7/inicio.md`:
   - `uv run python -m pytest` en verde;
   - el gate con `--etapa E7` (G10 puede fallar porque E7 aún no tiene requisitos: es esperado; QC-1 lo resuelve);
   - todas las metas de la sección 11 a 30k, para registrar la línea base en el equipo de Nicolás. Si `redundancia_30k` o `montecarlo_30k` superan 30 minutos, córtalas, registra "más de 30 min" y sigue.
5. Ejecuta E7, E8, E9 y E10 con el ciclo de 9.5.
6. Al terminar E10, escribe el reporte final (sección 16), haz el último push de `v3` y detente.

---

## 16. Reporte final

Escríbelo al principio de `docs/ESTADO.md` (sección "v3 — reporte final") y muéstralo en la sesión:
- **Por etapa:** veredicto, ciclos, gate (G1–G13), último commit.
- **Metas de la sección 11:** tabla con la línea base de la v3, el valor final en el equipo de Nicolás (CPU, RAM, SO) y si está activa en `seccion11.toml`.
- **Prueba diferencial:** cantidad de ejemplos por propiedad, diferencias encontradas y corregidas.
- **Brechas:** B-01 a B-23 con su estado y evidencia.
- **Cobertura:** por paquete frente a `baseline.json` y frente a la meta; G13 informativo, si se midió.
- **Hallazgos QA** abiertos por severidad.
- **Para Nicolás:** checklist priorizado de `VALIDACIONES_PENDIENTES.md`.
- **Para la v4:** qué fue ambiguo o insuficiente en este documento.
