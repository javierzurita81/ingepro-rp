import os, json
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','cambiar-esta-clave-en-produccion')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///ingepro.db')
if db_url.startswith('postgres://'): db_url = db_url.replace('postgres://','postgresql://',1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

PERMISOS = {
 'ingreso':'Ingreso de equipos', 'diagnostico':'Diagnóstico', 'cotizaciones':'Cotizaciones',
 'reparacion':'Reparación', 'calidad':'Control de calidad', 'despacho':'Embalaje y despacho',
 'informes':'Informes', 'maestros':'Maestros', 'clientes':'Clientes y contactos', 'usuarios':'Administración de usuarios'
}

class Usuario(db.Model):
    id=db.Column(db.Integer, primary_key=True); username=db.Column(db.String(60), unique=True, nullable=False)
    nombre=db.Column(db.String(120), nullable=False); cargo=db.Column(db.String(100)); password_hash=db.Column(db.String(255), nullable=False)
    rol=db.Column(db.String(30), default='Usuario'); permisos_json=db.Column(db.Text, default='[]'); activo=db.Column(db.Boolean, default=True)
    creado=db.Column(db.DateTime, default=datetime.utcnow); ultimo_acceso=db.Column(db.DateTime)
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)
    @property
    def es_admin(self):
        return (self.rol or '').strip().lower() in ('administrador','admin','administrator')
    @property
    def permisos(self):
        if self.es_admin: return list(PERMISOS.keys())
        try: return json.loads(self.permisos_json or '[]')
        except: return []
    def puede(self,p):
        # Compatibilidad con permisos de versiones anteriores.
        if self.es_admin: return True
        permisos=set(self.permisos)
        aliases={'usuarios':{'administracion'}, 'clientes':{'maestros'}}
        return p in permisos or bool(aliases.get(p,set()) & permisos)

class Auditoria(db.Model):
    id=db.Column(db.Integer, primary_key=True); fecha=db.Column(db.DateTime, default=datetime.utcnow)
    usuario=db.Column(db.String(120)); accion=db.Column(db.String(200)); detalle=db.Column(db.Text)

