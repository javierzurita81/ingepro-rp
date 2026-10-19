# INGEPRO RP V7.43 — Corrección de error HTTP 500

- Se agrega la ruta POST `/ot/<ot_id>/agregar-componentes` (`agregar_componentes_ot`) utilizada por `templates/ot.html`.
- Solo se aceptan componentes activos pertenecientes al modelo asociado a la OT.
- Si el componente ya existe como «No recibido», se actualiza a «Recibido» sin duplicarlo.
- Se conservan hallazgos, fotografías y datos de la OT.
- No requiere migraciones de base de datos.
- Validación local: compilación sintáctica de `app.py` y estructura ZIP. Pendiente prueba de ejecución en Render.
