# INGEPRO RP V7.54 — Perfil Supervisor de Producción (prueba)

Crear desde **Usuarios INGEPRO → Nuevo usuario** y elegir rol **Supervisor de Producción**. Nombre sugerido `supervisor01`; contraseña privada de mínimo 8 caracteres. No se crea automáticamente ninguna contraseña ni usuario.

Permisos efectivos fijados en servidor: ingreso de OT, diagnóstico, lectura de planificación Gantt y control de producción. Denegadas por defecto las rutas no expresamente autorizadas (cotizaciones, gerencia, usuarios, exportación Excel, administración y modificación de planificación). El detalle OT de supervisión utiliza una plantilla separada sin información comercial. El inicio oculta cotización y precio neto.

Importante: revisar pruebas de integración antes de desplegar en producción, especialmente fotos, PDF de diagnóstico y creación de OT. El bloqueo Android FLAG_SECURE pertenece al proyecto Android y NO se incorpora al navegador web.

Sin migraciones PostgreSQL. No modifica permisos de administradores ni otros usuarios.
