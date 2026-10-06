import os, json
from datetime import datetime, date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

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
 'informes':'Informes', 'maestros':'Maestros', 'usuarios':'Administración de usuarios'
}

class Usuario(db.Model):
    id=db.Column(db.Integer, primary_key=True); username=db.Column(db.String(60), unique=True, nullable=False)
    nombre=db.Column(db.String(120), nullable=False); cargo=db.Column(db.String(100)); password_hash=db.Column(db.String(255), nullable=False)
    rol=db.Column(db.String(30), default='Usuario'); permisos_json=db.Column(db.Text, default='[]'); activo=db.Column(db.Boolean, default=True)
    creado=db.Column(db.DateTime, default=datetime.utcnow); ultimo_acceso=db.Column(db.DateTime)
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)
    @property
    def permisos(self):
        if self.rol=='Administrador': return list(PERMISOS.keys())
        try: return json.loads(self.permisos_json or '[]')
        except: return []
    def puede(self,p): return self.rol=='Administrador' or p in self.permisos

class Auditoria(db.Model):
    id=db.Column(db.Integer, primary_key=True); fecha=db.Column(db.DateTime, default=datetime.utcnow)
    usuario=db.Column(db.String(120)); accion=db.Column(db.String(200)); detalle=db.Column(db.Text)

class Cliente(db.Model):
    id=db.Column(db.Integer, primary_key=True); nombre=db.Column(db.String(120), unique=True, nullable=False); activo=db.Column(db.Boolean, default=True)
class ModeloEquipo(db.Model):
    id=db.Column(db.Integer, primary_key=True); tipo=db.Column(db.String(80), nullable=False); marca=db.Column(db.String(80), nullable=False); modelo=db.Column(db.String(80), nullable=False); activo=db.Column(db.Boolean, default=True)
    componentes=db.relationship('ComponenteModelo', backref='modelo_equipo', cascade='all, delete-orphan', lazy=True)
    __table_args__=(db.UniqueConstraint('tipo','marca','modelo',name='uq_equipo_modelo'),)
class ComponenteModelo(db.Model):
    id=db.Column(db.Integer, primary_key=True); modelo_id=db.Column(db.Integer, db.ForeignKey('modelo_equipo.id'), nullable=False); nombre=db.Column(db.String(100), nullable=False)

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
    creada_por=db.Column(db.String(120))
    lineas=db.relationship('LineaCotizacion', backref='cotizacion', cascade='all, delete-orphan', lazy=True)
    @property
    def subtotal(self): return sum((l.cantidad or 0)*(l.precio_unitario or 0) for l in self.lineas)
    @property
    def iva(self): return round(self.subtotal*0.19)
    @property
    def total(self): return self.subtotal+self.iva

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
    @property
    def avance(self):
        estados=['Diagnóstico','Cotización enviada','Aprobada / Reparación','Control de calidad','Checklist / Embalaje','Despachada','Cerrada']
        try:return int((estados.index(self.estado)+1)/len(estados)*100)
        except:return 10

def usuario_actual(): return db.session.get(Usuario, session.get('user_id')) if session.get('user_id') else None
@app.context_processor
def inject_user(): return dict(usuario_actual=usuario_actual(), PERMISOS=PERMISOS)

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

def seed_maestros():
    if Cliente.query.count()==0:
        for n in ['SQM Nueva Victoria','SQM Salar','Cliente de prueba']: db.session.add(Cliente(nombre=n))
    if ModeloEquipo.query.count()==0:
        m=ModeloEquipo(tipo='Bomba centrífuga',marca='Vogel',modelo='P204/5')
        m.componentes=[ComponenteModelo(nombre=n) for n in ['Eje','Cuerpo de rodamientos','Impulsor','Voluta','Frame adapter']]; db.session.add(m)
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
          'inicio_plazo':'VARCHAR(120)', 'fecha_aprobacion':'TIMESTAMP', 'fecha_comprometida':'DATE'}
        for n,t in defs.items():
            if n not in cols: db.session.execute(text(f'ALTER TABLE cotizacion ADD COLUMN {n} {t}'))
    if 'ot' in insp.get_table_names():
        cols={c['name'] for c in insp.get_columns('ot')}
        if 'fecha_comprometida' not in cols: db.session.execute(text('ALTER TABLE ot ADD COLUMN fecha_comprometida DATE'))
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
    m=db.session.get(ModeloEquipo,modelo_id) or abort(404); return jsonify([{'id':c.id,'nombre':c.nombre} for c in m.componentes])
@app.route('/ot/nueva',methods=['GET','POST'])
@permiso_required('ingreso')
def nueva_ot():
    clientes=Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all(); modelos=ModeloEquipo.query.filter_by(activo=True).order_by(ModeloEquipo.tipo,ModeloEquipo.marca,ModeloEquipo.modelo).all()
    if request.method=='POST':
        cliente=db.session.get(Cliente,int(request.form['cliente_id'])) or abort(404); modelo=db.session.get(ModeloEquipo,int(request.form['modelo_id'])) or abort(404); recepcion=request.form.get('recepcion','Completa'); sel=request.form.getlist('componentes')
        if recepcion=='Completa': componente='Bomba completa'
        elif not sel: flash('Debes seleccionar al menos un componente.'); return render_template('nueva.html',clientes=clientes,modelos=modelos)
        else: componente=', '.join(sel)
        ot=OT(numero=next_number(),cliente=cliente.nombre,equipo=f'{modelo.tipo} {modelo.marca} {modelo.modelo}',componente=componente,serie=request.form.get('serie'),guia=request.form.get('guia'))
        db.session.add(ot); db.session.commit(); audit('OT creada',ot.numero); flash(f'{ot.numero} creada correctamente'); return redirect(url_for('ver_ot',ot_id=ot.id))
    return render_template('nueva.html',clientes=clientes,modelos=modelos)
