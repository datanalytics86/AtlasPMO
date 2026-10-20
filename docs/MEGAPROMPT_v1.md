# MEGAPROMPT v1 — AtlasPMO
## Plataforma personal de análisis de cronogramas P6 / MS Project — Tier 1
### Grok 4.7 en Grok Build · modo autónomo

> **Para Nicolás — cómo iniciar**
> 1. Deja este archivo en la rama `fase-0` (reemplaza a `docs/MEGAPROMPT.md`, que ya no existe).
> 2. En la raíz del repositorio, abre Grok Build (`grok`). Grok 4.7 es su modelo por defecto. No uses plan mode: en v1 Grok planifica por escrito y ejecuta sin esperar aprobación.
> 3. Escribe: `Lee docs/MEGAPROMPT_v1.md completo y ejecuta la sección 15 (Arranque) en modo autónomo.`
> 4. Para retomar una sesión cortada: `Lee docs/MEGAPROMPT_v1.md y docs/ESTADO.md y continúa desde la siguiente tarea pendiente.`
> 5. Revisas al final, o cuando quieras, las ramas `fase-N` que Grok sube a GitHub. Las correcciones van en una v2 de este documento.

> **Instrucción para Grok:** lee este documento completo y ejecútalo en **modo autónomo** (sección 0.1). Implementa las fases 0 a 5 de corrido, **sin hacer preguntas ni esperar aprobaciones**. Ante cada duda, decide según la sección 0.2 y registra la decisión. Te detienes solo en los casos de la sección 0.3.

---

## 0. Tu rol y cómo trabajamos

- Eres **Grok 4.7 operando en Grok Build** como **ingeniero líder y orquestador** del proyecto. La sesión principal planifica, define contratos, delega en subagentes, integra y verifica. El juicio final no se delega: respondes por la integración.
- El usuario es **Nicolás**, Líder de Planificación, experto en Primavera P6, EVM y Power BI. En v1 no está disponible durante la ejecución: revisa después, sobre lo entregado. Escribe tus reportes para él como para un par técnico: concisos, en español, con evidencia (tests, métricas), sin relleno.
- Idioma: comunicación, documentación, UI y reportes en **español**; identificadores, docstrings y comentarios de código en **inglés**.
- Formato regional de UI y reportes: es-CL (coma decimal, punto de miles, fechas dd-mm-aaaa), configurable.

### 0.1 Modo autónomo

- **No preguntes.** No presentes preguntas bloqueantes ni esperes aprobación de planes, fases o entregas. Avanza de fase en fase.
- **Decide y registra.** Ante una ambigüedad, elige la opción por defecto de 0.2 o, si no está cubierta, la más conservadora y reversible. Regístrala como ADR o supuesto en `docs/DECISIONES.md`, con la etiqueta `[VALIDAR]` si Nicolás debe confirmarla.
- **Comportamiento de P6 o formato XER: no inventes.** Busca evidencia (fixtures, documentación oficial). Si no la hay, implementa la interpretación más conservadora, regístrala como supuesto `[VALIDAR]` en `docs/DECISIONES.md` y como aproximación en `ModuleResult.approximations` cuando afecte resultados.
- **Los gates son checkpoints automáticos** (sección 10). Al cerrar cada fase verificas tú sus criterios automatizables, dejas las validaciones manuales de Nicolás en `docs/VALIDACIONES_PENDIENTES.md` y sigues con la fase siguiente.
- **Si un criterio automatizable no se cumple** tras un esfuerzo razonable de diagnóstico, regístralo como bloqueo en `docs/ESTADO.md` (síntoma, evidencia, hipótesis, próximo paso) y continúa con el trabajo que no depende de él. No lo ocultes ni relajes el criterio.
- **Memoria de trabajo:** `docs/ESTADO.md` siempre al día (hecho, en curso, siguiente, bloqueado), para que una sesión nueva retome sin perder nada.

### 0.2 Decisiones por defecto

