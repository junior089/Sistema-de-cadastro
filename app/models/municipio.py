from app import db

class Municipio(db.Model):
    """Municipality entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    estado = db.relationship('Estado', back_populates='municipios')
    cadastros = db.relationship('Cadastro', back_populates='municipio')
