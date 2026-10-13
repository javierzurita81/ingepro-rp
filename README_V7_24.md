# INGEPRO RP V7.24 — Gantt compacto

Basado en V7.23. Mantiene los módulos y PostgreSQL existentes.

## Cambios
- Selector Aplica / N/A en la columna fija de cada etapa de la carta Gantt.
- Estado N/A persistido en PlanNoAplica mediante endpoint existente, ahora compatible con JSON.
- Etapas N/A visibles en gris, sin programación. Para marcar N/A una etapa con asignaciones, primero se deben eliminar esas asignaciones mediante el editor rápido; no se borran horas sin consentimiento.
- Las etapas nuevas agregadas al maestro de reparaciones de un componente se cargan automáticamente al actualizar la carta Gantt, para las OT aprobadas y componentes recibidos que estén vinculados a ese maestro.
- Botones PDF mensual A3 horizontal y PDF individual A4 horizontal. Ambos leen datos actuales de la base de datos.
- Jornada V7.23 conservada: lunes a miércoles 9h, jueves y viernes 8h; sábado/domingo sin cambios.

## Validación
Se ha verificado sintaxis Python y estructura del ZIP. No se pudo ejecutar Flask/Render en este entorno: probar en un despliegue de prueba antes de producción. No borrar ni reiniciar PostgreSQL.