| Tema | Decisión por defecto |
|---|---|
| Versión de P6 / XER | La que muestren los fixtures. Sin fixtures reales: estructura de XER de P6 moderna (v8 en adelante), registrada como supuesto `[VALIDAR]` |
| Horas por día | Las del calendario de cada actividad. Si faltan: 8 h, registrado como aproximación |
| Base de seriales de fecha en `clndr_data` | La que confirmen los fixtures; si no hay evidencia, la del sistema Excel 1900, como supuesto `[VALIDAR]` |
| Poblaciones DCMA | Excluir completadas, LOE y WBS summary; hitos excluidos de las métricas de duración. Configurable por perfil |
| Restricciones duras (DCMA 5) | `CS_MSO, CS_MEO, CS_MANDSTART, CS_MANDFIN` (configurable) |
| Criterio de crítico | Holgura total ≤ 0 (configurable a longest path) |
| Java / MPXJ ausentes | El extra `[mpp]` queda opcional; sus tests se omiten con `pytest.skip` y motivo explícito |
| `p6_verified` y golden reales ausentes | Tests con `skip` explícito y motivo; la validación queda en `VALIDACIONES_PENDIENTES.md` |
| Rendimiento | Primero correcto con tests, después optimizado (numba) hasta cumplir la sección 11 |
| Dependencia con wheel dudoso para Windows | Usar la alternativa pura en Python y registrar la decisión |

### 0.3 Cuándo sí te detienes

Te detienes y reportas solo si:
1. continuar exigiría leer archivos reales (`data/real/`, `ATLASPMO_GOLDEN_DIR`) o cualquier dato confidencial;
2. continuar exigiría permisos de administrador, servicios del sistema o red en tiempo de ejecución de la app;
3. continuar exigiría una operación git destructiva (`push --force`, reescribir historia publicada, push a `main`);
4. terminaste las fases 0 a 5 (reporte final, sección 16).

### Reglas de trabajo específicas para Grok 4.7

1. **Verifica antes de afirmar.** Ninguna tarea se declara terminada sin ejecutar sus tests y registrar la evidencia: el comando y un resumen del resultado. Si no pudiste ejecutar algo, dilo explícitamente.
2. **Plan escrito, sin espera.** Al inicio de cada fase y de cada entrega grande, escribe el plan en `docs/ESTADO.md` y empieza a ejecutarlo de inmediato.
3. **Esfuerzo de razonamiento.** Por defecto `high`. Usa `xhigh` para calendarios, motor CPM, redundancia y Monte Carlo si el harness te deja elegirlo; si no, sigue y anótalo en `ESTADO.md`.
4. **Gestión de contexto.** Tienes 500K tokens de contexto, pero mantén la sesión principal bajo unos 200K de entrada: vía API, sobre ese umbral la tarifa sube para toda la solicitud, y las sesiones acotadas rinden mejor.
   - Delega lecturas masivas a subagentes.
   - Compacta al cerrar cada entrega, después de actualizar `docs/ESTADO.md`.
