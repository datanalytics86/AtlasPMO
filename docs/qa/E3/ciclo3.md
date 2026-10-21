# Ciclo 3 — lo que esta corrida no cierra

No hay una corrección correcta, en esta corrida, que deje G4 o G13 en verde.

G4 mide calendarios, motor y lógica. En los ciclos 1 y 2 esas seis cifras no se movieron: calendars líneas 85.2 y ramas 70.9, engine líneas 89.4 y ramas 79.5, logic líneas 88.6 y ramas 75.3. Llegar al umbral de la sección 8.1 exige cubrir ramas que E1 ya dejó abiertas después de tres ciclos. No se agregan tests vacíos y no se bajan umbrales.

G13 pide el informe de sabotaje de esta etapa. No existe `docs/qa/E3/sabotaje.md`. El último informe completo es el de E1, con kill_score 54.0, y el código de lógica cambió en E2. Copiarlo sería falso. Esa corrida no llegaba a 85. Aquí no se rehace la mutación y no se inventa un score.

La cadena driving del ciclo 2 queda. Siguen sin implementarse los multiple float paths, la continuidad desde la fecha de corte hasta el término, la doble firma fuera del CPLI de 24 h + 16 h, el caso con SS solapado, el caso con feriado y la WBS requerida de R-326. No se lee un golden ni un XER real.