@app.route('/ot/<int:ot_id>',methods=['GET','POST'])
@login_required
def ver_ot(ot_id):
    ot=db.session.get(OT,ot_id) or abort(404)
    if request.method=='POST':
        for f in ['diagnostico','cotizacion','aprobacion','reparacion','control_calidad','checklist','embalaje','despacho','estado']:
            if f in request.form:setattr(ot,f,request.form.get(f))
        db.session.commit(); audit('OT actualizada',ot.numero); flash('OT actualizada'); return redirect(url_for('ver_ot',ot_id=ot.id))
    return render_template('ot.html',ot=ot)


@app.route('/cotizaciones')
@permiso_required('cotizaciones')
def cotizaciones():
    qs=Cotizacion.query.order_by(Cotizacion.id.desc()).all()
    return render_template('cotizaciones.html',cotizaciones=qs)

@app.route('/ot/<int:ot_id>/cotizacion/nueva', methods=['GET','POST'])
@permiso_required('cotizaciones')
def cotizacion_nueva(ot_id):
    ot=db.session.get(OT,ot_id) or abort(404)
    if request.method=='POST':
        from datetime import date
        q=Cotizacion(numero=next_quote_number(), ot_id=ot.id, cliente=ot.cliente,
            contacto=request.form.get('contacto','').strip(), plazo_pago=request.form.get('plazo_pago','30 días').strip(),
            tiempo_entrega=request.form.get('tiempo_entrega','').strip(), referencia=request.form.get('referencia','').strip(),
            plazo_ejecucion_cantidad=int(request.form.get('plazo_ejecucion_cantidad') or 0),
            plazo_ejecucion_unidad=request.form.get('plazo_ejecucion_unidad','Días hábiles'),
            inicio_plazo=request.form.get('inicio_plazo','Recepción de OC / aprobación').strip(),
            notas=request.form.get('notas','').strip(), creada_por=usuario_actual().nombre)
        vh=request.form.get('validez_hasta')
        if vh: q.validez_hasta=datetime.strptime(vh,'%Y-%m-%d').date()
        db.session.add(q); db.session.flush()
        descs=request.form.getlist('descripcion[]'); cants=request.form.getlist('cantidad[]'); precios=request.form.getlist('precio[]')
        for i,desc in enumerate(descs):
            if not desc.strip(): continue
            try: cant=float(cants[i] or 1); precio=int(float(precios[i] or 0))
            except: cant,precio=1,0
            db.session.add(LineaCotizacion(cotizacion_id=q.id,descripcion=desc.strip(),cantidad=cant,precio_unitario=precio,orden=i))
        db.session.commit(); ot.cotizacion=q.numero; ot.estado='Cotización enviada' if request.form.get('accion')=='enviar' else 'Diagnóstico';
        if request.form.get('accion')=='enviar': q.estado='Presupuesto enviado'
        db.session.commit(); audit('Cotización creada',f'{q.numero} / {ot.numero}'); flash(f'{q.numero} creada correctamente'); return redirect(url_for('ver_cotizacion',qid=q.id))
    sugerencias=[]
    if ot.componente and ot.componente!='Bomba completa': sugerencias=[f'REPARACIÓN {x.strip().upper()}' for x in ot.componente.split(',')]
    elif ot.componente=='Bomba completa': sugerencias=['REPARACIÓN BOMBA COMPLETA']
    return render_template('cotizacion_form.html',ot=ot,sugerencias=sugerencias)

@app.route('/cotizacion/<int:qid>')
@permiso_required('cotizaciones')
def ver_cotizacion(qid):
    q=db.session.get(Cotizacion,qid) or abort(404)
    return render_template('cotizacion_ver.html',q=q,ot=db.session.get(OT,q.ot_id))

@app.route('/cotizacion/<int:qid>/estado', methods=['POST'])
@permiso_required('cotizaciones')
def cotizacion_estado(qid):
    q=db.session.get(Cotizacion,qid) or abort(404); nuevo=request.form.get('estado')
    if nuevo in ['Presupuesto','Presupuesto enviado','Aprobada','Rechazada']:
        q.estado=nuevo; ot=db.session.get(OT,q.ot_id)
        if nuevo=='Aprobada':
            ot.aprobacion='Aprobada'; ot.estado='Aprobada / Reparación'; q.fecha_aprobacion=datetime.utcnow(); q.fecha_comprometida=sumar_plazo(date.today(),q.plazo_ejecucion_cantidad,q.plazo_ejecucion_unidad); ot.fecha_comprometida=q.fecha_comprometida
        elif nuevo=='Rechazada': ot.aprobacion='Rechazada'
        elif nuevo=='Presupuesto enviado': ot.estado='Cotización enviada'
        db.session.commit(); audit('Estado cotización',f'{q.numero}: {nuevo}')
    return redirect(url_for('ver_cotizacion',qid=q.id))

with app.app_context(): db.create_all(); asegurar_columnas(); seed_maestros()
if __name__=='__main__': app.run(host='0.0.0.0',port=int(os.environ.get('PORT',5000)),debug=True)