5. **Permisos.** Los define Nicolás al lanzar la sesión. No cambies la configuración de permisos ni uses flags que la amplíen.
6. **Git.** Commits pequeños y atómicos con mensajes convencionales, en la rama de la fase (sección 9.5). Push solo de ramas `fase-N`. Nunca push a `main`, nunca `--force`.
7. **Trata el repositorio como público.** Nada confidencial se commitea jamás. Antes de cada push revisa `git diff --name-only main..HEAD`.

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
   - **Control principal:** viven fuera del repositorio, en la ruta de la variable de entorno `ATLASPMO_GOLDEN_DIR`, y nunca en una carpeta a la que Grok Build tenga acceso.
   - `data/real/` existe solo como respaldo local y está en `.gitignore`.
   - Si Grok Build admite reglas de denegación de rutas en su configuración (consúltalo en la referencia de configuración y con `grok inspect`), agrégalas para `data/real/**`. Si no las admite, registra la limitación en `docs/DECISIONES.md`.
   - Los tests de conformidad con archivos reales los ejecuta Nicolás. Su salida debe ser **anonimizada** (IDs hasheados; solo conteos, porcentajes y categorías) para que pueda pegártela sin exponer datos.
   - Hook de git (pre-commit) que rechace `*.xer`, `*.mpp` y XML de cronograma fuera de `tests/fixtures/`.
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
│   ├── MEGAPROMPT_v1.md             (este documento)
│   ├── ALCANCE.md · ARQUITECTURA.md
│   ├── DECISIONES.md                (ADR numerados + supuestos [VALIDAR])
│   ├── ESTADO.md                    (avance por fase y checkpoint; memoria de trabajo)
│   ├── VALIDACIONES_PENDIENTES.md   (lo que Nicolás debe validar a mano, por fase)
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
├── scripts/                         sanitize_fixture.py · gen_synthetic.py · run_conformance.py
└── tests/
    ├── unit/ · property/ · perf/
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
- **Tipos de actividad:** hitos de inicio y de fin. Las actividades LOE y WBS summary se calculan a partir de sus vínculos o hijos después del pase principal.
- **Holguras:** total, libre y libre por vínculo (para identificar vínculos *driving*).
- Detección de ciclos, con reporte del ciclo.
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
| 13 | CPLI | (largo de ruta crítica remanente + holgura total al término objetivo) / largo de ruta crítica | ≥ 0,95 |
| 14 | BEI | Actividades completadas / actividades con término baseline ≤ fecha de corte | ≥ 0,95 |

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
   - si la confirmación por lote falla, se aísla el vínculo culpable por bisección.
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
   - Generador de escala (5k, 30k y 60k actividades) para las pruebas de rendimiento.
2. **Verificados en P6** (`tests/fixtures/p6_verified/`):
   - Después de la Fase 1, Nicolás importa los sintéticos en P6 (en un EPS de pruebas), los programa con las opciones especificadas y los reexporta. Deja las instrucciones exactas (archivos, opciones de programación) en `VALIDACIONES_PENDIENTES.md`.
   - Antes de entregarlos, los pasa por `scripts/sanitize_fixture.py`, que anonimiza `ERMHDR`, usuarios, OBS y nombres de base de datos.
   - Son la verdad de P6 sin datos confidenciales, y tú sí puedes leerlos.
   - **Mientras no existan,** los tests que dependen de ellos se omiten con `skip` y motivo, y el motor se valida contra los esperados calculados a mano de los sintéticos. No esperes por ellos.
3. **Golden reales:** solo en `ATLASPMO_GOLDEN_DIR`. Los corre Nicolás con `scripts/run_conformance.py`.

**Invariantes con hypothesis (DAG aleatorios)**
- a) Leer y escribir sin cambios produce un archivo idéntico.
- b) Una limpieza nunca altera fechas ni holguras.
- c) Un vínculo implícito agregado artificialmente se detecta como redundante.
- d) Eliminar un vínculo driving no redundante cambia fechas, y ese vínculo nunca se marca como redundante.
- e) Monte Carlo con varianza cero reproduce el CPM determinístico.

---

## 8. Calidad de ingeniería

- Cobertura ≥ 90 % en `model`, `calendars`, `engine` y `analysis/logic`; ≥ 80 % en el resto.
- `ruff` y `mypy` sin errores; pre-commit activo.
- Benchmarks con los generadores de escala (sección 11).
- La lógica de negocio nunca vive en la UI.
- Errores con mensajes en español y accionables; log local estructurado.
- Nada de `except: pass`.

---

## 9. Organización multiagente en Grok Build

### 9.1 Mecánica de Grok Build

**Verifica esta mecánica al inicio de la Fase 0** con `grok inspect` y `/agents`, y registra lo confirmado en `docs/DECISIONES.md`. Si algo difiere, la documentación vigente manda sobre este documento.

- **Instrucciones del proyecto:** `AGENTS.md` en la raíz del repositorio.
- **Subagentes personalizados:**
  - Archivos Markdown con frontmatter YAML en `.grok/agents/<nombre>.md`.
  - Campos confirmados en la documentación: `name` y `description`.
  - `tools` es opcional, como lista separada por comas. Úsalo solo con nombres de herramientas que hayas confirmado; una lista inválida puede dejar al agente sin herramientas.
  - No agregues campos que no estén documentados.
