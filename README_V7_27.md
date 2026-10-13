# INGEPRO RP V7.27 — Seguimiento compacto de OT

Basado en V7.26. Se agregó en el detalle de cada OT un panel de diez etapas, con bloques verdes, rojos y grises, navegación contextual y estados derivados de registros existentes.

Cambios: control de diagnóstico previo a cotización; aprobación únicamente desde cotización; planificación requiere cotización aprobada; campos de envío de cotización y entrega en faena; migración aditiva de columnas en `ot`. No se borra ni reinicia la base de datos. No se alteraron plantillas del Gantt.

**Importante:** el diagnóstico se considera registrado cuando existe texto de diagnóstico o hallazgos. La finalización de reparación/calidad/despacho se infiere de los campos existentes, por lo que conviene validar el criterio operativo antes de usarlo como cierre formal. El seguimiento de entrega exige fecha y receptor; la guía y salida siguen como datos de despacho existentes. La aprobación comercial se realiza desde el estado de cotización.

**Verificación:** `python -m py_compile app.py` correcta. No se pudo ejecutar una prueba Flask en este entorno porque no están instaladas sus dependencias. Probar primero en ambiente de pruebas con copia de seguridad de PostgreSQL antes de desplegar en producción.