class Cliente(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    nombre=db.Column(db.String(120), unique=True, nullable=False) # razón social / nombre histórico
    nombre_comercial=db.Column(db.String(120))
    rut=db.Column(db.String(20), unique=True)
    direccion=db.Column(db.String(200)); comuna=db.Column(db.String(100)); ciudad=db.Column(db.String(100)); giro=db.Column(db.String(180))
    telefono=db.Column(db.String(60)); email=db.Column(db.String(140)); activo=db.Column(db.Boolean, default=True)
    contactos=db.relationship('ContactoCliente', backref='empresa', cascade='all, delete-orphan', lazy=True)

class ContactoCliente(db.Model):
    id=db.Column(db.Integer, primary_key=True); cliente_id=db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    nombre=db.Column(db.String(140), nullable=False); cargo=db.Column(db.String(120)); email=db.Column(db.String(140)); telefono=db.Column(db.String(60))
    recibe_cotizacion=db.Column(db.Boolean, default=True); puede_aprobar=db.Column(db.Boolean, default=False)
    recibe_diagnostico=db.Column(db.Boolean, default=True); recibe_informe_final=db.Column(db.Boolean, default=True); activo=db.Column(db.Boolean, default=True)
class ModeloEquipo(db.Model):
    id=db.Column(db.Integer, primary_key=True); tipo=db.Column(db.String(80), nullable=False); marca=db.Column(db.String(80), nullable=False); modelo=db.Column(db.String(80), nullable=False); activo=db.Column(db.Boolean, default=True)
    componentes=db.relationship('ComponenteModelo', backref='modelo_equipo', cascade='all, delete-orphan', lazy=True)
    __table_args__=(db.UniqueConstraint('tipo','marca','modelo',name='uq_equipo_modelo'),)
class ComponenteModelo(db.Model):
    id=db.Column(db.Integer, primary_key=True); modelo_id=db.Column(db.Integer, db.ForeignKey('modelo_equipo.id'), nullable=False); nombre=db.Column(db.String(100), nullable=False)
    codigo=db.Column(db.String(80)); categoria=db.Column(db.String(40), default='Componente reparable'); material_default=db.Column(db.String(80)); activo=db.Column(db.Boolean, default=True)

class OTComponente(db.Model):
    id=db.Column(db.Integer, primary_key=True); ot_id=db.Column(db.Integer, db.ForeignKey('ot.id'), nullable=False); componente_modelo_id=db.Column(db.Integer, db.ForeignKey('componente_modelo.id'))
    nombre=db.Column(db.String(120), nullable=False); codigo=db.Column(db.String(80)); categoria=db.Column(db.String(40), default='Componente reparable')
    condicion_ingreso=db.Column(db.String(30), default='No recibido'); resolucion=db.Column(db.String(40), default='Sin intervención')
    material=db.Column(db.String(80)); ubicacion=db.Column(db.String(120)); observacion=db.Column(db.Text)
    componente_modelo=db.relationship('ComponenteModelo')

class Cotizacion(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    numero=db.Column(db.String(30), unique=True, nullable=False)
    fecha=db.Column(db.DateTime, default=datetime.utcnow)
    validez_hasta=db.Column(db.Date)
    ot_id=db.Column(db.Integer, db.ForeignKey('ot.id'), nullable=False)
    cliente=db.Column(db.String(120), nullable=False)
    contacto=db.Column(db.String(120))
    moneda=db.Column(db.String(10), default='CLP')
    plazo_pago=db.Column(db.String(80), default='30 días')
    tiempo_entrega=db.Column(db.String(120))
    plazo_ejecucion_cantidad=db.Column(db.Integer)
    plazo_ejecucion_unidad=db.Column(db.String(30), default='Días hábiles')
    inicio_plazo=db.Column(db.String(120), default='Recepción de OC / aprobación')
    fecha_aprobacion=db.Column(db.DateTime)
    fecha_comprometida=db.Column(db.Date)
    referencia=db.Column(db.String(120))
    notas=db.Column(db.Text)
    estado=db.Column(db.String(30), default='Presupuesto')
    descuento_pct=db.Column(db.Float, default=0)
    anulada_motivo=db.Column(db.Text)
    anulada_fecha=db.Column(db.DateTime)
    anulada_por=db.Column(db.String(120))
    creada_por=db.Column(db.String(120))
    lineas=db.relationship('LineaCotizacion', backref='cotizacion', cascade='all, delete-orphan', lazy=True)
    @property
    def subtotal(self): return sum((l.cantidad or 0)*(l.precio_unitario or 0) for l in self.lineas)
    @property
    def descuento(self): return round(self.subtotal * max(0, min(self.descuento_pct or 0, 100)) / 100)
    @property
    def neto(self): return self.subtotal-self.descuento
    @property
    def iva(self): return round(self.neto*0.19)
    @property
    def total(self): return self.neto+self.iva

class LineaCotizacion(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    cotizacion_id=db.Column(db.Integer, db.ForeignKey('cotizacion.id'), nullable=False)
    descripcion=db.Column(db.String(250), nullable=False)
    cantidad=db.Column(db.Float, default=1)
    precio_unitario=db.Column(db.Integer, default=0)
    orden=db.Column(db.Integer, default=0)

class OT(db.Model):
    id=db.Column(db.Integer, primary_key=True); numero=db.Column(db.String(30), unique=True, nullable=False); fecha=db.Column(db.DateTime, default=datetime.utcnow)
    cliente=db.Column(db.String(120), nullable=False); equipo=db.Column(db.String(120), nullable=False); componente=db.Column(db.String(500), nullable=False)
    serie=db.Column(db.String(80)); guia=db.Column(db.String(80)); estado=db.Column(db.String(40), default='Diagnóstico'); diagnostico=db.Column(db.Text)
    cotizacion=db.Column(db.String(80)); aprobacion=db.Column(db.String(30), default='Pendiente'); reparacion=db.Column(db.Text); control_calidad=db.Column(db.Text)
    checklist=db.Column(db.String(120)); embalaje=db.Column(db.Text); despacho=db.Column(db.Text)
    fecha_comprometida=db.Column(db.Date)
    componentes_detalle=db.relationship('OTComponente', backref='ot', cascade='all, delete-orphan', lazy=True)
    @property
    def avance(self):
        estados=['Diagnóstico','Cotización enviada','Aprobada / Reparación','Control de calidad','Checklist / Embalaje','Despachada','Cerrada']
        try:return int((estados.index(self.estado)+1)/len(estados)*100)
        except:return 10

def usuario_actual(): return db.session.get(Usuario, session.get('user_id')) if session.get('user_id') else None
@app.context_processor
def inject_user(): return dict(usuario_actual=usuario_actual(), PERMISOS=PERMISOS, cotizacion_activa_ot=lambda ot_id: Cotizacion.query.filter(Cotizacion.ot_id==ot_id, Cotizacion.estado!='Anulada').order_by(Cotizacion.id.desc()).first())

def login_required(fn):
    @wraps(fn)
    def w(*a,**k):
        if Usuario.query.count()==0: return redirect(url_for('setup'))
        u=usuario_actual()
        if not u or not u.activo: session.clear(); return redirect(url_for('login'))
        return fn(*a,**k)
    return w

def permiso_required(p):
    def deco(fn):
        @wraps(fn)
        @login_required
        def w(*a,**k):
            if not usuario_actual().puede(p): abort(403)
            return fn(*a,**k)
        return w
    return deco

def audit(accion, detalle=''):
    u=usuario_actual(); db.session.add(Auditoria(usuario=u.nombre if u else 'Sistema', accion=accion, detalle=detalle)); db.session.commit()

def normalizar_rut(rut):
    raw=''.join(ch for ch in (rut or '').upper() if ch.isdigit() or ch=='K')
    if len(raw)<2: return ''
    return raw[:-1]+'-'+raw[-1]

def rut_valido(rut):
    r=normalizar_rut(rut)
    if '-' not in r: return False
    cuerpo,dv=r.split('-')
    if not cuerpo.isdigit() or dv not in '0123456789K': return False
    suma=0; factor=2
    for d in reversed(cuerpo):
        suma += int(d)*factor; factor = 2 if factor==7 else factor+1
    x=11-(suma%11); esperado='0' if x==11 else 'K' if x==10 else str(x)
    return dv==esperado

def formatear_rut(rut):
    r=normalizar_rut(rut)
    if '-' not in r: return rut or ''
    cuerpo,dv=r.split('-'); partes=[]
    while cuerpo: partes.insert(0,cuerpo[-3:]); cuerpo=cuerpo[:-3]
    return '.'.join(partes)+'-'+dv

def seed_maestros():
    if Cliente.query.count()==0:
        for n in ['SQM Nueva Victoria','SQM Salar','Cliente de prueba']: db.session.add(Cliente(nombre=n))
    if ModeloEquipo.query.count()==0:
        m=ModeloEquipo(tipo='Bomba centrífuga',marca='Vogel',modelo='P204/5')
        m.componentes=[ComponenteModelo(nombre=n) for n in ['Motor','Base','Acoplamiento','Tapa rodamiento lado transmisión','Tapa rodamiento lado impulsión','Cuerpo de rodamientos','Eje','Impulsor','Tuerca impulsor','Voluta','Descarga','Válvula check','Rodamiento lado transmisión','Rodamiento lado impulsión','Sello laberinto / Retén','Empaquetadura','O-rings']]; db.session.add(m)
    db.session.commit()

def sumar_plazo(fecha_base, cantidad, unidad):
    if not fecha_base or not cantidad: return None
    cantidad=int(cantidad)
    if unidad=='Semanas': return fecha_base + timedelta(weeks=cantidad)
    if unidad=='Días corridos': return fecha_base + timedelta(days=cantidad)
    # Días hábiles: lunes a viernes; feriados se podrán incorporar en una versión posterior.
    d=fecha_base; agregados=0
    while agregados<cantidad:
        d += timedelta(days=1)
        if d.weekday()<5: agregados += 1
    return d

def asegurar_columnas():
    # Migración ligera para instalaciones V4 existentes: create_all no agrega columnas nuevas.
    from sqlalchemy import inspect, text
    insp=inspect(db.engine)
    if 'cotizacion' in insp.get_table_names():
        cols={c['name'] for c in insp.get_columns('cotizacion')}
        defs={
          'plazo_ejecucion_cantidad':'INTEGER', 'plazo_ejecucion_unidad':'VARCHAR(30)',
          'inicio_plazo':'VARCHAR(120)', 'fecha_aprobacion':'TIMESTAMP', 'fecha_comprometida':'DATE',
          'descuento_pct':'FLOAT', 'anulada_motivo':'TEXT', 'anulada_fecha':'TIMESTAMP', 'anulada_por':'VARCHAR(120)'}
        for n,t in defs.items():
            if n not in cols: db.session.execute(text(f'ALTER TABLE cotizacion ADD COLUMN {n} {t}'))
    if 'ot' in insp.get_table_names():
        cols={c['name'] for c in insp.get_columns('ot')}
        if 'fecha_comprometida' not in cols: db.session.execute(text('ALTER TABLE ot ADD COLUMN fecha_comprometida DATE'))
    if 'cliente' in insp.get_table_names():
        cols={c['name'] for c in insp.get_columns('cliente')}
        defs={'nombre_comercial':'VARCHAR(120)','rut':'VARCHAR(20)','direccion':'VARCHAR(200)','comuna':'VARCHAR(100)','ciudad':'VARCHAR(100)','giro':'VARCHAR(180)','telefono':'VARCHAR(60)','email':'VARCHAR(140)'}
        for n,t in defs.items():
            if n not in cols: db.session.execute(text(f'ALTER TABLE cliente ADD COLUMN {n} {t}'))
        try: db.session.execute(text('CREATE UNIQUE INDEX IF NOT EXISTS uq_cliente_rut ON cliente (rut) WHERE rut IS NOT NULL'))
        except: pass
    if 'componente_modelo' in insp.get_table_names():
        cols={c['name'] for c in insp.get_columns('componente_modelo')}
        defs={'codigo':'VARCHAR(80)','categoria':'VARCHAR(40)','material_default':'VARCHAR(80)','activo':'BOOLEAN DEFAULT TRUE'}
        for n,t in defs.items():
            if n not in cols: db.session.execute(text(f'ALTER TABLE componente_modelo ADD COLUMN {n} {t}'))
    db.session.commit()

def next_quote_number():
    y=datetime.now().year; last=Cotizacion.query.filter(Cotizacion.numero.like(f'COT-{y}-%')).order_by(Cotizacion.id.desc()).first(); seq=int(last.numero.split('-')[-1])+1 if last else 1
    return f'COT-{y}-{seq:04d}'

def next_number():
    y=datetime.now().year; last=OT.query.filter(OT.numero.like(f'OT-{y}-%')).order_by(OT.id.desc()).first(); seq=int(last.numero.split('-')[-1])+1 if last else 1
    return f'OT-{y}-{seq:04d}'

@app.route('/setup',methods=['GET','POST'])
def setup():
    if Usuario.query.count()>0: return redirect(url_for('login'))
    if request.method=='POST':
        if len(request.form['password'])<8: flash('La contraseña debe tener al menos 8 caracteres.'); return render_template('setup.html')
        u=Usuario(username=request.form['username'].strip().lower(), nombre=request.form['nombre'].strip(), cargo='Administrador', rol='Administrador'); u.set_password(request.form['password'])
        db.session.add(u); db.session.commit(); session['user_id']=u.id; audit('Creación administrador inicial'); return redirect(url_for('index'))
    return render_template('setup.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if Usuario.query.count()==0:return redirect(url_for('setup'))
    if request.method=='POST':
        u=Usuario.query.filter_by(username=request.form['username'].strip().lower()).first()
        if u and u.activo and u.check_password(request.form['password']):
            session.clear(); session['user_id']=u.id; u.ultimo_acceso=datetime.utcnow(); db.session.commit(); audit('Inicio de sesión'); return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos.')
    return render_template('login.html')
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/')
@login_required
def index(): return render_template('index.html',ots=OT.query.order_by(OT.id.desc()).all())

@app.route('/usuarios')
@permiso_required('usuarios')
def usuarios(): return render_template('usuarios.html',usuarios=Usuario.query.order_by(Usuario.nombre).all())
@app.route('/usuarios/nuevo',methods=['GET','POST'])
@permiso_required('usuarios')
def usuario_nuevo():
    if request.method=='POST':
        username=request.form['username'].strip().lower()
        if Usuario.query.filter_by(username=username).first(): flash('Ese usuario ya existe.'); return render_template('usuario_form.html',permisos=PERMISOS)
        if len(request.form['password'])<8: flash('La contraseña debe tener al menos 8 caracteres.'); return render_template('usuario_form.html',permisos=PERMISOS)
        u=Usuario(username=username,nombre=request.form['nombre'].strip(),cargo=request.form.get('cargo','').strip(),rol=request.form.get('rol','Usuario'),permisos_json=json.dumps(request.form.getlist('permisos'))); u.set_password(request.form['password'])
        db.session.add(u); db.session.commit(); audit('Usuario creado',u.username); flash('Usuario creado correctamente.'); return redirect(url_for('usuarios'))
    return render_template('usuario_form.html',permisos=PERMISOS)
@app.route('/usuarios/<int:uid>/estado',methods=['POST'])
@permiso_required('usuarios')
def usuario_estado(uid):
    u=db.session.get(Usuario,uid) or abort(404)
    if u.id==usuario_actual().id: flash('No puedes desactivar tu propia cuenta.'); return redirect(url_for('usuarios'))
    u.activo=not u.activo; db.session.commit(); audit('Estado de usuario modificado',f'{u.username}: {u.activo}'); return redirect(url_for('usuarios'))

@app.route('/api/modelo/<int:modelo_id>/componentes')
@login_required
def componentes_modelo(modelo_id):
    m=db.session.get(ModeloEquipo,modelo_id) or abort(404); return jsonify([{'id':c.id,'nombre':c.nombre,'codigo':c.codigo or '','categoria':c.categoria or 'Componente reparable','material':c.material_default or ''} for c in m.componentes if c.activo is not False])
@app.route('/ot/nueva',methods=['GET','POST'])
@permiso_required('ingreso')
def nueva_ot():
    clientes=Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all(); modelos=ModeloEquipo.query.filter_by(activo=True).order_by(ModeloEquipo.tipo,ModeloEquipo.marca,ModeloEquipo.modelo).all()
    if request.method=='POST':
        cliente=db.session.get(Cliente,int(request.form['cliente_id'])) or abort(404); modelo=db.session.get(ModeloEquipo,int(request.form['modelo_id'])) or abort(404)
        recibidos=set(request.form.getlist('componentes_recibidos'))
        ot=OT(numero=next_number(),cliente=cliente.nombre,equipo=f'{modelo.tipo} {modelo.marca} {modelo.modelo}',componente='Pendiente detalle',serie=request.form.get('serie'),guia=request.form.get('guia'))
        db.session.add(ot); db.session.flush()
        nombres=[]
        for c in modelo.componentes:
            if c.activo is False: continue
            cond='Recibido' if str(c.id) in recibidos else 'No recibido'
            if cond=='Recibido': nombres.append(c.nombre)
            db.session.add(OTComponente(ot_id=ot.id,componente_modelo_id=c.id,nombre=c.nombre,codigo=c.codigo,categoria=c.categoria or 'Componente reparable',condicion_ingreso=cond,material=c.material_default))
        ot.componente=', '.join(nombres) if nombres else 'Sin componentes marcados como recibidos'
        db.session.commit(); audit('OT creada',ot.numero); flash(f'{ot.numero} creada correctamente'); return redirect(url_for('ver_ot',ot_id=ot.id))
    return render_template('nueva.html',clientes=clientes,modelos=modelos)
@app.route('/ot/<int:ot_id>',methods=['GET','POST'])
@login_required
def ver_ot(ot_id):
    ot=db.session.get(OT,ot_id) or abort(404)
    if request.method=='POST':
        for f in ['diagnostico','cotizacion','aprobacion','reparacion','control_calidad','checklist','embalaje','despacho','estado']:
            if f in request.form:setattr(ot,f,request.form.get(f))
        for c in ot.componentes_detalle:
            c.condicion_ingreso=request.form.get(f'condicion_{c.id}',c.condicion_ingreso)
            c.resolucion=request.form.get(f'resolucion_{c.id}',c.resolucion)
            c.material=request.form.get(f'material_{c.id}',c.material or '').strip()
            c.ubicacion=request.form.get(f'ubicacion_{c.id}',c.ubicacion or '').strip()
        db.session.commit(); audit('OT actualizada',ot.numero); flash('OT actualizada'); return redirect(url_for('ver_ot',ot_id=ot.id))
    return render_template('ot.html',ot=ot)


@app.route('/clientes')
@permiso_required('clientes')
def clientes(): return render_template('clientes.html',clientes=Cliente.query.order_by(Cliente.nombre).all())

@app.route('/clientes/nuevo',methods=['GET','POST'])
@permiso_required('clientes')
def cliente_nuevo():
    if request.method=='POST':
        rut=normalizar_rut(request.form.get('rut'))
        if not rut_valido(rut): flash('RUT inválido. Revisa el dígito verificador.'); return render_template('cliente_form.html',cliente=None)
        existente=Cliente.query.filter_by(rut=rut).first()
        if existente: flash(f'El RUT {formatear_rut(rut)} ya está registrado en {existente.nombre}.'); return redirect(url_for('cliente_ver',cid=existente.id))
        c=Cliente(nombre=request.form['nombre'].strip(),nombre_comercial=request.form.get('nombre_comercial','').strip(),rut=rut,direccion=request.form.get('direccion','').strip(),comuna=request.form.get('comuna','').strip(),ciudad=request.form.get('ciudad','').strip(),giro=request.form.get('giro','').strip(),telefono=request.form.get('telefono','').strip(),email=request.form.get('email','').strip())
        db.session.add(c); db.session.commit(); audit('Cliente creado',f'{c.nombre} / {c.rut}'); return redirect(url_for('cliente_ver',cid=c.id))
    return render_template('cliente_form.html',cliente=None)

@app.route('/clientes/<int:cid>',methods=['GET','POST'])
@permiso_required('clientes')
def cliente_ver(cid):
    c=db.session.get(Cliente,cid) or abort(404)
    if request.method=='POST':
        if request.form.get('accion')=='contacto':
            x=ContactoCliente(cliente_id=c.id,nombre=request.form['contacto_nombre'].strip(),cargo=request.form.get('cargo','').strip(),email=request.form.get('contacto_email','').strip(),telefono=request.form.get('contacto_telefono','').strip(),recibe_cotizacion=bool(request.form.get('recibe_cotizacion')),puede_aprobar=bool(request.form.get('puede_aprobar')),recibe_diagnostico=bool(request.form.get('recibe_diagnostico')),recibe_informe_final=bool(request.form.get('recibe_informe_final')))
            db.session.add(x); db.session.commit(); audit('Contacto cliente creado',f'{c.nombre}: {x.nombre}'); flash('Contacto agregado.')
        return redirect(url_for('cliente_ver',cid=c.id))
    return render_template('cliente_ver.html',cliente=c,formatear_rut=formatear_rut)

@app.route('/maestros/equipos',methods=['GET','POST'])
@permiso_required('maestros')
def maestros_equipos():
    if request.method=='POST':
        m=ModeloEquipo(tipo=request.form['tipo'].strip(),marca=request.form['marca'].strip(),modelo=request.form['modelo'].strip())
        db.session.add(m); db.session.commit(); audit('Modelo de equipo creado',f'{m.marca} {m.modelo}'); return redirect(url_for('maestro_modelo',mid=m.id))
    return render_template('maestros_equipos.html',modelos=ModeloEquipo.query.order_by(ModeloEquipo.marca,ModeloEquipo.modelo).all())

@app.route('/maestros/equipos/<int:mid>',methods=['GET','POST'])
@permiso_required('maestros')
def maestro_modelo(mid):
    m=db.session.get(ModeloEquipo,mid) or abort(404)
    if request.method=='POST':
        c=ComponenteModelo(modelo_id=m.id,nombre=request.form['nombre'].strip(),codigo=request.form.get('codigo','').strip(),categoria=request.form.get('categoria','Componente reparable'),material_default=request.form.get('material_default','').strip())
        db.session.add(c); db.session.commit(); audit('Componente de modelo creado',f'{m.marca} {m.modelo}: {c.nombre}'); flash('Componente agregado al despiece.'); return redirect(url_for('maestro_modelo',mid=m.id))
    return render_template('maestro_modelo.html',modelo=m)

def cotizacion_activa_ot(ot_id):
    return Cotizacion.query.filter(Cotizacion.ot_id==ot_id, Cotizacion.estado!='Anulada').order_by(Cotizacion.id.desc()).first()

def cargar_cotizacion_form(q, form):
    q.contacto=form.get('contacto','').strip(); q.plazo_pago=form.get('plazo_pago','30 días').strip()
    q.referencia=form.get('referencia','').strip(); q.notas=form.get('notas','').strip()
    q.plazo_ejecucion_cantidad=int(form.get('plazo_ejecucion_cantidad') or 0)
    q.plazo_ejecucion_unidad=form.get('plazo_ejecucion_unidad','Días hábiles')
    q.inicio_plazo=form.get('inicio_plazo','Recepción de OC / aprobación').strip()
    try: q.descuento_pct=max(0,min(float(form.get('descuento_pct') or 0),100))
    except: q.descuento_pct=0
    vh=form.get('validez_hasta'); q.validez_hasta=datetime.strptime(vh,'%Y-%m-%d').date() if vh else None
    q.lineas.clear(); db.session.flush()
    descs=form.getlist('descripcion[]'); cants=form.getlist('cantidad[]'); precios=form.getlist('precio[]')
    for i,desc in enumerate(descs):
        if not desc.strip(): continue
        try: cant=float(cants[i] or 1); precio=int(float(precios[i] or 0))
        except: cant,precio=1,0
        q.lineas.append(LineaCotizacion(descripcion=desc.strip(),cantidad=cant,precio_unitario=precio,orden=i))

@app.route('/cotizaciones')
@permiso_required('cotizaciones')
def cotizaciones():
    qs=Cotizacion.query.order_by(Cotizacion.id.desc()).all()
    return render_template('cotizaciones.html',cotizaciones=qs)

@app.route('/ot/<int:ot_id>/cotizacion/nueva', methods=['GET','POST'])
@permiso_required('cotizaciones')
def cotizacion_nueva(ot_id):
    ot=db.session.get(OT,ot_id) or abort(404)
    activa=cotizacion_activa_ot(ot.id)
    if activa:
        flash(f'Esta OT ya tiene una cotización activa: {activa.numero}.')
        return redirect(url_for('ver_cotizacion',qid=activa.id))
    if request.method=='POST':
        q=Cotizacion(numero=next_quote_number(),ot_id=ot.id,cliente=ot.cliente,creada_por=usuario_actual().nombre)
        cargar_cotizacion_form(q,request.form); db.session.add(q); db.session.commit()
        ot.cotizacion=q.numero
        if request.form.get('accion')=='enviar': q.estado='Presupuesto enviado'; ot.estado='Cotización enviada'
        db.session.commit(); audit('Cotización creada',f'{q.numero} / {ot.numero}'); flash(f'{q.numero} creada correctamente')
        return redirect(url_for('ver_cotizacion',qid=q.id))
    sugerencias=[f'REPARACIÓN {x.strip().upper()}' for x in ot.componente.split(',')] if ot.componente and ot.componente!='Bomba completa' else ['REPARACIÓN BOMBA COMPLETA']
    return render_template('cotizacion_form.html',ot=ot,sugerencias=sugerencias,q=None,modo='nueva')

@app.route('/cotizacion/<int:qid>')
@permiso_required('cotizaciones')
def ver_cotizacion(qid):
    q=db.session.get(Cotizacion,qid) or abort(404)
    return render_template('cotizacion_ver.html',q=q,ot=db.session.get(OT,q.ot_id))

@app.route('/cotizacion/<int:qid>/editar',methods=['GET','POST'])
@permiso_required('cotizaciones')
def editar_cotizacion(qid):
    q=db.session.get(Cotizacion,qid) or abort(404); ot=db.session.get(OT,q.ot_id)
    if q.estado=='Anulada': flash('Una cotización anulada no puede modificarse.'); return redirect(url_for('ver_cotizacion',qid=q.id))
    if request.method=='POST':
        cargar_cotizacion_form(q,request.form)
        if request.form.get('accion')=='enviar': q.estado='Presupuesto enviado'; ot.estado='Cotización enviada'
        db.session.commit(); audit('Cotización editada',q.numero); flash('Cotización actualizada correctamente.')
        return redirect(url_for('ver_cotizacion',qid=q.id))
    return render_template('cotizacion_form.html',ot=ot,sugerencias=[],q=q,modo='editar')

@app.route('/cotizacion/<int:qid>/anular',methods=['POST'])
@permiso_required('cotizaciones')
def anular_cotizacion(qid):
    q=db.session.get(Cotizacion,qid) or abort(404); motivo=request.form.get('motivo','').strip()
    if not motivo: flash('Debes indicar el motivo de anulación.'); return redirect(url_for('ver_cotizacion',qid=q.id))
    q.estado='Anulada'; q.anulada_motivo=motivo; q.anulada_fecha=datetime.utcnow(); q.anulada_por=usuario_actual().nombre
    ot=db.session.get(OT,q.ot_id); ot.cotizacion=None; ot.aprobacion='Pendiente'
    db.session.commit(); audit('Cotización anulada',f'{q.numero}: {motivo}'); flash(f'{q.numero} quedó ANULADA. Ya puedes crear una nueva cotización para la OT.')
    return redirect(url_for('ver_ot',ot_id=ot.id))

@app.route('/cotizacion/<int:qid>/estado', methods=['POST'])
@permiso_required('cotizaciones')
def cotizacion_estado(qid):
    q=db.session.get(Cotizacion,qid) or abort(404); nuevo=request.form.get('estado')
    if q.estado=='Anulada': return redirect(url_for('ver_cotizacion',qid=q.id))
    if nuevo in ['Presupuesto','Presupuesto enviado','Aprobada','Rechazada']:
        q.estado=nuevo; ot=db.session.get(OT,q.ot_id)
        if nuevo=='Aprobada':
            ot.aprobacion='Aprobada'; ot.estado='Aprobada / Reparación'; q.fecha_aprobacion=datetime.utcnow(); q.fecha_comprometida=sumar_plazo(date.today(),q.plazo_ejecucion_cantidad,q.plazo_ejecucion_unidad); ot.fecha_comprometida=q.fecha_comprometida
        elif nuevo=='Rechazada': ot.aprobacion='Rechazada'
        elif nuevo=='Presupuesto enviado': ot.estado='Cotización enviada'
        db.session.commit(); audit('Estado cotización',f'{q.numero}: {nuevo}')
    return redirect(url_for('ver_cotizacion',qid=q.id))

@app.route('/cotizacion/<int:qid>/pdf')
@permiso_required('cotizaciones')
def cotizacion_pdf(qid):
    q=db.session.get(Cotizacion,qid) or abort(404); ot=db.session.get(OT,q.ot_id)
    buf=BytesIO(); doc=SimpleDocTemplate(buf,pagesize=A4,rightMargin=28,leftMargin=28,topMargin=28,bottomMargin=28)
    styles=getSampleStyleSheet(); story=[]
    title=ParagraphStyle('t',parent=styles['Title'],fontSize=22,textColor=colors.HexColor('#0b6596'),alignment=TA_RIGHT)
    logo_path=os.path.join(app.root_path,'static','img','logo-ingepro.png')
    logo=Image(logo_path,width=170,height=70) if os.path.exists(logo_path) else Paragraph('<b>INGEPRO</b>',styles['Heading1'])
    cab=Table([[logo,Paragraph(f'<b>DIVISIÓN MAESTRANZA</b><br/><font size="16">Presupuesto {q.numero}</font>',title)]],colWidths=[220,290]); cab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LINEBELOW',(0,0),(-1,-1),2,colors.HexColor('#0b6596')),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story += [cab,Spacer(1,14)]
    meta=[[Paragraph('<b>Cliente</b>',styles['BodyText']),q.cliente],[Paragraph('<b>OT</b>',styles['BodyText']),ot.numero],[Paragraph('<b>Equipo</b>',styles['BodyText']),ot.equipo],[Paragraph('<b>Fecha</b>',styles['BodyText']),q.fecha.strftime('%d/%m/%Y')],[Paragraph('<b>Validez</b>',styles['BodyText']),q.validez_hasta.strftime('%d/%m/%Y') if q.validez_hasta else '-'],[Paragraph('<b>Tiempo de ejecución</b>',styles['BodyText']),f'{q.plazo_ejecucion_cantidad or "-"} {q.plazo_ejecucion_unidad or ""}']]
    mt=Table(meta,colWidths=[120,390]); mt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.lightgrey),('BACKGROUND',(0,0),(0,-1),colors.HexColor('#eef3f7')),('PADDING',(0,0),(-1,-1),6)])); story += [mt,Spacer(1,14)]
    data=[['DESCRIPCIÓN','CANT.','PRECIO UNITARIO','SUBTOTAL']]
    for l in q.lineas: data.append([Paragraph(l.descripcion,styles['BodyText']),f'{l.cantidad:g}',f'$ {l.precio_unitario:,.0f}'.replace(',','.'),f'$ {l.cantidad*l.precio_unitario:,.0f}'.replace(',','.')])
    t=Table(data,colWidths=[270,55,95,90],repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0b6596')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.grey),('ALIGN',(1,1),(-1,-1),'RIGHT'),('PADDING',(0,0),(-1,-1),6)])); story += [t,Spacer(1,10)]
    totals=[['Subtotal',f'$ {q.subtotal:,.0f}'.replace(',','.')], [f'Descuento {q.descuento_pct or 0:g}%',f'- $ {q.descuento:,.0f}'.replace(',','.')],['Neto',f'$ {q.neto:,.0f}'.replace(',','.')],['IVA 19%',f'$ {q.iva:,.0f}'.replace(',','.')],['TOTAL',f'$ {q.total:,.0f}'.replace(',','.')]]
    tt=Table(totals,colWidths=[120,120],hAlign='RIGHT'); tt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.4,colors.grey),('ALIGN',(1,0),(1,-1),'RIGHT'),('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#0b6596')),('TEXTCOLOR',(0,-1),(-1,-1),colors.white),('PADDING',(0,0),(-1,-1),6)])); story += [tt,Spacer(1,14)]
    story += [Paragraph(f'<b>Condiciones de pago:</b> {q.plazo_pago}',styles['BodyText']),Paragraph(f'<b>Inicio del plazo:</b> {q.inicio_plazo}',styles['BodyText'])]
    if q.referencia: story.append(Paragraph(f'<b>Referencia:</b> {q.referencia}',styles['BodyText']))
    if q.notas: story.append(Paragraph(f'<b>Notas:</b> {q.notas}',styles['BodyText']))
    if q.estado=='Anulada': story.append(Paragraph('<b>COTIZACIÓN ANULADA</b>',styles['Heading2']))
    doc.build(story); buf.seek(0)
    audit('PDF cotización generado',q.numero)
    return send_file(buf,mimetype='application/pdf',as_attachment=True,download_name=f'{q.numero}.pdf')

with app.app_context(): db.create_all(); asegurar_columnas(); seed_maestros()
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=True)
