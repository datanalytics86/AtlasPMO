# Rendimiento E2

Equipo: Intel Core Ultra 9 185H, 31.4 GB, Windows 11 Enterprise. Fecha 2026-10-21. Red de `gen_scale` con `series=False`. No se usó un XER real.

| Medición | Cifra | Qué cubre |
|---|---|---|
| Filtro de candidatos, 30 000 actividades | 0.345 s | 24 998 candidatos sobre 69 996 vínculos. Un grafo y un recorrido por origen. |
| `classify_links`, 100 actividades | 3.25 s | 81 candidatos y 121 corridas del CPM. |
| `classify_links`, 400 actividades | 58.1 s | 331 candidatos. El filtro solo, en esa red, tardó 0.003 s. |

La confirmación de 30 000 actividades no se corrió. El filtro ya deja del orden de 25 000 candidatos, y cada candidato que no entra en un conjunto de delta cero cuesta un CPM. En 100 actividades el CPM salió a unos 0.027 s; a 30 000, la cifra vieja del motor era del orden de 8 s. Con cerca de 1.5 CPM por candidato, la proyección queda en decenas de horas. No cumple los 3 minutos de la sección 11. No es un pass.

El test de `tests/perf/test_redundancy.py` cronometra solo el filtro y exige menos de 15 s. No afirma la confirmación de 30 000.
