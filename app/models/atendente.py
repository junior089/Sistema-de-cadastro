from app import db

class Atendente(db.Model):
    """Attendant entity."""
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
