# INGEPRO RP V7.18 — Listado integral de OT

Actualización basada en V7.17. Se conserva el resto de los módulos y la base de datos.

- Listado OT horizontal compacto, con buscador y filtros de cotización, aprobación y estado.
- Columnas de identificación, cliente, equipo y componentes del despiece, ingreso, referencia/guía, cotización, monto, contacto destinatario, fechas, estado de reparación, etapa de programación, trabajadores con colores, avance, entrega, documentación, ubicación y acciones.
- Componentes visibles en la misma fila y desplegables sin abrir OT.
- Datos vinculados a cotizaciones y asignaciones existentes, sin crear campos ni inventar valores.
- «Fecha envío» y «Aprobado por» se muestran con guion porque V7.17 no guarda esos campos de forma independiente. «Enviado a» utiliza el contacto de la cotización, si existe.
- «Avance» actual es el avance administrativo calculado por el modelo OT, no progreso físico real.
- No borra datos, no cambia el esquema de la base de datos y no realiza migraciones.

Pruebas: compilación de app.py y compilación de plantilla Jinja. Requiere validación funcional en Render.
