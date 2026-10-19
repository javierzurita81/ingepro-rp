# INGEPRO RP V7.41 — Ajuste fotográfico PDF

Base: INGEPRO RP V7.40. Cambios únicamente en el generador PDF de Diagnóstico Técnico (`app.py`).

- Fotografías centradas horizontalmente dentro de la columna izquierda.
- Proporción original de cada fotografía preservada, sin recortes ni deformación.
- Límite de altura de 210 puntos y ancho adaptativo al espacio disponible.
- Esquinas suavizadas mediante máscara PNG transparente, sin recortar contenido relevante.
- Pie de fotografía centrado debajo de cada imagen.
- Sin migraciones de base de datos ni cambios en módulos de OT, diagnóstico o fotografías guardadas.

Verificación: `python -m py_compile app.py`. Pendiente: prueba de PDF real en Render con fotos verticales y horizontales.