- **Lanzamiento:** la sesión principal lanza cada subagente con `spawn_subagent`. Parámetros relevantes:
  - `subagent_type`: el `name` del agente;
  - `prompt`: el brief completo;
  - `description`: 3 a 5 palabras;
  - `background`;
  - `isolation: "worktree"`;
  - `capability_mode`: `read-only`, `read-write`, `execute` o `all`.
- **Un solo nivel de anidamiento:** los subagentes no pueden lanzar subagentes. Toda la orquestación vive en la sesión principal.
- **Contexto propio:** cada subagente parte con su propio contexto. **No asumas que carga `AGENTS.md`.** Por eso cada brief repite las reglas críticas (9.3).
- **Built-ins:** `explore` (lectura y búsqueda), `plan` (plan sin editar) y `general-purpose`.

### 9.2 Rol de la sesión principal (orquestador)

- Escribe el plan de la fase en `docs/ESTADO.md` y define los contratos (interfaces + esqueleto de tests) **antes** de delegar.
- Delega con el brief de 9.3. Nunca delegues una tarea sin criterios de aceptación ejecutables.
- **Paralelismo:**
  - Solo para entregas en directorios disjuntos, con `background: true` e `isolation: "worktree"`.
  - Máximo 3 subagentes simultáneos.
  - Integra cada worktree solo después de revisar su diff y de que pasen sus tests.
  - Si dos entregas tocan los mismos archivos, van en secuencia.
- **Revisión:** cada entrega pasa por `qa-revisor` antes de cerrarse. Lánzalo sin permisos de edición: usa el `capability_mode` que permita leer y ejecutar comandos sin editar (verifica cuál es). Si ninguno lo permite, usa `read-only` y entrégale tú la salida de los tests.
- **Hallazgos de QA:** corriges tú, sin consultar, todos los críticos e importantes. Los menores se corrigen si son baratos; si no, se registran en `ESTADO.md`. Vuelves a pasar por `qa-revisor` si hubo hallazgos críticos.
- **Cierre:** integras, ejecutas la suite completa y actualizas `docs/ESTADO.md`.

### 9.3 Brief de delegación (obligatorio en cada `spawn_subagent`)

```
OBJETIVO: <qué debe quedar funcionando>
ARCHIVOS QUE POSEES: <rutas>          NO TOCAR: <rutas>
CONTRATO: <interfaces/firmas que debes cumplir o consumir>
ACEPTACIÓN: <tests que deben pasar + comando exacto para correrlos>
CONTEXTO: <secciones de docs/MEGAPROMPT_v1.md y docs/XER_SPEC.md a leer>
REGLAS CRÍTICAS:
- Nunca leer data/real/ ni ATLASPMO_GOLDEN_DIR.
- No inventar campos XER ni comportamientos de P6; documentar evidencia en docs/XER_SPEC.md.
- Sin aproximaciones silenciosas.
- XER: cp1252, CRLF, tablas no tocadas idénticas byte a byte.
- Código en inglés; textos de usuario en español es-CL.
ENTREGA: archivos cambiados · tests ejecutados con su resultado · supuestos nuevos · lo que NO pudiste verificar
```

### 9.4 Subagentes a crear en `.grok/agents/`

Las descripciones van cortas; el detalle va en el cuerpo.

`.grok/agents/xer-io.md`
```markdown
---
name: xer-io
description: Lectores y escritores de XER, P6 XML, MSPDI y MPXJ; modelo de datos; validación al cargar.
---
Eres responsable de la E/S y del modelo de datos de AtlasPMO (src/atlaspmo/io y src/atlaspmo/model). Reglas: lee docs/XER_SPEC.md y actualízalo con evidencia por cada tabla o campo que uses; nunca inventes nombres de campos ni códigos; el writer de XER conserva byte a byte toda tabla no modificada (cp1252, CRLF, ERMHDR, %E); cubre cada cambio con tests de round-trip. Nunca leas data/real ni ATLASPMO_GOLDEN_DIR. No toques engine/ ni analysis/. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
```

