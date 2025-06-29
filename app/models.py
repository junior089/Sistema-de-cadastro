from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Template literals for reuse
DEFAULT_ROLE = 'cadastrador'
DEFAULT_MAINTENANCE_MSG = "Sistema em manutenção. Por favor, tente novamente mais tarde."

class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=DEFAULT_ROLE)
    cadastros = db.relationship('Cadastro', back_populates='atendente', cascade="all, delete-orphan")

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class SystemStatus(db.Model):
    """System maintenance status and message."""
    id = db.Column(db.Integer, primary_key=True)
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.String(500), default=DEFAULT_MAINTENANCE_MSG)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))

class Municipio(db.Model):
    """Municipality entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    estado = db.relationship('Estado', back_populates='municipios')
    cadastros = db.relationship('Cadastro', back_populates='municipio')

class Estado(db.Model):
    """State entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    municipios = db.relationship('Municipio', back_populates='estado')
    cadastros = db.relationship('Cadastro', back_populates='estado')

class Descricao(db.Model):
    """Description entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cadastros = db.relationship('Cadastro', back_populates='descricao')

class Instituicao(db.Model):
    """Institution entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cadastros = db.relationship('Cadastro', back_populates='instituicao')

class Atendente(db.Model):
    """Attendant entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)

class Cadastro(db.Model):
    """Registration entity."""
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    telefone = db.Column(db.String(15), nullable=True)
    assentamento = db.Column(db.String(255), nullable=True)
    municipio_id = db.Column(db.Integer, db.ForeignKey('municipio.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    descricao_id = db.Column(db.Integer, db.ForeignKey('descricao.id'), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicao.id'), nullable=False)
    atendente_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    atendida = db.Column(db.Boolean, default=False, nullable=False)
    municipio = db.relationship('Municipio', back_populates='cadastros')
    estado = db.relationship('Estado', back_populates='cadastros')
    descricao = db.relationship('Descricao', back_populates='cadastros')
    instituicao = db.relationship('Instituicao', back_populates='cadastros')
    atendente = db.relationship('User', back_populates='cadastros')

class Log(db.Model):
    """System log entity."""
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    usuario = db.Column(db.String(100), nullable=False)
    acao = db.Column(db.String(255), nullable=False)
