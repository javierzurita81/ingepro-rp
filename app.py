import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','ingepro-demo')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///ingepro.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://','postgresql://',1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), unique=True, nullable=False)
    activo = db.Column(db.Boolean, default=True)

class ModeloEquipo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(80), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    modelo = db.Column(db.String(80), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    componentes = db.relationship('ComponenteModelo', backref='modelo_equipo', cascade='all, delete-orphan', lazy=True)
    __table_args__ = (db.UniqueConstraint('tipo','marca','modelo', name='uq_equipo_modelo'),)

class ComponenteModelo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modelo_id = db.Column(db.Integer, db.ForeignKey('modelo_equipo.id'), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)

class OT(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    numero=db.Column(db.String(30), unique=True, nullable=False)
    fecha=db.Column(db.DateTime, default=datetime.utcnow)
    cliente=db.Column(db.String(120), nullable=False)
    equipo=db.Column(db.String(120), nullable=False)
    componente=db.Column(db.String(500), nullable=False)
    serie=db.Column(db.String(80))
    guia=db.Column(db.String(80))
    estado=db.Column(db.String(40), default='Diagnóstico')
    diagnostico=db.Column(db.Text)
    cotizacion=db.Column(db.String(80))
    aprobacion=db.Column(db.String(30), default='Pendiente')
    reparacion=db.Column(db.Text)
    control_calidad=db.Column(db.Text)
    checklist=db.Column(db.String(120))
    embalaje=db.Column(db.Text)
    despacho=db.Column(db.Text)

    @property
    def avance(self):
        estados=['Diagnóstico','Cotización enviada','Aprobada / Reparación','Control de calidad','Checklist / Embalaje','Despachada','Cerrada']
        try: return int((estados.index(self.estado)+1)/len(estados)*100)
        except: return 10

def seed_maestros():
    if Cliente.query.count() == 0:
        for nombre in ['SQM Nueva Victoria', 'SQM Salar', 'Cliente de prueba']:
            db.session.add(Cliente(nombre=nombre))
    if ModeloEquipo.query.count() == 0:
        vogel = ModeloEquipo(tipo='Bomba centrífuga', marca='Vogel', modelo='P204/5')
        vogel.componentes = [ComponenteModelo(nombre=n) for n in ['Eje','Cuerpo de rodamientos','Impulsor','Voluta','Frame adapter']]
        db.session.add(vogel)
    db.session.commit()

def next_number():
    year=datetime.now().year
    last=OT.query.filter(OT.numero.like(f'OT-{year}-%')).order_by(OT.id.desc()).first()
    seq=(int(last.numero.split('-')[-1])+1) if last else 1
    return f'OT-{year}-{seq:04d}'

@app.route('/')
def index():
    ots=OT.query.order_by(OT.id.desc()).all()
    return render_template('index.html', ots=ots)

@app.route('/api/modelo/<int:modelo_id>/componentes')
def componentes_modelo(modelo_id):
    modelo = ModeloEquipo.query.get_or_404(modelo_id)
    return jsonify([{'id': c.id, 'nombre': c.nombre} for c in modelo.componentes])

@app.route('/ot/nueva', methods=['GET','POST'])
def nueva_ot():
    clientes = Cliente.query.filter_by(activo=True).order_by(Cliente.nombre).all()
    modelos = ModeloEquipo.query.filter_by(activo=True).order_by(ModeloEquipo.tipo, ModeloEquipo.marca, ModeloEquipo.modelo).all()
    if request.method=='POST':
        cliente = Cliente.query.get_or_404(int(request.form['cliente_id']))
        modelo = ModeloEquipo.query.get_or_404(int(request.form['modelo_id']))
        recepcion = request.form.get('recepcion','Completa')
        seleccion = request.form.getlist('componentes')
        if recepcion == 'Completa':
            componente = 'Bomba completa'
        else:
            if not seleccion:
                flash('Debes seleccionar al menos un componente cuando la recepción es parcial.')
                return render_template('nueva.html', clientes=clientes, modelos=modelos)
            componente = ', '.join(seleccion)
        equipo = f'{modelo.tipo} {modelo.marca} {modelo.modelo}'
        ot=OT(numero=next_number(), cliente=cliente.nombre, equipo=equipo, componente=componente, serie=request.form.get('serie'), guia=request.form.get('guia'))
        db.session.add(ot); db.session.commit()
        flash(f'{ot.numero} creada correctamente')
        return redirect(url_for('ver_ot', ot_id=ot.id))
    return render_template('nueva.html', clientes=clientes, modelos=modelos)

@app.route('/ot/<int:ot_id>', methods=['GET','POST'])
def ver_ot(ot_id):
    ot=OT.query.get_or_404(ot_id)
    if request.method=='POST':
        for f in ['diagnostico','cotizacion','aprobacion','reparacion','control_calidad','checklist','embalaje','despacho','estado']:
            if f in request.form: setattr(ot,f,request.form.get(f))
        db.session.commit(); flash('OT actualizada')
        return redirect(url_for('ver_ot', ot_id=ot.id))
    return render_template('ot.html', ot=ot)

with app.app_context():
    db.create_all()
    seed_maestros()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
