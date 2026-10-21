# Manual de usuario

AtlasPMO analiza cronogramas de Primavera P6 y MS Project en este equipo.
No usa red ni telemetría. Los cronogramas reales no se guardan en el repositorio
y esta aplicación no abre `ATLASPMO_GOLDEN_DIR`.

## Instalación en un paso

Hace falta Python 3.12. Si falta `uv`, sin permisos de administrador:

```
py -3.12 -m pip install --user uv
```

En la raíz del repositorio:

```
py -3.12 -m uv sync --group dev
```

Eso instala el entorno de desarrollo. Comprobar:

```
py -3.12 -m uv run python -m pytest
py -3.12 -m uv run python -m ruff check .
py -3.12 -m uv run python -m mypy src
```

En este equipo `uv run pytest` y `uv run streamlit` fallan con `os error 5`.
El lanzador y los comandos de arriba evitan ese fallo. El detalle está en
`docs/DECISIONES.md` (ADR-004).

## Abrir la pantalla

Doble clic en `atlaspmo.bat`, o desde la raíz:

```
py -3.12 -m uv run python -m streamlit run src/atlaspmo/ui/app.py
```

`uv run streamlit` falla en este equipo (ADR-004). `.streamlit/config.toml`
pide `localhost` y apaga las estadísticas de uso. Esta versión no demostró,
con un socket, que un proceso esté escuchando.

La pantalla carga un XER, muestra cuántas actividades tiene, deja elegir
módulos y un perfil de calidad, y ejecuta. Resultados y exportaciones van en
dos pestañas. Se descarga Excel, PDF, un zip Parquet y el manifiesto. El
visor aparece solo si el módulo trae una tabla CPM con inicio y fin tempranos.
Sin fecha de corte el motor no arma esa tabla y la pantalla lo dice. El lote
corre los XER de una carpeta. La biblioteca guarda métricas en un DuckDB y no
guarda el cronograma.

El baseline no se asocia. No hay avance parcial: la barra se llena al
terminar. No hay bandas de holgura ni filtro por WBS. No se abrió un
navegador para escribir esto. La evidencia de la pantalla es AppTest, en
`tests/test_e5_ui.py`.

## Módulos

| Nombre en la lista | Qué hace | Límite |
|---|---|---|
| Calidad (DCMA y GAO) | Chequeos DCMA salvo la prueba de ruta, más lo automatizable de GAO | El índice deja fuera lo `no_evaluable` y lo `info` |
| Ruta crítica (modo A) | Bandas con la holgura guardada | No reprograma. Sin holgura convertible, la actividad no entra |
| Ruta crítica (modo B) | Recalcula con el motor e incluye la prueba DCMA 12 | La sonda son 8 horas en la primera crítica por `task_code` |
| Lógica redundante | Marca un vínculo solo si al quitarlo el CPM no se mueve | No usa reducción transitiva |
| Limpieza de XER | Borra filas `TASKPRED` confirmadas | Hace falta el XER original. No hay paso de aprobación en la pantalla |
| Riesgo (Monte Carlo) | Sensibilidad y muestreo | Los rangos los pone el usuario. No salen del XER |
| EVM y Earned Schedule | PV, EV, AC y Earned Schedule a la fecha de corte | PV lineal. La curva es un solo punto |
| Comparación de updates | Diferencias entre dos cronogramas | Solo por `task_code`. Hacen falta los dos cronogramas; la pantalla no pide el segundo |

Cada simplificación queda en `approximations` del resultado, en la leyenda de
la pantalla y en el Excel, el PDF y el manifiesto cuando se exporta.

## Riesgo

Los rangos mínimo / más probable / máximo, la distribución, la correlación y
los eventos son configuración del llamado. La semilla queda en el resultado.

Con rangos de ancho cero y sin eventos, el término repite el CPM determinístico.
Eso está probado a mano en `tests/test_risk.py`. No está contrastado con P6.
El motor es Python puro: numba no está cargado. No se midió el caso de
30 000 actividades por 1 000 iteraciones.

