# MEGAPROMPT v2 — AtlasPMO
## Plataforma personal de análisis de cronogramas P6 / MS Project — Tier 1
### Grok 4.7 en Grok Build · modo autónomo multiagente · auto-aprobación · QA/QC estricto por etapa

> **Para Nicolás — cómo iniciar**
> 1. En la raíz de tu clon local del repositorio:
>    ```
>    git fetch origin
>    git checkout -b v2 origin/claude/beautiful-goodall-m0q2zj
>    ```
>    Esa rama contiene todo lo de `fase-5` más este documento.
> 2. Desmonta o desconecta la ubicación de tus cronogramas reales y no definas `ATLASPMO_GOLDEN_DIR` en esa terminal (sección 14).
> 3. Abre Grok Build (`grok`) en la raíz del repositorio, con tu `permission_mode = "always-approve"` (ADR-003). No uses plan mode.
> 4. Escribe: `Lee docs/MEGAPROMPT_v2.md completo y ejecuta la sección 15 (Arranque) en modo autónomo.`
> 5. Para retomar una sesión cortada: `Lee docs/MEGAPROMPT_v2.md y docs/ESTADO.md y continúa desde la siguiente tarea pendiente.`
> 6. Grok sube la rama `v2` al cerrar cada etapa aprobada por QA. Los veredictos quedan en `docs/qa/E<n>/VEREDICTO.md`.

> **Instrucción para Grok:** lee este documento completo y ejecútalo en **modo autónomo** (sección 0.1), **multiagente** (sección 9) y con **QA/QC estricto en cada etapa** (sección 8). La sesión corre con **auto-aprobación**: nadie revisa tus comandos antes de que se ejecuten, así que las reglas de la sección 14 son límites duros. Tu trabajo es cerrar las brechas de la v1 (sección 10) por etapas E0 a E6, sin preguntar. Una etapa se cierra solo con veredicto **APROBADO** de QA. Te detienes solo en los casos de la sección 0.3.

---

## 0. Tu rol y cómo trabajamos

- Eres **Grok 4.7 operando en Grok Build** como **ingeniero líder y orquestador**. La sesión principal planifica, define contratos, delega, integra y verifica. **No te autoapruebas:** el cierre de una etapa lo decide el veredicto de `qa-revisor`, apoyado en el gate automático.
- El usuario es **Nicolás**, Líder de Planificación, experto en Primavera P6, EVM y Power BI. No está disponible durante la ejecución: revisa después, sobre lo entregado. Escribe tus reportes para él como para un par técnico: concisos, en español, con evidencia, sin relleno.
- Idioma: comunicación, documentación, UI y reportes en **español**; identificadores, docstrings y comentarios de código en **inglés**.
- Formato regional de UI y reportes: es-CL (coma decimal, punto de miles, fechas dd-mm-aaaa), configurable.
- **Mantén la honestidad de la v1.** El `ESTADO.md` de la v1 decía con precisión qué no se midió y qué no se hizo. Sigue así: "no medido" o "no implementado" es aceptable; afirmar sin evidencia es un hallazgo crítico.

### 0.1 Modo autónomo

- **No preguntes.** No presentes preguntas bloqueantes ni esperes aprobación de planes o etapas.
- **Decide y registra.** Ante una ambigüedad, aplica 0.2 o, si no está cubierta, la opción más conservadora y reversible. Regístrala como ADR o supuesto en `docs/DECISIONES.md`, con `[VALIDAR]` si Nicolás debe confirmarla.
- **P6 y XER: no inventes.** Busca evidencia (fixtures, documentación oficial). Sin evidencia, implementa la interpretación más conservadora, regístrala `[VALIDAR]` y como aproximación en `ModuleResult.approximations` cuando afecte resultados.
- **Las validaciones manuales nunca te detienen:** van a `docs/VALIDACIONES_PENDIENTES.md`.
- **Memoria de trabajo:** `docs/ESTADO.md` siempre al día (hecho, en curso, siguiente, bloqueado, ciclo de QA actual), para que una sesión nueva retome sin perder nada.

### 0.2 Decisiones por defecto

