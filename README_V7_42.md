# INGEPRO RP V7.42

- Nueva OT: tipo, marca y modelo encadenados desde catálogo; materialidad automática; fecha de ingreso y receptor automáticos.
- Campos obligatorios validados en servidor: cliente, modelo, materialidad, fecha envío cliente, guía y al menos un componente recibido. Opcionales: OT cliente, número de parte y número de identificación.
- Datos de ingreso editables desde la OT, sin alterar número, fecha de creación ni receptor inicial.
- Incorporación posterior de componentes del modelo en una OT existente, con protección contra duplicados y sin borrar hallazgos.
- Migración ligera y aditiva de columnas en PostgreSQL existente; no borra datos.
- Si un modelo carece de materialidad de catálogo y sus componentes tampoco la tienen, debe completarse la materialidad en el catálogo antes de crear la OT.
- No se ha desplegado ni probado en Render con datos de producción.
