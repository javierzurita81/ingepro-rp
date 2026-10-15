# INGEPRO RP V7.31 (preparación de limpieza y maestros)

- Maestro de Equipos con códigos basados en prefijos y ID persistente. Componentes nuevos con código automático; códigos anteriores se preservan.
- Edición de modelo, componentes y eliminación/desactivación protegida por administrador.
- Administración > Reiniciar OT: conteo, respaldo completo y confirmación explícita.
- PostgreSQL: requiere `pg_dump` instalado en el entorno de Render. Si falta, la limpieza queda bloqueada.
- La limpieza conserva tablas maestras y auditoría, no reinicia correlativos.
- No ejecutar sobre producción sin pruebas de restauración del respaldo.

- La ejecución permanece deshabilitada por defecto: requiere HABILITAR_LIMPIEZA_OT=SI tras validar la restauración del respaldo.
