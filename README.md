# INGEPRO RP - Modelo de prueba
MVP para trazabilidad de reparaciones: ingreso de equipo, OT de diagnóstico, cotización/aprobación, reparación, control de calidad, referencia de checklist físico, embalaje y despacho.

## Local
pip install -r requirements.txt
python app.py

## Render
Build: `pip install -r requirements.txt`
Start: `gunicorn app:app`
Usar PostgreSQL mediante `DATABASE_URL`.
