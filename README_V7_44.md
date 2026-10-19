# INGEPRO RP V7.44 — Corrección de Nueva OT

- Corrige el error 500 al abrir `/ot/nueva`: la plantilla requería `catalogo` pero `nueva_ot()` no lo entregaba.
- Genera `catalogo` con estructuras JSON serializables de modelos activos.
- Materialidad mostrada a partir de las materialidades configuradas en los componentes del modelo; cuando no existen, queda sin completar para impedir la confirmación accidental.
- Sin migraciones ni cambios de tablas PostgreSQL.
- Validación: compilación Python y prueba local de render de plantilla con Jinja2. No se ha probado en Render.
