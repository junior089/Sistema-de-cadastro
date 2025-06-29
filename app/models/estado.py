from app import db

class Estado(db.Model):
    """State entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    municipios = db.relationship('Municipio', back_populates='estado')
    cadastros = db.relationship('Cadastro', back_populates='estado')