P50, P80 y P90 usan el índice `ceil(p * n) - 1` sobre las fechas ordenadas.

## EVM

`CP_Phys`, `CP_Drtn` y `CP_Units` son nombres vistos en XER públicos, sin
confirmar en un export de este equipo. `CP_Units` y el tope de recurso quedan
`no_evaluable`. El PV es lineal en tiempo laboral. La tabla `scurve` tiene un
solo punto, en la fecha de corte. El caso a mano está en `tests/test_evm.py`.
No se contrastó con P6.

## Comparación, lote y biblioteca

La comparación usa la holgura total guardada. No recalcula el CPM. Un lag vacío
no se compara como cero.

El lote lee solo `*.xer` de una carpeta. Sin módulos elegidos corre calidad.
Si la pantalla tiene una selección, usa esos módulos. Ordena por índice de
mayor a menor. Un índice ausente queda al final. También se puede llamar
desde Python:

```python
from pathlib import Path

from atlaspmo.batch import run_folder, write_ranking

rows = run_folder(Path("carpeta"))
write_ranking(Path("ranking.xlsx"), rows)
```

La biblioteca DuckDB guarda corridas, métricas y hallazgos. Las actividades
entran solo si `store_schedule` es verdadero. La pantalla guarda métricas y
no pide guardar el cronograma. En EVM, `fact_timephased` guarda la duración
remanente en el balde `corte` cuando la actividad trae `spread_hours`. No es
una curva por periodo. `dim_activity` no se llena desde la pantalla.

## Power BI

`powerbi/AtlasPMO.pbip` apunta el parámetro `ParquetFolder` a
`C:/AtlasPMO/parquet`, un marcador de posición. Esta corrida no abrió el archivo
en Power BI Desktop ni comprobó el refresco. Las medidas definidas son
`Hallazgos` y `IndicePromedio`.

## MSPDI y .mpp

El lector MSPDI cubre el fixture `tests/fixtures/synthetic/mspdi/chain.xml`.
No lee calendarios. No traduce `ConstraintType` a códigos `CS_*`. Una duración
con componente de días cuenta 24 horas de reloj por día, y lo anota.
La fecha de corte es `StatusDate`.

`.mpp` no se abre en este equipo: Java no está en el PATH y el extra `[mpp]`
no queda instalado con el `uv sync` de arriba. `read_mpp` avisa y no importa
`mpxj`.

## Checklist de reimportación en P6

Estos pasos no se ejecutaron en esta corrida. Tampoco se importaron los
fixtures sintéticos: no hay `p6_verified`.

1. Correr la limpieza sobre una copia de trabajo. El módulo elimina solo las
   filas `TASKPRED` ya confirmadas como redundantes. La pantalla no pide
   aprobación.
2. Dejar el XER limpio fuera del repositorio.
3. En P6, importarlo como proyecto nuevo.
4. Anotar cualquier error de importación.
5. Reprogramar con la misma fecha de corte y la misma opción de avance usada
   en la limpieza. El valor por defecto del módulo es retained logic.
6. Comparar fechas tempranas, fechas tardías y holgura total con las de antes
   de reprogramar. El criterio del producto es que no cambien.
7. No copiar ese archivo a `data/real/` ni dejarlo en una ruta que el
   repositorio pueda commitear. No hace falta abrir `ATLASPMO_GOLDEN_DIR`
   para este checklist.

`scripts/run_conformance.py`, si la variable de entorno está definida, imprime
que no abre esa carpeta.

## Qué no está medido

El detalle y los números de la suite están en `docs/ESTADO.md`. En corto:
no se midió la redundancia bajo 3 minutos, ni el Monte Carlo grande, ni el
99,5 % contra cronogramas reales, ni la importación limpia en P6, ni la
apertura del PBIP.
