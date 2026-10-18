# INGEPRO RP V7.39 — Corrección de diagnóstico por recepción y fotografías

Base: V7.38. Mantiene módulos existentes y datos PostgreSQL.

- El selector de componentes del diagnóstico lista **solo** componentes con `condicion_ingreso='Recibido'` en la OT.
- El servidor valida la condición de recepción al crear y editar hallazgos; no basta con ocultar opciones en la interfaz.
- Se pueden crear muchos hallazgos para un mismo componente recibido.
- Cada hallazgo puede almacenar varias fotografías. La fotografía histórica permanece; las nuevas se agregan en `diagnostico_foto`.
- Cámara y selección múltiple desde archivos para fotografías adicionales.
- Anotaciones individuales por fotografía adicional, con foto original conservada.
- El PDF de diagnóstico incluye todas las fotografías de cada hallazgo, con marcas.
- Los hallazgos históricos de componentes que no estén recibidos siguen visibles; para editarlos debe seleccionarse un componente recibido.

## Despliegue
Respaldar PostgreSQL. Subir archivos a GitHub/Render como nueva versión. La inicialización `db.create_all()` creará la tabla `diagnostico_foto` sin borrar las anteriores. **No** crear una base de datos nueva ni restaurar tablas encima de producción.

## Verificación
Python `py_compile`, plantilla Jinja parseada y JavaScript `node --check`. No se ejecutó prueba funcional con Flask/Render; verificar con OT que contenga un solo componente recibido, crear varios hallazgos, añadir 3 fotos, guardar marcas y exportar PDF.
