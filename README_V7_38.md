# INGEPRO RP V7.38 — Diagnóstico técnico vertical

Base: INGEPRO RP V7.37. Se conservan los demás módulos y datos.

- Todos los hallazgos se muestran uno debajo de otro, con fotografía izquierda y formulario derecho.
- Un archivo fotográfico por hallazgo. Botones independientes para cámara de tablet y galería/archivo.
- Edición de hallazgos en la misma página y guardado mediante las rutas existentes.
- Herramientas táctiles círculo, flecha, cuadro, tres colores y deshacer; botón Guardar marcas.
- Las anotaciones se guardan en una tabla PostgreSQL nueva `diagnostico_marca` y se integran al PDF; el original fotográfico no se modifica.
- Se mantienen la selección de componentes de la OT y la integración con reparaciones/planificación.

## Instalación
Subir el contenido de este ZIP al repositorio del servicio web Render. La inicialización existente `db.create_all()` creará la tabla adicional sin borrar las tablas anteriores. No reemplazar la base de datos. Hacer respaldo antes de desplegar.

## Validación
Sintaxis Python y plantilla Jinja verificadas. No se pudo ejecutar prueba integrada del servidor Flask en este entorno porque no está instalada la dependencia Flask. Probar cámara, archivo, marcas, edición y PDF en Render antes de usar en producción.
