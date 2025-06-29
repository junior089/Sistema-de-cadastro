from app import db

class Descricao(db.Model):
    """Description entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cadastros = db.relationship('Cadastro', back_populates='descricao')
