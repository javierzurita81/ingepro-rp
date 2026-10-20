# INGEPRO RP V7.56 — Planificación de supervisor

- Supervisor puede crear asignaciones nuevas desde el Gantt (API `api_gantt_rapido`).
- Prohibido modificar o eliminar asignaciones existentes, validado en el servidor con HTTP 403.
- Interfaz impide abrir asignaciones existentes y deshabilita cambiar Aplica/No aplica.
- Mensajes diferenciados para HTTP 403 y errores de conexión.
- Administrador conserva el flujo existente.
- No requiere migración de base de datos.

**Pendiente:** prueba real en Render con PostgreSQL y cuenta `supervisor01`.
