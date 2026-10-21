# Gate E1

Codigo de salida: 1

- **G1** pass: ruff check y ruff format --check en verde
- **G2** pass: mypy src sin errores
- **G3** pass: python -m pytest exit 0
- **G4** fail: calendars lineas 85.2 < 90; calendars ramas 70.9 < 85; engine lineas 89.4 < 90; engine ramas 79.5 < 85; logic lineas 87.3 < 90; logic ramas 73.6 < 85 | cobertura_total: 88.8; calendars lineas 85.2% ramas 70.9%; engine lineas 89.4% ramas 79.
- **G5** pass: invariantes a-e con perfil qa
- **G6** pass: .                                                                        [100%]
- **G7** pass: no hay skip ni xfail
- **G8** pass: sin cronogramas fuera de fixtures, sin rutas de perfil, sin red
- **G9** pass: tablas y campos literales de src/ estan en XER_SPEC.md
- **G10** pass: 36 requisitos de E1 citan un archivo de test que existe. El verde de la suite lo mide G3.
- **G11** pass: cambios protegidos citan un ADR
- **G12** pass: tests 173 frente a 137
- **G13** fail: kill_score 54.0 < 70; engine 60.2 < 85; calendars 45.5 < 85; logic 52.0 < 85
