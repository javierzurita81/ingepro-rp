# INGEPRO RP V7 – División Maestranza

Actualización acumulativa sobre V6. Mantiene PostgreSQL y los datos existentes.

Novedades:
- Identidad visual INGEPRO / División Maestranza en inicio y navegación.
- Logo INGEPRO integrado en PDF de cotización.
- Módulo Clientes/Empresas con RUT chileno validado por módulo 11 y control de duplicados.
- Contactos por empresa con roles de recepción de cotización, aprobación e informes.
- Maestro de Equipos: Tipo → Marca → Modelo → Despiece.
- Componentes del despiece con código (ej. CPR T10), categoría y material.
- Ingreso de OT por despiece: Recibido / No recibido.
- Control por componente dentro de la OT: condición de ingreso, resolución, material y ubicación.
- Resoluciones: Sin intervención, Reutilizar, Reparar, Recuperar, Fabricar nuevo, Suministrar nuevo, Reemplazar.

IMPORTANTE: no borrar la base PostgreSQL ni modificar DATABASE_URL. La aplicación crea tablas/columnas nuevas sin borrar OTs, usuarios o cotizaciones existentes.
