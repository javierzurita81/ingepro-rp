import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','ingepro-demo')
db_url = os.environ.get('DATABASE_URL', 'sqlite:///ingepro.db')
if db_url.startswith('postgres://'):
    db_url = db_url.replace('postgres://','postgresql://',1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class OT(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    numero=db.Column(db.String(30), unique=True, nullable=False)
    fecha=db.Column(db.DateTime, default=datetime.utcnow)
    cliente=db.Column(db.String(120), nullable=False)
    equipo=db.Column(db.String(120), nullable=False)
    componente=db.Column(db.String(120), nullable=False)
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

def next_number():
    year=datetime.now().year
    last=OT.query.filter(OT.numero.like(f'OT-{year}-%')).order_by(OT.id.desc()).first()
    seq=(int(last.numero.split('-')[-1])+1) if last else 1
    return f'OT-{year}-{seq:04d}'

@app.route('/')
def index():
    ots=OT.query.order_by(OT.id.desc()).all()
    return render_template('index.html', ots=ots)

@app.route('/ot/nueva', methods=['GET','POST'])
def nueva_ot():
    if request.method=='POST':
        ot=OT(numero=next_number(), cliente=request.form['cliente'], equipo=request.form['equipo'], componente=request.form['componente'], serie=request.form.get('serie'), guia=request.form.get('guia'))
        db.session.add(ot); db.session.commit()
        flash(f'{ot.numero} creada correctamente')
        return redirect(url_for('ver_ot', ot_id=ot.id))
    return render_template('nueva.html')

@app.route('/ot/<int:ot_id>', methods=['GET','POST'])
def ver_ot(ot_id):
    ot=OT.query.get_or_404(ot_id)
    if request.method=='POST':
        for f in ['diagnostico','cotizacion','aprobacion','reparacion','control_calidad','checklist','embalaje','despacho','estado']:
            if f in request.form: setattr(ot,f,request.form.get(f))
        db.session.commit(); flash('OT actualizada')
        return redirect(url_for('ver_ot', ot_id=ot.id))
    return render_template('ot.html', ot=ot)

with app.app_context(): db.create_all()

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)), debug=True)
