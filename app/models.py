from app import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='cadastrador')

class SystemStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.String(500), default="Sistema em manutenção. Por favor, tente novamente mais tarde.")
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Municipio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    estado = db.relationship('Estado', backref='municipios')

class Estado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

class Descricao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class instituicao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Atendente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Cadastro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.String(20), default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    telefone = db.Column(db.String(15), nullable=True)
    assentamento = db.Column(db.String(255), nullable=True)
    municipio_id = db.Column(db.Integer, db.ForeignKey('municipio.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    descricao_id = db.Column(db.Integer, db.ForeignKey('descricao.id'), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)
    atendente_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    atendida = db.Column(db.Boolean, default=False, nullable=False)
    municipio = db.relationship('Municipio', backref='cadastros')
    estado = db.relationship('Estado', backref='cadastros')
    descricao = db.relationship('Descricao', backref='cadastros')
    instituicao = db.relationship('instituicao', backref='cadastros')
    atendente = db.relationship('User', backref='cadastros')

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.String(20), default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    usuario = db.Column(db.String(100), nullable=False)
    acao = db.Column(db.String(255), nullable=False)
