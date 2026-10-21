# Ciclo 2 — pantalla, sin cerrar el gate

La pantalla ahora ofrece PDF, un zip Parquet, el manifiesto y, cuando el módulo trae tabla CPM, el visor que ya existía en `gantt_figure`. `minimal.xer` no trae fecha de corte, el motor no arma la tabla y la pantalla lo dice. El visor se prueba con un XER a mano que sí tiene fecha de corte y calendario. El lote llama a `run_folder` sobre una carpeta. Nada de eso recalcula fechas en la UI.

Sigue sin asociarse el baseline. La prueba de localhost sigue leyendo `.streamlit/config.toml` y no abre un socket. No se abrió un navegador: la evidencia nueva es AppTest.

G4 y G13 no se tocan. No se bajan umbrales. No se copia un kill score. Esto no es el e2e completo de B-01.