| Tema | Decisión por defecto |
|---|---|
| Versión de P6 / XER | La que muestren los fixtures. Sin fixtures reales: XER de P6 moderna (v8 en adelante), como supuesto `[VALIDAR]` |
| Horas por día | Las del calendario de cada actividad. Si faltan: 8 h, registrado como aproximación |
| Base de seriales de fecha en `clndr_data` | La que confirmen los fixtures; sin evidencia, sistema Excel 1900, como `[VALIDAR]` |
| Poblaciones DCMA | Excluir completadas, LOE y WBS summary; hitos fuera de las métricas de duración. Configurable por perfil |
| Restricciones duras (DCMA 5) | `CS_MSO, CS_MEO, CS_MANDSTART, CS_MANDFIN` (configurable) |
| Criterio de crítico | Holgura total ≤ 0, con longest path disponible y seleccionable |
| Hitos contractuales (protección M3) | Lista vacía por defecto; configurable por código de actividad, UDF o lista. Los demás hitos **no** se protegen solo por ser hitos |
| Java / MPXJ ausentes | Extra `[mpp]` opcional; sus tests se omiten con motivo listado en `docs/qa/skips.toml` |
| `p6_verified` y golden reales ausentes | Tests omitidos con motivo listado en `skips.toml`; validación en `VALIDACIONES_PENDIENTES.md` |
| numba | Se usa en CPM vectorizado y Monte Carlo si hay wheel para Windows y Python 3.12. Si no la hay, se registra y se busca otra vía que cumpla la sección 11 |
| Herramienta de mutación | Una que funcione en Windows sin administrador; si ninguna sirve, `scripts/qa_sabotage.py` propio (sección 8.3, G13) |

### 0.3 Cuándo sí te detienes

Te detienes, actualizas `ESTADO.md` y reportas solo si:
1. continuar exigiría leer archivos reales (`data/real/`, `ATLASPMO_GOLDEN_DIR`) o cualquier dato confidencial;
2. continuar exigiría permisos de administrador, cambios al sistema o red en tiempo de ejecución de la app;
3. continuar exigiría una acción prohibida de la sección 14 (push a `main`, `--force`, reescribir historia publicada, borrar ramas remotas);
4. una etapa sigue **RECHAZADA** tras **3 ciclos de corrección** (sección 8.4). No se construye encima de una base rechazada;
5. terminaste E6 (reporte final, sección 16).

### Reglas de trabajo específicas para Grok 4.7

1. **Verifica antes de afirmar.** Nada se declara terminado sin ejecutar sus tests y dejar la evidencia en `docs/qa/E<n>/`.
2. **Test primero.** Para cada brecha, el test de aceptación se escribe y se ejecuta **antes** del arreglo, y debe fallar. La salida en rojo queda como evidencia. Un test que nunca estuvo en rojo no prueba el arreglo.
3. **Esfuerzo de razonamiento.** Por defecto `high`; `xhigh` para calendarios, motor CPM, redundancia y Monte Carlo, si el harness lo permite. Si no, anótalo y sigue.
4. **Gestión de contexto.** Mantén la sesión principal bajo unos 200K tokens de entrada (sobre ese umbral la tarifa sube para toda la solicitud). Delega lecturas masivas, compacta al cerrar cada entrega después de actualizar `ESTADO.md`.
5. **Git.** Commits pequeños y atómicos, uno por entrega o corrección, con mensaje convencional que cite los IDs de brecha (p.ej. `fix(engine): B-08 restricciones obligatorias`). La v1 hizo un commit por fase: no se repite.
6. **Trata el repositorio como público.** Nada confidencial se commitea jamás.

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
│   ├── MEGAPROMPT_v2.md             (este documento)
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

### 8.1 Estándares de código

- **Cobertura** (pytest-cov con `--cov-branch`): ≥ 90 % de líneas y ≥ 85 % de ramas en `model`, `calendars`, `engine` y `analysis/logic`; ≥ 80 % de líneas en el resto.
- `ruff check`, `ruff format --check` y `mypy` sin errores. mypy estricto en `model`, `calendars`, `engine` y `analysis/logic`.
- Reglas de ruff, como mínimo: `E, F, I, UP, B, BLE, S110, E722, SIM, PT, RET, PL` (ajustadas por ADR si alguna choca con el estilo). Esto prohíbe por máquina `except: pass` y capturas genéricas silenciosas.
- `uv run pytest` **funciona tal cual**: configura `pythonpath` en `pyproject.toml`. En el equipo de Nicolás se acepta `uv run python -m pytest` por el `os error 5` (ADR-004), y el gate prueba ambos cuando el entorno lo permite.
- Benchmarks con `pytest-benchmark` sobre los generadores de escala (sección 11).
- La lógica de negocio nunca vive en la UI. Errores en español y accionables; log local estructurado.

