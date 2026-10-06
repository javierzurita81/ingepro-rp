# INGEPRO RP V7.3 — OT por despiece + edición de diagnóstico

Cambios principales:
- La OT queda vinculada al modelo de equipo mediante `modelo_id`.
- Las OT antiguas sin componentes intentan recuperar automáticamente el despiece según marca/modelo.
- Si no se puede identificar el modelo, aparece un selector para cargar manualmente el despiece.
- Bomba Vogel P204/5 carga sus componentes en la OT y el diagnóstico los utiliza individualmente.
- `General` solo aparece en diagnóstico cuando la OT realmente no tiene despiece.
- Hallazgos de diagnóstico ahora se pueden editar, incluyendo cambio opcional de fotografía.
- Campos técnicos usan `lang="es"` y `spellcheck="true"` para activar el corrector ortográfico español del navegador.
- No borra usuarios, OT, cotizaciones ni diagnósticos existentes.

## Despliegue
Descomprimir y subir a GitHub el contenido completo, reemplazando los archivos actuales. Hacer un solo commit y esperar que Render termine el deploy y muestre Live. No cambiar DATABASE_URL.
