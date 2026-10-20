# INGEPRO RP V7.52 — Control de Producción
- Nuevo módulo en Inicio y navegación, visible solo a administradores o usuarios con permiso explícito `produccion`.
- Seguimiento por OT, componente recibido y reparaciones seleccionadas; colores: verde ejecución, rojo pendiente, gris terminado.
- Las jefaturas registran término, observación, usuario y fecha; secuencia de etapas obligatoria.
- Sin planificación (S/P) no se permite cerrar una etapa.
- Nuevo modelo `ProduccionEtapa`, creado automáticamente mediante `db.create_all()` al iniciar. No elimina datos anteriores.
- Se conserva planificación, OT Internas y límite diario de horas V7.51.
- Nota: el permiso es por usuario, no por área/jefatura. El alcance por área deberá configurarse en una versión posterior.
- Los estados de ejecución en esta primera versión se derivan de la primera etapa no terminada que tenga planificación.