### 8.2 Principios QA/QC

1. **Separación de funciones.** Quien implementa no escribe su oráculo, no edita esperados ni umbrales y no aprueba su entrega.
2. **Rechazo por defecto.** QA parte de RECHAZADO; la entrega debe demostrar que cumple, con evidencia.
3. **Evidencia o no existe.** Toda afirmación de estado apunta a un archivo en `docs/qa/E<n>/` (salida de comandos, gate.json, informe).
4. **Gate automático primero, revisión después.** QA no revisa una entrega cuyo gate esté en rojo.
5. **Sin regresión.** Un test, un umbral o un benchmark que pasó no se elimina ni se relaja sin ADR firmado por `qa-revisor`. El gate compara contra la etapa anterior.
6. **Severidad sin negociación** (8.5). Un hallazgo crítico o importante abierto impide el cierre.

### 8.3 Gate automático — `scripts/qa_gate.py`

Comando: `uv run python scripts/qa_gate.py --etapa E<n>`. Escribe `docs/qa/E<n>/gate.json` y `gate.md`, y sale con código ≠ 0 si falla cualquier control. El script tiene sus propios tests: cada control se prueba con un caso que debe pasar y uno que debe fallar.

| ID | Control | Falla si |
|---|---|---|
| G1 | Lint y formato | `ruff check` o `ruff format --check` reportan algo |
| G2 | Tipos | `mypy` reporta errores |
| G3 | Suite completa | cualquier test falla o hay errores de colección (con `uv run pytest` y con `uv run python -m pytest`) |
| G4 | Cobertura | se incumple 8.1 en cualquier paquete |
| G5 | Propiedades | falta alguno de los invariantes a–e de la sección 7, o corre con menos de 500 ejemplos en el perfil `qa` |
| G6 | Rendimiento | un criterio de la sección 11 medible en la etapa supera su meta con el generador de escala; se registra el equipo (CPU, RAM, SO) |
| G7 | Omisiones | un `skip`, `skipif` o `xfail` no figura en `docs/qa/skips.toml` con motivo, o su motivo no es uno de los aceptados (dependencia opcional ausente, fixture pendiente de Nicolás, plataforma) |
| G8 | Privacidad y red | `.xer`, `.mpp` o XML de cronograma fuera de `tests/fixtures/`; algo bajo `data/real/`; `.env`; rutas absolutas a perfiles de usuario o nombres de usuario del equipo en archivos versionados (el patrón vive solo en `qa_gate.py` y sus tests, excluidos de ese control); un `ERMHDR` de fixture con valores fuera de la lista anónima; imports de red en `src/` (`socket`, `requests`, `urllib.request`, `http.client`, `httpx`, `aiohttp`); Streamlit sin `localhost` o con estadísticas activas |
| G9 | Campos XER | una tabla o campo XER literal usado en `src/` no aparece en `docs/XER_SPEC.md` |
| G10 | Trazabilidad | un requisito R-xxx de la etapa en `docs/qa/TRAZABILIDAD.md` no tiene un test existente y en verde |
| G11 | Rutas protegidas | cambiaron esperados, oráculos, `skips.toml`, umbrales o `qa_gate.py` sin un ADR que lo justifique, citado en el commit |
| G12 | Regresión | bajó la cantidad de tests, la cobertura cayó más de 0,5 puntos o un benchmark empeoró más de 20 % respecto de la etapa anterior |
| G13 | Mutación | en los módulos tocados por la etapa, el kill score es menor que 85 % en `engine`, `calendars` y `analysis/logic`, o menor que 70 % en el resto |

### 8.4 Controles QC por etapa (secuencia obligatoria)

Cada etapa E<n> pasa por estos seis controles, en orden. Ninguno se salta.

