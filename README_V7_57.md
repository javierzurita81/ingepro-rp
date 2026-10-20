# INGEPRO RP V7.57

- Administrador libera individualmente una asignación existente desde la carta Gantt.
- Supervisor puede crear asignaciones y editar únicamente una asignación liberada.
- La liberación se consume automáticamente al guardar la modificación; queda bloqueada otra vez.
- El supervisor no puede eliminar, duplicar o modificar por rutas de edición alternativas.
- Se registran en PostgreSQL el administrador que liberó, la fecha de liberación, el supervisor que utilizó el permiso y su fecha.
- La tabla `plan_liberacion` se crea mediante `db.create_all()` en el arranque. Hacer respaldo de PostgreSQL antes de desplegar.
- Pruebas locales: compilación Python, sintaxis de plantillas y ZIP; pendiente probar en Render con usuarios reales.
