# INGEPRO RP V7.63 — Guías de Despacho internas

- Nuevo módulo para Administración (permiso `despacho`).
- Una guía puede incluir componentes de múltiples OT del mismo cliente.
- Selección parcial por componente recibido, evitando repetir componentes ya despachados.
- Número correlativo asignado al guardar: `GD-000001` basado en ID persistente.
- Editar borradores, confirmar despacho, anular borradores y descargar PDF interno.
- Se agregan tablas mediante `db.create_all()` existente; no se eliminan tablas anteriores.
- No constituye documento tributario electrónico SII.
- Cantidad inicial por componente: 1; no admite fraccionar unidades del mismo componente.
- Confirmaciones simultáneas y restauraciones de datos deben verificarse en ambiente de pruebas antes de producción.
