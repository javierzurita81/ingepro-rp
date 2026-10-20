# INGEPRO RP V7.53 — Diseño agrupado de Control de Producción

- Una tarjeta por OT, incluyendo todos sus componentes recibidos y sus etapas seleccionadas.
- Tarjeta exterior blanca con borde delgado gris oscuro (#515963).
- Encabezado de OT negro (#111111); componentes gris medio (#C7CDD3); títulos de componentes gris acero (#737D88).
- Etapas verde (en ejecución), rojo (pendiente) y gris (terminada).
- Porcentaje de avance general de la OT y avance de cada componente.
- Se conserva el botón Terminar, su formulario y la validación de permisos, secuencia y registro del término de V7.52.
- Sin cambios en tablas o migraciones de PostgreSQL respecto de V7.52.
- Validaciones realizadas: compilación Python, análisis de plantilla Jinja e integridad ZIP. Requiere prueba funcional en Render.
