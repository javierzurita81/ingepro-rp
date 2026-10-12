# INGEPRO RP V7.23 — Jornadas y HH Gantt

Base: V7.22. Se mantiene corrección de HH estimadas de reparación y edición rápida.

- Lunes, martes, miércoles: 9 h máximas por trabajador y fecha.
- Jueves y viernes: 8 h máximas por trabajador y fecha.
- Sábado y domingo: sin cambio respecto de V7.22 (límite provisional de 8 h); su política se definirá posteriormente.
- La API de disponibilidad devuelve `limite`, `ocupadas` y `disponibles`.
- Validación central en `validar_cupo` para Gantt, formularios y duplicación.
- Campo de horas de formularios acepta hasta 9; el servidor aplica el máximo de cada día.
- La pantalla de carga avanzada marca sobrecarga según jornada de cada fecha.
- No se altera la apariencia del Gantt compacto ni el esquema PostgreSQL.

**Despliegue:** subir contenido del ZIP al repositorio GitHub, desplegar en Render, probar primero con datos de prueba. No reiniciar ni borrar la base.
