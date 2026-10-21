# Gate E0

Codigo de salida: 0

- **G1** pass: ruff check y ruff format --check en verde
- **G2** pass: mypy src sin errores
- **G3** pass: python -m pytest exit 0
- **G4** linea_base: calendars ramas 81.0 < 85; engine lineas 83.5 < 90; engine ramas 72.4 < 85; logic lineas 76.1 < 90; logic ramas 60.6 < 85; model ramas 62.5 < 85 | calendars lineas 91.8% ramas 81.0%; engine lineas 83.5% ramas 72.4%; logic lineas 76.1% ramas
- **G5** linea_base: no existe tests/property
- **G6** linea_base: no medido: no hay tests/perf
- **G7** pass: no hay skip ni xfail
- **G8** pass: sin cronogramas fuera de fixtures, sin rutas de perfil, sin red
- **G9** pass: tablas y campos literales de src/ estan en XER_SPEC.md
- **G10** pass: 16 requisitos de E0 citan un archivo de test que existe. El verde de la suite lo mide G3.
- **G11** pass: cambios protegidos citan un ADR
- **G12** pass: sin etapa anterior; no hay regresion que medir
- **G13** linea_base: no medido: falta el informe de qa-sabotaje
