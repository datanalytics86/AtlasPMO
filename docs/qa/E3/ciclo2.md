# Ciclo 2 — cadena driving que el motor ya calculaba

El test `test_the_longer_predecessor_is_the_driving_one` se escribió antes del arreglo. La primera corrida falló:

```
KeyError: 'driving_codes'
FAILED tests/test_e3_paths.py::test_the_longer_predecessor_is_the_driving_one
```

El motor ya guardaba `driving_preds` y no los devolvía. Ahora `ScheduledActivity.driving_pred_ids` sale del mismo criterio: el límite de la predecesora coincide con el inicio temprano, incluida la regla del hito abierto. El modo B arma la columna `driving_codes` y la tabla `driving_chain`, desde el término del proyecto o desde `milestone_code`.

En la red a mano, SHORT dura 8 h y LONG dura 16 h, ambas FS hacia JOIN. Solo LONG queda driving. La cadena de JOIN es LONG y JOIN. No es un float path de P6 y no hay doble firma.

Sigue sin implementarse: multiple float paths, la continuidad desde la fecha de corte hasta el término, y la mitad de WBS de R-326. G4 y G13 no se tocan. No se bajan umbrales. No se copia el kill score de E1. No se reejecuta la mutación.
