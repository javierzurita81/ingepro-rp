# INGEPRO RP V7.59 — Corrección de limpieza de OT de prueba

- Corrige error HTTP 500 por FK `plan_liberacion_asignacion_id_fkey` al limpiar actividades.
- Agrega al orden de limpieza: `plan_liberacion`, `produccion_etapa`, `ot_interna`, `diagnostico_foto` y `diagnostico_marca`.
- Orden de eliminación de hijos a padres, dentro de una única transacción con rollback en caso de error.
- Mantiene protección administrativa, respaldo de sesión, validación de conteos y variable `HABILITAR_LIMPIEZA_OT=SI`.
- Conserva usuarios, clientes, modelos, componentes y reparaciones maestras.
- No cambia las demás pantallas ni módulos.

**Antes de utilizar en producción:** generar respaldo actualizado de PostgreSQL y verificar que el entorno desplegado tenga las tablas esperadas. Revisar la vista previa de registros y el resultado en Logs.