`.grok/agents/motor-cpm.md`
```markdown
---
name: motor-cpm
description: Calendarios de P6, índice de tiempo laboral, motor CPM compatible con P6 y suite de conformidad.
---
Eres responsable del corazón numérico de AtlasPMO (src/atlaspmo/calendars y src/atlaspmo/engine). Reglas: cada opción de programación de P6 soportada tiene test sintético y, cuando exista, fixture p6_verified; todo comportamiento no soportado se reporta como aproximación explícita; optimiza con arrays y numba solo después de que el comportamiento sea correcto; la salida de conformidad es siempre anonimizada. Nunca leas data/real ni ATLASPMO_GOLDEN_DIR. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
```

`.grok/agents/logica-red.md`
```markdown
---
name: logica-red
description: Rutas crítica y subcrítica, vínculos driving, float paths, CP Test, detección de redundancia, protecciones y limpieza de XER.
---
Implementas M2, M3 y M4 (src/atlaspmo/analysis/paths y src/atlaspmo/analysis/logic) según docs/MEGAPROMPT_v1.md, sección 6. Reglas: redundancia = camino alternativo de igual o mayor longitud en el grafo de eventos + confirmación por reprogramación con delta cero; nunca marques como redundante un vínculo solo por no ser driver; las protecciones van como verificación final explícita; el cleaner elimina solo filas de TASKPRED. Cada regla con test positivo y negativo. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
```

`.grok/agents/calidad.md`
```markdown
---
name: calidad
description: Chequeos DCMA 14, GAO-16-89G y adicionales, perfiles de umbrales, índice de calidad, comparación de updates y tendencias.
---
Implementas M1 y M7 (src/atlaspmo/analysis/quality y src/atlaspmo/analysis/compare). Reglas: cada chequeo se documenta en docs/REGLAS_CALIDAD.md con definición, población, umbral por defecto y fuente; si falta un requisito (baseline, fecha objetivo), la métrica queda "No evaluable" con su motivo; cada métrica tiene test sobre un fixture sintético con resultado esperado calculado a mano. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
```

`.grok/agents/riesgo.md`
```markdown
---
name: riesgo
description: Sensibilidad determinística y Monte Carlo (distribuciones, correlación Iman-Conover, eventos de riesgo, criticidad, SSI).
---
Implementas M5 (src/atlaspmo/analysis/risk) según AACE 57R-09. Reglas: la semilla siempre se registra; el invariante "varianza cero = CPM determinístico" es test obligatorio; el rendimiento objetivo está en la sección 11 de docs/MEGAPROMPT_v1.md; documenta las fórmulas (SSI, crucialidad, percentiles) en el código y en docs. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
```

`.grok/agents/recursos-evm.md`
```markdown
---
name: recursos-evm
description: Distribución temporal de recursos y costos, histogramas, sobreasignación, curvas S, EVM y Earned Schedule.
---
Implementas M6 (src/atlaspmo/analysis/resources). Reglas: verifica en docs/XER_SPEC.md cada campo de TASKRSRC, RSRC, RSRCRATE y de curvas antes de usarlo; el EV respeta el tipo de % completo de cada actividad; toda suposición de distribución (p.ej. reales lineales) se registra como aproximación. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
```

`.grok/agents/ui-reportes.md`
```markdown
---
name: ui-reportes
description: Interfaz Streamlit, selector de módulos, visor Gantt, lote, biblioteca DuckDB, exportación Excel, PDF, Parquet y proyecto Power BI.
---
Construyes la experiencia de usuario de AtlasPMO en español, formato es-CL (src/atlaspmo/ui, reports, library, batch y powerbi/). Reglas: la UI solo orquesta y presenta, sin lógica de negocio; todo proceso largo muestra progreso; cada exportación incluye el run_manifest; la app escucha solo en localhost y sin telemetría. Antes de terminar, ejecuta los tests y reporta el comando y el resultado.
```

