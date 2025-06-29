from app import db

class Instituicao(db.Model):
    """Institution entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cadastros = db.relationship('Cadastro', back_populates='instituicao')
