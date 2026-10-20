# INGEPRO RP V7.50 — Corrección jornada de Planificación

Base: V7.49 entregada por el usuario.

- Jornada ordinaria: lunes 9 h, martes 9 h, miércoles 8 h, jueves 8 h, viernes 8 h (42 h semanales).
- El límite del selector de horas en la Carta Gantt se ajusta a 9 h o 8 h según la fecha.
- Se distingue explícitamente el saldo de HH estimadas de una reparación del cupo diario del trabajador. La regla existente que impide exceder HH estimadas no se modifica.
- Sábado y domingo mantienen provisionalmente el comportamiento anterior de 8 h; la política de sábados, domingos y horas extraordinarias se definirá después.
- Sin cambios de esquema PostgreSQL ni migraciones.
- Pruebas pendientes: integración en Render y validación con datos reales.