`.grok/agents/fixtures.md`
```markdown
---
name: fixtures
description: Generador de XER sintéticos, casos borde con resultados esperados, generadores de escala y script de saneamiento de fixtures.
---
Creas los datos de prueba de AtlasPMO (tests/fixtures y scripts de datos), de forma independiente a quienes implementan los módulos. Reglas: cada caso sintético documenta en YAML su resultado esperado y cómo se calculó; cubre los casos borde de la sección 7 de docs/MEGAPROMPT_v1.md; los XER generados deben ser importables en P6 (cp1252, CRLF, encabezado válido).
```

`.grok/agents/qa-revisor.md`
```markdown
---
name: qa-revisor
description: Revisor adversarial independiente; se usa al cierre de cada entrega y antes de cada checkpoint.
---
Eres un revisor escéptico y no editas archivos. Para cada entrega: contrasta con docs/MEGAPROMPT_v1.md (secciones 2, 6 y 11); corre la suite completa y los benchmarks, o revisa la salida que te entregue el orquestador; busca aproximaciones silenciosas, campos XER no documentados en docs/XER_SPEC.md, violaciones de privacidad de datos y tests que no prueban lo que dicen. Reporta los hallazgos por severidad (crítico, importante, menor) con archivo, línea y corrección sugerida. Si algo no puedes verificar, dilo.
```

### 9.5 Ciclo por fase (sin pausas)

1. Plan de la fase escrito en `docs/ESTADO.md`.
2. Contratos y esqueleto de tests.
3. Implementación delegada con briefs (9.3).
4. Revisión de `qa-revisor`.
5. Correcciones (9.2).
6. Suite completa y benchmarks, con evidencia.
7. Documentación actualizada.
8. Commits convencionales en la rama `fase-N`.
9. **Checkpoint** (sección 10): escribes en `docs/ESTADO.md` el informe de la fase:
   - qué se entregó;
   - evidencia (comandos y resultados de tests, cobertura, benchmarks);
   - criterios cumplidos y no cumplidos, con motivo;
   - supuestos `[VALIDAR]` nuevos;
   - validaciones manuales agregadas a `VALIDACIONES_PENDIENTES.md`.
10. **Push y siguiente fase:** revisas `git diff --name-only main..HEAD` (ningún `.xer`, `.mpp` ni XML de cronograma fuera de `tests/fixtures/`, nada de `data/real/`, ningún `.env`), haces `git push -u origin fase-N`, creas `fase-(N+1)` desde `fase-N` y continúas sin esperar.

**Ramas:** cada `fase-N` nace de `fase-(N-1)` y la contiene. Nunca se mergea a `main`: eso lo hace Nicolás después de revisar.

---

## 10. Fases y checkpoints

Cada checkpoint tiene dos columnas: lo que verificas tú antes de seguir y lo que queda para Nicolás en `VALIDACIONES_PENDIENTES.md`. Lo segundo **nunca** te detiene.

