# INGEPRO RP V7.26 — Planificación compacta como pantalla principal

- Menú Planificación e Inicio llevan directamente a `/planificacion/gantt`.
- Las rutas GET `/planificacion` y `/planificacion/detalle` redirigen al Gantt (conservan mes y año).
- Se oculta el acceso a Herramientas avanzadas en la vista principal para evitar el desorden.
- El módulo anterior se conserva en `/planificacion/administracion` para operaciones heredadas, sin eliminar datos ni tablas.
- Se mantienen etiquetas Aplica / No aplica con clic, PDF A3/A4, editor rápido y validaciones existentes.
- No se requiere migración ni reiniciar la base de datos.
- Desplegar ZIP como actualización del repositorio; revisar que Render publique la última confirmación (commit).