| QC | Control | Responsable | Sale con |
|---|---|---|---|
| QC-1 | **Contrato y trazabilidad.** Cada brecha de la etapa tiene requisitos R-xxx, criterio de aceptación ejecutable, test planificado y fuente del oráculo. Antes de escribir código | `qa-spec` | `docs/qa/E<n>/QC1_contrato.md`, aprobado |
| QC-2 | **Oráculo independiente.** Casos y esperados escritos por `fixtures` y recalculados por `qa-oraculo` por otro método (sección 7, punto 3). Discrepancias resueltas con evidencia | `fixtures` + `qa-oraculo` | esperados con doble firma |
| QC-3 | **Implementación con test primero.** Los tests de la etapa en rojo antes del arreglo (evidencia guardada); el agente que implementa trabaja en su worktree y entrega con su subconjunto del gate en verde | agentes que implementan | diff + evidencia rojo→verde |
| QC-4 | **Revisión adversarial,** en paralelo: revisión de código contra la spec, mutación dirigida y auditoría de privacidad | `qa-revisor`, `qa-sabotaje`, `qa-privacidad` | `docs/qa/E<n>/hallazgos.md` |
| QC-5 | **Integración.** El orquestador integra, corre el gate completo sobre la rama integrada y lo compara con la etapa anterior (G12) | orquestador | `gate.json` en verde |
| QC-6 | **Veredicto.** `qa-revisor` revisa el gate, los hallazgos y la evidencia, y emite APROBADO o RECHAZADO | `qa-revisor` | `docs/qa/E<n>/VEREDICTO.md` |

**Regla de cierre:** APROBADO exige gate en verde, 0 hallazgos críticos y 0 importantes abiertos. Los menores quedan registrados con su decisión.

**Ciclo de corrección:** un RECHAZADO devuelve a QC-3 con la lista de hallazgos. Cada ciclo se numera en `ESTADO.md` y en el veredicto. Tras el tercer RECHAZADO consecutivo de la misma etapa, te detienes (0.3, punto 4).

**Control técnico de solo lectura:** `qa-spec`, `qa-revisor` y `qa-privacidad` no editan archivos. Al terminar cada uno, el orquestador verifica con `git status --porcelain` que su worktree quedó limpio. Si no, descarta los cambios y registra un hallazgo de proceso. `qa-sabotaje` sí modifica código, pero solo en un worktree desechable que nunca se integra y que se elimina al terminar.

### 8.5 Severidad

| Severidad | Incluye | Efecto |
|---|---|---|
| Crítico | resultado numérico incorrecto; pérdida o corrupción de datos; XER escrito con cambios fuera de `TASKPRED`; violación de privacidad; caída con una entrada válida; un criterio de la sección 11 incumplido; afirmar algo sin evidencia | bloquea el cierre |
| Importante | desviación de la spec; aproximación silenciosa; test que no prueba lo que dice; caso borde de la sección 7 sin cubrir; campo XER sin evidencia | bloquea el cierre |
| Menor | estilo, nombres, documentación incompleta que no cambia resultados | se registra |

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
- **Cierre de etapa:** con APROBADO, actualizas `ESTADO.md`, haces commit y push de `v2` (sección 9.5) y sigues con la etapa siguiente.

### 9.3 Brief de delegación (obligatorio en cada `spawn_subagent`)