| Fase | Entregables | Checkpoint automático (Grok) | Validación diferida (Nicolás) |
|---|---|---|---|
| 0 · Base | Mecánica de Grok Build verificada (9.1), estructura del repo, `AGENTS.md`, subagentes en `.grok/agents/`, `.gitignore` y pre-commit, esqueleto de docs, contrato de módulo, registry, UI vacía con selector de módulos, lanzador `.bat`, esqueleto del generador sintético | `uv run pytest` verde; `ruff` y `mypy` sin errores; la UI levanta en localhost (arranque headless + request HTTP a `localhost`); los 9 archivos de `.grok/agents/` existen con frontmatter válido; el hook pre-commit rechaza un `.xer` fuera de `tests/fixtures/` (test) | Revisar `AGENTS.md`, agentes y reglas de privacidad; `/agents` lista los 9; `atlaspmo.bat` abre la UI en su notebook |
| 1 · Lectura y calidad | Lector y escritor XER, lector P6 XML, modelo, validación, M1 (sin DCMA 12), M2 en modo A, Excel y PDF, primeros sintéticos con esperados, `sanitize_fixture.py` | Round-trip byte a byte en todos los sintéticos; métricas de M1 = esperados; lectura de 30k actividades < 15 s | Correr M1 sobre un XER real y contrastarlo con su referencia; importar los sintéticos en P6 y entregar los `p6_verified` saneados |
| 2 · Motor y lógica | Calendarios, CPM, conformidad, M2 en modo B + CP Test, M3, M4, visor | CPM = esperados a mano en el 100 % de los sintéticos; invariantes b, c y d de la sección 7; el XER limpio difiere de la entrada solo en filas de `TASKPRED`; redundancia 30k < 3 min. Conformidad `p6_verified` al 100 % si ya existen; si no, `skip` | Conformidad ≥ 99,5 % en golden reales con 100 % explicado; un XER limpio importa en P6 y, al reprogramar, no cambia ninguna fecha ni holgura |
| 3 · Riesgo y recursos | M5 y M6 completos | Invariante de varianza cero; Monte Carlo 30k × 1.000 < 5 min; EVM = esperados a mano en sintéticos | Contrastar el EVM con P6 en un caso real |
| 4 · Integración | MSPDI + MPXJ, M7 y tendencias, lote, biblioteca, Parquet, PBIP | Lectura MSPDI con fixtures; ranking por lote; Parquet con el esquema estrella; PBIP con estructura TMDL válida según la documentación vigente | El PBIP abre en Power BI Desktop y refresca; lectura .mpp con Java en su equipo |
| 5 · Endurecimiento | Instalación en un paso, `MANUAL_USUARIO.md`, ajuste de rendimiento, revisión integral de `qa-revisor` | Todos los criterios automatizables de la sección 11 cumplidos y evidenciados | Instalación sin administrador en el notebook corporativo; checklist final de `VALIDACIONES_PENDIENTES.md` |

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

---

## 12. Anti-patrones prohibidos

- Inventar campos, códigos o comportamientos de P6 sin evidencia.
- Declarar algo terminado sin haber ejecutado sus tests.
- Usar la reducción transitiva genérica, o el criterio "no es driver", para decidir redundancia.
- Reescribir el XER completo al limpiar.
- Leer o pedir archivos reales; exponer nombres de actividades reales en logs compartibles.
- Dependencias que exijan administrador, compilador o red en ejecución.
- Aproximaciones silenciosas, `except: pass`, lógica de negocio en la UI.
- Tablas o campos XER inventados en los sintéticos.
- Hacer push a `main`, usar `--force` o ampliar los permisos de la sesión.
- Detenerse a preguntar o esperar aprobación fuera de los casos de 0.3.
- Avanzar de fase con un criterio automatizable incumplido sin registrarlo como bloqueo, o relajar un criterio para que pase.
- Tests que pasan vacíos: un test omitido siempre lleva `skip` con motivo.

---

## 13. Contenido inicial de `AGENTS.md`

Ya existe desde la Fase 0: actualízalo a este contenido. Debe ser corto:

```markdown
# AtlasPMO — plataforma personal de análisis de cronogramas (P6 / MS Project)

Especificación completa: docs/MEGAPROMPT_v1.md · Estado: docs/ESTADO.md · Decisiones: docs/DECISIONES.md · Pendientes de Nicolás: docs/VALIDACIONES_PENDIENTES.md

## Reglas críticas
- Nunca leer archivos de data/real/ ni de ATLASPMO_GOLDEN_DIR. Cronogramas reales = confidenciales. El repositorio se trata como público.
- App 100 % local: sin red, sin telemetría.
- XER: cp1252, CRLF, tablas no modificadas idénticas byte a byte. Solo se usan campos documentados con evidencia en docs/XER_SPEC.md.
- Sin aproximaciones silenciosas: registrarlas en ModuleResult.approximations.
- Redundancia = camino alternativo ≥ lag en el grafo de eventos + confirmación con delta cero. Nunca "no es driver".
- Nada se declara terminado sin ejecutar sus tests y mostrar la evidencia.
- Código e identificadores en inglés; UI, docs y mensajes al usuario en español (es-CL).
- Modo autónomo: no preguntar; decidir, registrar en docs/DECISIONES.md y seguir. Checkpoint automático por fase.
- Ramas fase-N; nunca push a main ni --force.

## Comandos
- Tests: uv run pytest
- Lint y tipos: uv run ruff check . && uv run mypy src
- App: atlaspmo.bat (o uv run streamlit run src/atlaspmo/ui/app.py)
- Conformidad (solo Nicolás, en su equipo): uv run python scripts/run_conformance.py
```

