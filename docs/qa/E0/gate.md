# Gate E0

Codigo de salida: 0

- **G1** pass: ruff check y ruff format --check en verde
- **G2** pass: mypy src sin errores
- **G3** pass: python -m pytest exit 0
- **G4** linea_base: Cobertura medida. El umbral de la seccion 8.1 no se declara cumplido en E0. 35
- **G5** linea_base: no existe tests/property
- **G6** linea_base: no medido: no hay tests/perf
- **G7** pass: no hay skip ni xfail
- **G8** pass: sin cronogramas fuera de fixtures, sin rutas de perfil, sin red
- **G9** pass: tablas y campos literales de src/ estan en XER_SPEC.md
- **G10** linea_base: 8 requisitos de E0; el verde se exige desde E1
- **G11** pass: cambios protegidos citan un ADR
- **G12** pass: sin etapa anterior; no hay regresion que medir
- **G13** linea_base: no medido: falta el informe de qa-sabotaje
