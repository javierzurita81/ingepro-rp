# INGEPRO RP V7.16 – Control de Gerencia

- Nuevo menú **Gerencia** para administradores y usuarios autorizados para cotizaciones.
- Tabla filtrable por OT, cliente, cotización, aprobación y planificación.
- Resumen por OT y componente con reparaciones, trabajador (sigla y color), fechas y horas.
- Porcentaje basado únicamente en etapas marcadas explícitamente como finalizadas; una programación no se considera ejecución.
- Sin migraciones ni borrado de base de datos. Se conserva la planificación V7.15.
- Los registros antiguos sin componente asociado se identifican como históricos.
- Nota: el modelo actual de OT no tiene un campo dedicado OT SQM; la referencia existente `guia` se muestra como referencia cliente, sin asumir que sea OT SQM.
- Pendiente de prueba funcional con la base real en Render.
