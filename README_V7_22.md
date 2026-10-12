# INGEPRO RP V7.22 — Validación consistente de HH en Gantt

- Corrige el salto de validación: editar una asignación ahora verifica las HH estimadas igual que crearla.
- Al editar un día se descuenta solo la asignación anterior de ese día, incluso si proviene de un rango de fechas.
- Mantiene las validaciones de disponibilidad del trabajador y duplicidad.
- El mensaje de error muestra HH estimadas, programadas sin la casilla, disponibles y solicitadas.
- Sin cambios de esquema de PostgreSQL.
- No se modifica la interfaz Gantt compacta.

**Nota:** La validación de jornada permanece en 8 h/día como en V7.21; la configuración de 9 h lunes-miércoles debe implementarse y probarse por separado.
