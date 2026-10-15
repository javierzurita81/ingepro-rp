# INGEPRO RP V7.34 — Migración controlada de códigos de componentes

Ruta de administrador: `/administracion/codigos-componentes`.

- Vista previa determinista: prefijo de componente (2 letras), marca (3 letras), correlativo por combinación (4 dígitos).
- Los códigos existentes no se cambian al desplegar la aplicación.
- Descargar respaldo PostgreSQL completo con pg_dump disponible en Render.
- Verificar manualmente que el archivo de respaldo sea restaurable.
- Para aplicar, habilitar temporalmente `HABILITAR_MIGRACION_CODIGOS=SI` en Render.
- Confirmar escribiendo `ACTUALIZAR CODIGOS`.
- Conserva IDs de componentes y reparaciones, actualiza el código visible en OTComponente vinculados.
- Si los datos cambiaron desde el respaldo, se bloquea la operación.
- Deshabilitar la variable tras terminar.

**Precaución:** la versión de PostgreSQL usada por pg_dump debe ser compatible con el servidor. Probar en un entorno de ensayo y verificar el respaldo antes de ejecutar en producción.
