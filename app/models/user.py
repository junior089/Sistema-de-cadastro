from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

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

# Importa os demais modelos para facilitar o import externo
from .municipio import Municipio
from .estado import Estado
from .descricao import Descricao
from .instituicao import Instituicao
from .atendente import Atendente
from .cadastro import Cadastro
from .log import Log
