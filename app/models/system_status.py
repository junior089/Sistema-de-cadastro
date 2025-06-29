from app import db
from datetime import datetime, UTC

class SystemStatus(db.Model):
    __tablename__ = 'system_status'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(64), nullable=False, default='OK')
    last_update = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.String(500), default="Sistema em manutenção. Por favor, tente novamente mais tarde.")

    def __repr__(self):
        return f'<SystemStatus {self.status}>'
    
    def update_status(self, status='OK'):
        """Atualiza o status do sistema"""
        self.status = status
        self.last_update = datetime.now(UTC)
        db.session.commit()
    
    def enable_maintenance(self, message=None):
        """Ativa o modo de manutenção"""
        self.maintenance_mode = True
        if message:
            self.maintenance_message = message
        self.update_status('MAINTENANCE')
    
    def disable_maintenance(self):
        """Desativa o modo de manutenção"""
        self.maintenance_mode = False
        self.update_status('OK')
