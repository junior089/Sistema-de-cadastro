from app import db
from datetime import datetime

class Cadastro(db.Model):
    """Registration entity."""
    __tablename__ = 'cadastro'

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
