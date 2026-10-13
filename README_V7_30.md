# INGEPRO RP V7.30 — Control general de OT compacto

Cambios exclusivos de `templates/index.html` y CSS al final de `static/style.css`:
- Botones pequeños Nueva OT y Excel.
- Filtro automático de búsqueda (550 ms) y condición; enlace Limpiar discreto.
- Filas separadas con borde gris claro y esquinas redondeadas.
- Condición actual y títulos de fecha en dos líneas; botón Ver eliminado.
- Enlace del número de OT conserva navegación al detalle.
- Exportación Excel sigue utilizando filtros del backend existente.

No se modifica `app.py`, base de datos, Gantt ni pantalla de seguimiento dentro de OT.
Respaldar datos y probar en Render antes de usar en producción.
