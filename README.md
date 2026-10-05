# INGEPRO RP - Modelo de prueba v2

MVP de trazabilidad de reparaciones con ingreso por listas maestras.

## Incluye
- Cliente desde lista desplegable.
- Bomba/modelo desde lista desplegable.
- Recepción completa o parcial.
- Selección múltiple de componentes cuando la bomba no llega completa.
- OT correlativa automática.
- Flujo diagnóstico, cotización/aprobación, reparación, calidad, checklist físico, embalaje y despacho.

## Datos demo iniciales
Clientes: SQM Nueva Victoria, SQM Salar, Cliente de prueba.
Modelo: Bomba centrífuga Vogel P204/5.
Componentes: Eje, Cuerpo de rodamientos, Impulsor, Voluta, Frame adapter.

## Render
Build: `pip install -r requirements.txt`
Start: `gunicorn app:app`
Usar PostgreSQL mediante `DATABASE_URL`.
