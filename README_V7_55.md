# INGEPRO RP V7.55 — Acceso a OT Internas para supervisión

- Se autorizan las rutas `oti_lista`, `oti_seleccionar`, `oti_editar` y `oti_pdf` por GET para el rol Supervisor de Producción.
- Se autorizan `oti_nueva` y `oti_editar` por POST para crear y editar OT Internas.
- No se habilitan eliminación de OT ni módulos comerciales; la lista blanca de V7.54 se mantiene.
- Los permisos del administrador y los demás perfiles no cambian.
- El PDF de OT Interna muestra datos técnicos, sin precios.
- No requiere migración de base de datos.
- Pendiente prueba funcional en Render con usuario supervisor01.
