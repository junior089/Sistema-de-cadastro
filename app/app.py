from flask import Flask
from app import db, migrate
from flask_login import LoginManager
from app.backup_utils import DatabaseBackup
from app.scheduler import init_scheduler
from app.database_config import create_flask_app
from queue import Queue
import os

# Inicialização do app e extensões (apenas uma vez, via factory)
app, backup_system = create_flask_app()
db.init_app(app)
migrate.init_app(app, db)
app.backup_system = backup_system  # Disponibiliza backup_system no contexto do app

# Sistema de notificações em tempo real
notification_queue = Queue()
connected_clients = set()
app.notification_queue = notification_queue
app.connected_clients = connected_clients
app.config['notification_queue'] = notification_queue
app.config['connected_clients'] = connected_clients

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Por favor, faça login para acessar esta página."

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Importação dos blueprints
from app.routes.auth_routes import auth_bp
from app.routes.cadastro_routes import cadastro_bp
from app.routes.admin_routes import admin_bp
from app.routes.api_routes import api_bp

# Registro dos blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(cadastro_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp)

# Funções utilitárias globais (exemplo)
def get_error_code(titulo):
    error_codes = {
        "Requisição Inválida": "400",
        "Não Autorizado": "401",
        "Acesso Negado": "403",
        "Página Não Encontrada": "404",
        "Erro Interno": "500",
        "Serviço Indisponível": "503"
    }
    return error_codes.get(titulo, "000")

def get_error_icon(titulo):
    error_icons = {
        "Requisição Inválida": "fa-exclamation-circle",
        "Não Autorizado": "fa-lock",
        "Acesso Negado": "fa-ban",
        "Página Não Encontrada": "fa-question-circle",
        "Erro Interno": "fa-exclamation-triangle",
        "Serviço Indisponível": "fa-tools"
    }
    return error_icons.get(titulo, "fa-exclamation-triangle")

@app.context_processor
def utility_processor():
    return dict(
        get_error_code=get_error_code,
        get_error_icon=get_error_icon
    )

# Inicialização do banco e diretórios

def create_backup_dirs():
    for dir_name in ['backups', 'logs']:
        os.makedirs(dir_name, exist_ok=True)
    for subdir in ['daily', 'weekly', 'monthly', 'manual', 'safety']:
        os.makedirs(os.path.join('backups', subdir), exist_ok=True)

def init_system_status():
    from app.models import SystemStatus
    from datetime import datetime, UTC
    status = SystemStatus.query.first()
    if not status:
        status = SystemStatus(
            maintenance_mode=False,
            maintenance_message="Sistema em manutenção. Por favor, tente novamente mais tarde.",
            last_updated=datetime.now(UTC)
        )
        db.session.add(status)
        db.session.commit()

if __name__ == '__main__':
    import socket
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    local_ip = get_local_ip()
    with app.app_context():
        db.create_all()
        create_backup_dirs()
        init_system_status()
    print("\n" + "=" * 50)
    print("🌱 SISTEMA MUTIRÃO DA MULHER RURAL")
    print("=" * 50)
    print("✅ Sistema iniciado com sucesso!")
    print(f"🌐 Acesso Local:  http://127.0.0.1:5000")
    print(f"🌐 Acesso Rede:   http://{local_ip}:5000")
    print("=" * 50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
