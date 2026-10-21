# Gate E1

Codigo de salida: 1

- **G1** pass: ruff check y ruff format --check en verde
- **G2** pass: mypy src sin errores
- **G3** pass: python -m pytest exit 0
- **G4** fail: calendars lineas 81.6 < 90; calendars ramas 63.9 < 85; engine lineas 86.0 < 90; engine ramas 74.8 < 85; logic lineas 87.3 < 90; logic ramas 73.6 < 85 | cobertura_total: 87.9; calendars lineas 81.6% ramas 63.9%; engine lineas 86.0% ramas 74.
- **G5** pass: invariantes a-e con perfil qa
- **G6** pass: .                                                                        [100%]
- **G7** pass: no hay skip ni xfail
- **G8** pass: sin cronogramas fuera de fixtures, sin rutas de perfil, sin red
- **G9** pass: tablas y campos literales de src/ estan en XER_SPEC.md
- **G10** pass: 36 requisitos de E1 citan un archivo de test que existe. El verde de la suite lo mide G3.
- **G11** pass: cambios protegidos citan un ADR
- **G12** pass: tests 167 frente a 137
- **G13** fail: kill_score 54.0 < 70; engine 60.2 < 85; calendars 45.5 < 85; logic 52.0 < 85