```
ETAPA / BRECHAS: E<n> · B-xx, B-yy
OBJETIVO: <qué debe quedar funcionando>
ARCHIVOS QUE POSEES: <rutas>          NO TOCAR: <rutas; siempre incluye tests/fixtures/**/expected*, tests/oracle/**, docs/qa/skips.toml, scripts/qa_gate.py salvo que seas su dueño>
CONTRATO: <interfaces/firmas que debes cumplir o consumir>
REQUISITOS: <R-xxx de docs/qa/TRAZABILIDAD.md>
ACEPTACIÓN: <tests que deben pasar + comando exacto> · TEST PRIMERO: guarda la salida en rojo antes del arreglo
ORÁCULO: <de dónde salen los esperados; nunca de tu propio código>
CONTEXTO: <secciones de docs/MEGAPROMPT_v2.md y docs/XER_SPEC.md a leer>
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

Actualiza los 9 agentes existentes a v2 y crea los 4 nuevos de QA (13 en total). Las descripciones van cortas y el detalle en el cuerpo. Todos los cuerpos terminan con: *"Sesión con auto-aprobación: respeta la sección 14 de docs/MEGAPROMPT_v2.md. Nunca leas data/real ni ATLASPMO_GOLDEN_DIR por ningún medio. Entrega tu informe en docs/qa/E<n>/<tu-nombre>.md con comandos y resultados."*

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
3. Si es RECHAZADO: correcciones y nuevo ciclo (máximo 3).
4. Si es APROBADO:
   - actualiza `ESTADO.md`, `DECISIONES.md` y `VALIDACIONES_PENDIENTES.md`;
   - corre G8 por última vez;
   - haz `git push -u origin v2`;
   - continúa con la etapa siguiente sin esperar.

**Rama:** todo el trabajo de la v2 va en `v2`, creada desde `origin/claude/beautiful-goodall-m0q2zj`. Nunca se mergea a `main`: eso lo hace Nicolás después de revisar.

---

## 10. Brechas de la v1 y etapas de la v2

### 10.1 Brechas encontradas en la revisión de `fase-5` (`b131428`)

Revisión independiente del 2026-10-20. Ejecuté la suite, lint y tipos, leí el código del motor, la redundancia, la limpieza, la calidad y la UI, y medí rendimiento con redes sintéticas. La evidencia de cada brecha es reproducible. Cada una se convierte en requisitos R-xxx en QC-1.

| ID | Sev. | Brecha | Evidencia | Aceptación |
|---|---|---|---|---|
| B-01 | Crítico | La UI no es usable: solo muestra un `multiselect`. No carga archivos, no ejecuta, no muestra resultados ni exporta | `src/atlaspmo/ui/app.py` (25 líneas) | Test e2e con `AppTest`: cargar un sintético → resumen y validación → elegir módulos → configurar con perfil → ejecutar con progreso → pestañas de resultados → exportar Excel, PDF, Parquet y manifiesto; más el visor Gantt y el modo lote |
| B-02 | Crítico | La detección de redundancia no escala: rearma el grafo y lo ordena por cada vínculo (O(E·(V+E))) | 500 act.: 1,9 s; 2.000 act.: 33,7 s; proyección a 30k > 2 h (meta < 3 min) | Benchmark de 30k realista < 3 min incluida la confirmación; algoritmo por rango topológico y agrupado por origen (sección 6, M3) |
| B-03 | Crítico | La bisección une subconjuntos confirmados por separado sin validarlos juntos, y el cleaner escribe el XER aunque `dates_unchanged = 0` | `redundant.py::_confirm` (ramas `kept.extend`); `clean.py::clean_document` | Test con dos vínculos mutuamente redundantes y uno no confirmable en el mismo lote: el conjunto final da delta cero. Si el delta del limpio no es cero, no se escribe el archivo |
| B-04 | Importante | Protecciones incompletas: no se verifican los extremos abiertos a nivel de evento; se protegen **todos** los hitos y no solo los contractuales; no hay listas de usuario | `redundant.py::_protected` | Tests positivo y negativo por regla de protección; hitos contractuales por código, UDF o lista |
| B-05 | Crítico | La detección de ciclos es recursiva y se cae con cadenas largas | `RecursionError` en `io/validate.py::_cycles` con 30k act. en serie | Validación y CPM corren sobre una cadena de 60k en serie sin error |
| B-06 | Crítico | El reloj laboral recorre día por día, con un tope fijo de 3.660 días | `CalendarLimitError` con 5k act. y ~15 años; no hay índice O(log n) | Índice acumulado con horizonte dinámico; proyecto de 20 años sin error; microbenchmarks de `add_work` y `work_between` independientes del largo del intervalo |
| B-07 | Crítico | Monte Carlo y tornado corren un CPM completo y reconstruyen el cronograma en cada iteración o actividad; no hay numba | CPM de 30k: 8,2 s → MC de 1.000 iteraciones ≈ 2,3 h; tornado de 30k en días | MC 30k × 1.000 < 5 min; tornado recalcula solo el cono afectado; invariante e) intacta |
| B-08 | Crítico | `CS_MANDSTART` y `CS_MANDFIN` se tratan como "start on": no imponen su fecha sobre la lógica | `CS_MANDSTART` al lunes 08:00 tras una predecesora: ES quedó el martes 08:00 | La fecha obligatoria se impone en ambos pases y la violación de lógica se reporta; caso para `p6_verified` |
| B-09 | Importante | No existe la opción de longest path; crítico solo por holgura ≤ X | `engine/options.py` | Longest path seleccionable y comparado con holgura ≤ X en M2 |
| B-10 | Crítico | CPLI mal definido: el largo de ruta es la suma de duraciones remanentes de la ruta 1 y la holgura es la guardada de la última actividad, no la del término objetivo | `quality/check.py::_cpli` | Definición de la sección 6 (DCMA 13) con esperados de doble firma, incluidos un caso con SS solapado y uno con feriado |
| B-11 | Importante | BEI: el numerador cuenta solo las completadas dentro de las vencidas | `quality/check.py::_baseline_ratio` | Numerador = todas las completadas (sección 6, DCMA 14); caso con una completada antes de tiempo |
| B-12 | Importante | M2 incompleto: no hay trazado de cadena driving hacia un hito, ni multiple float paths propios, ni verificación de continuidad; las bandas de holgura están fijas en código | `analysis/paths/` | Cada función con tests y documentación del algoritmo; bandas configurables por perfil |
| B-13 | Importante | M6 incompleto: no hay distribución temporal por periodo, histogramas, sobreasignación ni curvas S; `fact_timephased` se escribe vacío; el PV es lineal | `analysis/resources/evm.py`; ADR-007 y ADR-008 | Funciones de la sección 6 (M6) con esperados; `fact_timephased` poblado; supuestos como aproximación |
| B-14 | Importante | Datos de prueba insuficientes: `gen_synthetic.py` sigue escribiendo la tabla inventada `SYNTH`; no hay generador de escala; 8 casos no cubren la lista de la sección 7; los esperados los generó el mismo autor del motor | `tests/fixtures/synthetic/minimal.xer`; `scripts/build_cases.py` | Generador con tablas reales, `gen_scale.py`, todos los casos borde de la sección 7 y esperados con doble firma |
| B-15 | Importante | No hay tests de propiedades: `hypothesis` no está en las dependencias; los invariantes a–e no existen | `pyproject.toml` | G5 en verde |
| B-16 | Crítico | No hay medición de rendimiento: ningún criterio de la sección 11 está medido salvo la lectura de 30k, y esa prueba usa un XER de 2 columnas | `tests/test_phase1.py::test_read_30k...`; `ESTADO.md`, fase 5 | G6 en verde con `gen_scale.py` |
| B-17 | Importante | `uv run pytest` falla en la colección (`No module named 'scripts'`) en cualquier equipo, no solo por el `os error 5` | ejecución en Linux | `pythonpath` configurado; G3 con ambos comandos |
| B-18 | Menor | 14 archivos sin `ruff format` | `ruff format --check` | G1 |
| B-19 | Importante | El repositorio sigue apuntando a `docs/MEGAPROMPT.md`, que ya no existe; `AGENTS.md` y los agentes no reflejan ni la v1 ni la v2 | `AGENTS.md`, `.grok/agents/*.md` | Referencias a `MEGAPROMPT_v2.md`; los 13 agentes de 9.4 |
| B-20 | Importante | Un XER con bytes indefinidos en cp1252 (p.ej. `0x81`) se rechaza entero | `read_xer_bytes` → "no decodifica como cp1252" | Se lee, se registra la aproximación y el round-trip sigue siendo byte a byte |
| B-21 | Menor | Un hito de inicio que sigue a una FS que termina a las 16:00 queda en el mismo instante (16:00) y no en el inicio laboral siguiente | caso de 3 actividades en un calendario de 08:00 a 16:00 | Regla de la sección 6 (M0), marcada `[VALIDAR]` con caso para `p6_verified` |
| B-22 | Importante | Proceso: un commit por fase, sin evidencia de test primero, y `fase-1` se creó antes del gate de la Fase 0 | historial de `fase-0` a `fase-5` | Reglas de trabajo 2 y 5 de la sección 0; G11 y G12 |
| B-23 | Importante | Ruta absoluta con el usuario de Windows de Nicolás en código publicado (`reports/export.py::_git_executable`) y en `ESTADO.md`; detectada por G8 el 2026-10-21 | `git grep` sobre `fase-1` a `fase-5` | **Corregido en `claude/beautiful-goodall-m0q2zj`**: el código usa `git` del PATH o la variable `ATLASPMO_GIT`. Queda en la historia de `fase-1` a `fase-5`; limpiarla exige reescribir historia publicada y lo decide Nicolás (sección 14) |

Lo que la v1 hizo bien y se conserva: el lector y escritor XER con reposición de bytes; la estructura de contrato, registro y módulos; la honestidad del `ESTADO.md` y los ADR; la semilla en el manifiesto; el hook de privacidad; los imports sin red; y el PBIP con TMDL basado en la documentación vigente.

### 10.2 Etapas

| Etapa | Alcance | Criterios propios (además del gate G1–G13 en verde) |
|---|---|---|
| **E0 · Base QA** | B-17, B-18, B-19, B-22 (proceso). `qa_gate.py` con G1–G13 y sus tests; dependencias `hypothesis`, `pytest-benchmark`, `pytest-cov` y la herramienta de mutación; reglas de ruff de 8.1; `docs/qa/` con `TRAZABILIDAD.md` de **toda** la spec (cada requisito de las secciones 2, 5, 6, 7 y 11 con su R-xxx); `skips.toml`; hook pre-push; los 13 agentes; `AGENTS.md` v2; `gen_scale.py` | El gate corre y reporta con veracidad. **Excepción solo para E0:** G4, G5, G6, G10 y G13 pueden fallar sobre el código heredado; ese resultado queda como **línea base** en `docs/qa/E0/gate.json` y no bloquea el cierre de E0. G1, G2, G3, G7, G8, G9 y G11 sí deben quedar en verde |
| **E1 · Núcleo robusto** | B-05, B-06, B-08, B-09, B-20, B-21; parte de B-14 (calendarios con feriados, medias jornadas, 24 h y 7 días; restricciones; avance; hitos); invariante a) | Cadena de 60k en serie sin error; proyecto de 20 años; lectura de un XER realista de 30k < 15 s |
| **E2 · Lógica y limpieza** | B-02, B-03, B-04; casos de redundancia de la sección 7; invariantes b), c) y d) | Redundancia 30k < 3 min; el XER limpio difiere solo en filas de `TASKPRED` y el delta es cero, o no se escribe |
| **E3 · Calidad y rutas** | B-10, B-11, B-12; DCMA 12 con el motor corregido; GAO | DCMA y chequeos de calidad sobre 30k < 10 s; todas las métricas contra esperados con doble firma |
| **E4 · Riesgo y recursos** | B-07, B-13; invariante e) | Monte Carlo 30k × 1.000 < 5 min; EVM y curvas S contra esperados con doble firma |
| **E5 · UI y reportes** | B-01; exportaciones con manifiesto; lote y biblioteca desde la UI | e2e completo en verde; la app solo escucha en localhost (test) |
| **E6 · Endurecimiento** | Regresión total; auditoría integral de `qa-revisor`, `qa-privacidad` y `qa-sabotaje` sobre todo el repo; `MANUAL_USUARIO.md` actualizado; instalación en un paso | Todos los criterios automatizables de la sección 11 en verde y evidenciados; G13 sobre todo `src/`; checklist final de `VALIDACIONES_PENDIENTES.md` |

Las validaciones manuales de cada etapa (P6, golden reales, Power BI Desktop, `.mpp` con Java) van a `VALIDACIONES_PENDIENTES.md` con instrucciones exactas y nunca detienen la ejecución.

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

---

## 13. Contenido de `AGENTS.md`

Ya existe: reemplázalo por este contenido en E0.

```markdown
# AtlasPMO — plataforma personal de análisis de cronogramas (P6 / MS Project)

Especificación: docs/MEGAPROMPT_v2.md · Estado: docs/ESTADO.md · Decisiones: docs/DECISIONES.md · QA: docs/qa/ · Pendientes de Nicolás: docs/VALIDACIONES_PENDIENTES.md

## Reglas críticas
- Sesiones con auto-aprobación: los límites duros de la sección 14 del megaprompt son absolutos.
- Nunca leer data/real/ ni ATLASPMO_GOLDEN_DIR, por ningún medio (incluido el shell). El repositorio se trata como público.
- App 100 % local: sin red, sin telemetría.
- XER: cp1252, CRLF, tablas no modificadas idénticas byte a byte. Solo campos con evidencia en docs/XER_SPEC.md.
- Sin aproximaciones silenciosas: registrarlas en ModuleResult.approximations.
- Redundancia = camino alternativo ≥ lag en el grafo de eventos + confirmación conjunta con delta cero. Nunca "no es driver".
- Test primero; nada se declara terminado sin evidencia en docs/qa/E<n>/.
- Quien implementa no edita oráculos, esperados, umbrales ni el gate. Nadie se autoaprueba.
- Una etapa se cierra solo con VEREDICTO APROBADO de qa-revisor y gate en verde.
- Código e identificadores en inglés; UI, docs y mensajes al usuario en español (es-CL).
- Rama v2; nunca push a main ni --force.

## Comandos
- Gate: uv run python scripts/qa_gate.py --etapa E<n>
- Tests: uv run pytest  (en el equipo de Nicolás: uv run python -m pytest)
- Lint, formato y tipos: uv run ruff check . && uv run ruff format --check . && uv run mypy src
- App: atlaspmo.bat (uv run python -m streamlit run src/atlaspmo/ui/app.py)
- Conformidad (solo Nicolás, en su equipo): uv run python scripts/run_conformance.py
```

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
   - `git fetch` y `git push` de la rama `v2` a `origin`.

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
- Hooks pre-commit y pre-push con G8. El pre-push además rechaza cualquier destino distinto de `origin/v2`.
- **Recomendaciones para Nicolás** (escríbelas con el texto exacto en `VALIDACIONES_PENDIENTES.md`; no las apliques tú):
  - una regla de denegación con la ruta absoluta de su carpeta golden en `~/.grok/config.toml`;
  - mantener los golden en una unidad o contenedor cifrado desmontado durante las sesiones de Grok.

### 14.3 Otros harnesses

Si Nicolás usa Grok 4.7 desde Cursor o GitHub Copilot, `AGENTS.md` y esta sección siguen aplicando. Los roles de 9.4 se ejecutan en secuencia dentro de la sesión, con el mismo brief y los mismos controles QC. La separación de funciones se mantiene: el rol QA nunca revisa un cambio que escribió el mismo turno sin pasar antes por el gate.

---

## 15. Arranque

**Estado de partida.** La rama `v2` nace de `origin/claude/beautiful-goodall-m0q2zj`, que contiene `fase-5` (`b131428`) más este documento. `docs/MEGAPROMPT.md` y `docs/MEGAPROMPT_v1.md` ya no existen: este documento los reemplaza.

1. Verifica que estás en la rama `v2` y que el árbol está limpio. Si no existe, créala: `git checkout -b v2 origin/claude/beautiful-goodall-m0q2zj`.
2. Lee este documento completo y `docs/ESTADO.md`. Si `ESTADO.md` indica una etapa v2 en curso, retómala desde el control QC pendiente.
3. Registra en `ESTADO.md` el inicio de la v2: base `b131428`, brechas B-01 a B-23, etapas E0 a E6.
4. Ejecuta E0 a E6 con el ciclo de 9.5, sin pausas, cada una con QC-1 a QC-6.
5. Al terminar E6, escribe el reporte final (sección 16) y detente.

---

## 16. Reporte final

Escríbelo en `docs/ESTADO.md` y muéstralo en la sesión. Incluye:
- **Por etapa:**
  - brechas cerradas;
  - veredicto y número de ciclos de QA;
  - gate (G1–G13: estado y valores);
  - último commit.
- **Brechas:** tabla B-01 a B-23 con estado final (cerrada / abierta) y evidencia.
- **Pruebas:**
  - suite completa con su comando y resultado;
  - cobertura por paquete;
  - kill score de mutación por paquete;
  - benchmarks contra la sección 11, con los datos del equipo.
- **Hallazgos QA:** abiertos por severidad (debería haber 0 críticos y 0 importantes) y menores registrados.
- **Supuestos `[VALIDAR]`:** lista con enlace a su ADR.
- **Para Nicolás:** checklist priorizado de `VALIDACIONES_PENDIENTES.md`.
- **Para la v3 del megaprompt:** qué fue ambiguo, contradictorio o insuficiente en este documento, con propuesta de redacción.