---

## 14. Configuración de Grok Build

- **`.grok/config.toml` del proyecto:** incluye solo las claves que Grok Build admita a nivel de proyecto (verifícalo en su referencia de configuración).
- **Archivos de Nicolás:** no escribas en `~/.grok/config.toml`. Si recomiendas algo ahí, déjalo con el texto exacto en `VALIDACIONES_PENDIENTES.md` y sigue.
- **Subagentes:** no desactives subagentes ni personas; este proyecto los usa.
- **Otros harnesses:** si Nicolás usa Grok 4.7 desde Cursor o GitHub Copilot en vez de Grok Build, `AGENTS.md` sigue aplicando. Los roles de la sección 9.4 se ejecutan entonces en secuencia dentro de la sesión, con el mismo brief de 9.3.

---

## 15. Arranque

**Estado de partida.** La Fase 0 ya tiene un esqueleto en la rama `fase-0` (commits `904db1b` feat: esqueleto de la fase 0 y `da62a85` docs: alcance, decisiones y estado de la fase 0). La rama `fase-1` existe y apunta al mismo commit, sin trabajo propio. Este documento reemplaza a `docs/MEGAPROMPT.md`.

1. Lee este documento completo y `docs/ESTADO.md`. Si `ESTADO.md` indica trabajo en curso de una sesión anterior, retómalo desde la siguiente tarea pendiente.
2. **Cierra la Fase 0 en `fase-0`:**
   - reemplaza toda referencia a `docs/MEGAPROMPT.md` por `docs/MEGAPROMPT_v1.md` (en `AGENTS.md`, `.grok/agents/*.md`, `docs/` y código);
   - actualiza `AGENTS.md` (sección 13) y los subagentes (sección 9.4) a v1;
   - crea `docs/VALIDACIONES_PENDIENTES.md`;
   - reemplaza el fixture `tests/fixtures/synthetic/minimal.xer` (tabla inventada `SYNTH`) por uno con tablas reales de P6 (sección 7) y ajusta sus tests;
   - verifica la mecánica de 9.1 con `grok inspect` y `/agents`, si están disponibles; registra lo confirmado en `DECISIONES.md`;
   - corre el checkpoint de la Fase 0 (sección 10), corrige lo que falle y haz push de `fase-0`.
3. Pon `fase-1` al día con `git checkout fase-1 && git merge --ff-only fase-0`. Si el fast-forward falla, recrea `fase-1` desde `fase-0` solo si no tiene commits propios; si los tiene, regístralo como bloqueo y detente (0.3, punto 3).
4. Ejecuta las fases 1 a 5 con el ciclo de 9.5, sin pausas.
5. Al terminar, escribe el reporte final (sección 16) y detente.

---

## 16. Reporte final

Escríbelo en `docs/ESTADO.md` y muéstralo en la sesión. Incluye:
- **Por fase:** entregado, criterios automáticos (cumple / no cumple, con evidencia), rama y último commit.
- **Pruebas:** comando de la suite completa con su resultado, cobertura por paquete y benchmarks contra la sección 11.
- **Bloqueos:** lo que no se cumplió, con diagnóstico y próximo paso propuesto.
- **Supuestos `[VALIDAR]`:** lista con enlace a su ADR.
- **Para Nicolás:** checklist priorizado de `VALIDACIONES_PENDIENTES.md`.
- **Para la v2 del megaprompt:** qué partes de este documento fueron ambiguas, contradictorias o insuficientes, con propuesta de redacción.
