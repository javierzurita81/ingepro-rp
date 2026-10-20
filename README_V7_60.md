# INGEPRO RP V7.60 — Informe de salida

- Nuevo Informe de Salida por OT, independiente del diagnóstico.
- Solo componentes recibidos, hallazgos, fotos múltiples, anotaciones y PDF.
- Enlace desde el detalle de OT.
- Tres tablas nuevas: salida_hallazgo, salida_marca, salida_foto. Se crean mediante db.create_all al arrancar.
- Limpieza de OT actualizada para eliminar también informes de salida.
- No se modifica ni se copia información existente del diagnóstico.

**Precaución:** hacer respaldo en Render antes del despliegue. Probar primero en entorno de pruebas.
