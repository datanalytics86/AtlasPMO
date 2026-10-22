# Gate E7

Codigo de salida: 0

- **G1** pass: ruff check y ruff format --check en verde
- **G2** pass: mypy src sin errores
- **G3** pass: python -m pytest exit 0
- **G4** pass: cobertura_total: 91.2; calendars lineas 91.5% ramas 81.6%; engine lineas 95.0% ramas 89.8%; logic lineas 88.6% ramas 75.3%; model lineas 100.0% ramas 100.0%; resto lineas 89.9% ramas 78.8% | meta pendiente: calendars ramas 81.6 bajo la meta
- **G5** pass: invariantes a-e con perfil qa
- **G6** pass: ....                                                                     [100%]
- **G7** pass: no hay skip ni xfail
- **G8** pass: sin cronogramas fuera de fixtures, sin rutas de perfil, sin red
- **G9** pass: tablas y campos literales de src/ estan en XER_SPEC.md
- **G10** pass: 5 requisitos de E7 citan un archivo de test que existe. El verde de la suite lo mide G3.
- **G11** pass: cambios protegidos citan un ADR
- **G12** pass: tests 236 frente a 216
- **G13** info: no medido: falta el informe de qa-sabotaje
