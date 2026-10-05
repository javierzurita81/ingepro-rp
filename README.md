# INGEPRO RP v3
Prototipo de sistema de reparación y trazabilidad.

## Novedades v3
- Configuración inicial del Administrador.
- Inicio/cierre de sesión.
- Creación de usuarios por el Administrador.
- Permisos por módulo.
- Activación/desactivación de usuarios.
- Contraseñas almacenadas con hash seguro.
- Auditoría básica de accesos, creación de usuarios y cambios de OT.
- Mantiene ingreso de equipos con clientes/modelos/componentes en listas.

## Primer ingreso
Al desplegar una base de datos nueva, abre la aplicación. El sistema mostrará **Configuración inicial** para crear el primer Administrador. Después esa pantalla queda bloqueada.

## Producción
Configurar `SECRET_KEY` como variable de entorno en Render y usar PostgreSQL mediante `DATABASE_URL`.
