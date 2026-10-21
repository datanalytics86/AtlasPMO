RECHAZADA-BLOQUEADA

Ciclo 3. El revisor emitió RECHAZADO. Esta corrida, por ADR-013, no abre un cuarto ciclo: el tercer rechazo consecutivo deja la etapa bloqueada. No es APROBADO.

Diagnóstico. El gate bloqueante está en verde en los tres ciclos. El importante abierto es I-3: R-198 cita `tests/test_conformance_stub.py::test_stub_exits_and_leaves_files_untouched`. Ese test comprueba que los bytes de un `.xer` no cambian y que la salida no contiene `secret`. Leer el archivo no cambia esos bytes, así que el test no fija que el script no abra la carpeta. `scripts/run_conformance.py` hoy no la abre: si `ATLASPMO_GOLDEN_DIR` está definida, imprime una frase fija. La evidencia está en `docs/qa/E0/hallazgos.md` y en `docs/qa/E0/gate.json` (exit_code 0, test_count 137). G4, G5, G6 y G13 siguen en linea_base y no están cumplidos.

Las etapas siguientes quedan condicionales a este hallazgo. No se reescribe historia ni se marca esta etapa como aprobada.

Ciclo 3, texto del revisor: HEAD `cfdfbd2`. El gate bloqueante está en verde: exit_code 0, test_count 137. Pass: G1, G2, G3, G7, G8, G9, G10, G11 y G12. G3 no corrió `uv run pytest` (en este equipo no arranca, ADR-004); corrió `python -m pytest` con exit 0. G4, G5, G6 y G13 están en linea_base: no están cumplidos y no se marcan pass. I-6, I-7, I-8, I-9 e I-10 quedaron cerrados. I-3 no: las filas que faltaban están, y R-350 deja SYNTH fuera de verde a propósito, pero el test de R-198 no prueba que el script no abra la carpeta. No hay críticos. Los menores no deciden. Con un importante abierto la etapa no cierra.
