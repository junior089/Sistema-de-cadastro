from flask import Flask, request
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.utils.backup_utils import DatabaseBackup
from app.utils.scheduler import init_scheduler
from app.utils.database_config import create_flask_app
from app.utils.logger_config import setup_logging, get_logger, log_system_event
from queue import Queue
import os
import logging
from datetime import datetime
from app import db, migrate

# Configuração do sistema de logging
logger, loggers = setup_logging('mutirao_mulher', log_level=logging.INFO)
logger.info("Iniciando configuração da aplicação Flask")

# Inicialização do app e extensões (apenas uma vez, via factory)
try:
    app, backup_system = create_flask_app()
    logger.info("Aplicação Flask criada com sucesso")
except Exception as e:
    logger.error(f"Erro ao criar aplicação Flask: {str(e)}")
    raise

app.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
logger.debug(f"Template folder configurado: {app.template_folder}")
logger.debug(f"Static folder configurado: {app.static_folder}")

try:
    db.init_app(app)
    migrate.init_app(app, db)
    logger.info("Extensões SQLAlchemy e Migrate inicializadas")
except Exception as e:
    logger.error(f"Erro ao inicializar extensões: {str(e)}")
    raise

# Inicialização do SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
logger.info("SocketIO inicializado com sucesso")

# Disponibiliza backup_system no contexto do app via config
app.config['BACKUP_SYSTEM'] = backup_system
logger.debug("Sistema de backup configurado no app")

# Configuração centralizada de caminhos
app.config['BACKUP_FOLDER'] = os.path.join(app.root_path, 'backups')
app.config['LOG_FOLDER'] = os.path.join(app.root_path, 'logs')
app.config['DATABASE_FOLDER'] = os.path.join(app.instance_path, 'cadastro.db')

logger.info(f"Configurações de caminhos definidas:")
logger.info(f"  - Backup folder: {app.config['BACKUP_FOLDER']}")
logger.info(f"  - Log folder: {app.config['LOG_FOLDER']}")
logger.info(f"  - Database file: {app.config['DATABASE_FOLDER']}")

# Sistema de notificações em tempo real
notification_queue = Queue()
connected_clients = set()
# Disponibiliza via config em vez de atribuição direta
app.config['notification_queue'] = notification_queue
app.config['connected_clients'] = connected_clients
logger.info("Sistema de notificações em tempo real configurado")

login_manager = LoginManager()
login_manager.init_app(app)
# Não atribuir login_view para evitar erro de tipo do linter
# login_manager.login_view = "login"
login_manager.login_message = "Por favor, faça login para acessar esta página."
logger.info("LoginManager configurado")

from app.models.system_status import SystemStatus
from app.models.user import User
from app.models.cadastro import Cadastro
from app.models.municipio import Municipio
from app.models.estado import Estado
from app.models.descricao import Descricao
from app.models.instituicao import Instituicao
from app.models.atendente import Atendente
from app.models.log import Log

logger.info("Modelos importados com sucesso")

@login_manager.user_loader
def load_user(user_id):
    logger.debug(f"Carregando usuário com ID: {user_id}")
    try:
        user = db.session.get(User, int(user_id))
        if user:
            logger.debug(f"Usuário carregado: {user.username}")
        else:
            logger.warning(f"Usuário não encontrado para ID: {user_id}")
        return user
    except Exception as e:
        logger.error(f"Erro ao carregar usuário {user_id}: {str(e)}")
        return None

# Importação dos blueprints
logger.info("Importando blueprints...")
from app.routes.auth_routes import auth_bp
from app.routes.cadastro_routes import cadastro_bp
from app.routes.admin_routes import admin_bp
from app.routes.api_routes import api_bp
from app.routes.senhas_routes import senhas_bp

# Registro dos blueprints
try:
    app.register_blueprint(auth_bp)
    app.register_blueprint(cadastro_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(senhas_bp)
    logger.info("Todos os blueprints registrados com sucesso")
except Exception as e:
    logger.error(f"Erro ao registrar blueprints: {str(e)}")
    raise

# Eventos SocketIO
@socketio.on('connect')
def handle_connect():
    logger.info(f"Cliente conectado via WebSocket - SID: {request.sid}")
    emit('connected', {'message': 'Conectado ao servidor de senhas'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Cliente desconectado via WebSocket - SID: {request.sid}")

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    if room:
        join_room(room)
        logger.info(f"Cliente {request.sid} entrou na sala: {room}")
        emit('room_joined', {'room': room}, room=room)

@socketio.on('leave_room')
def handle_leave_room(data):
    room = data.get('room')
    if room:
        leave_room(room)
        logger.info(f"Cliente {request.sid} saiu da sala: {room}")

@socketio.on('chamar_senha')
def handle_chamar_senha(data):
    """Evento para chamar uma senha"""
    try:
        cadastro_id = data.get('cadastro_id')
        usuario = data.get('usuario', 'Sistema')
        
        with app.app_context():
            cadastro = Cadastro.query.get(cadastro_id)
            if cadastro:
                cadastro.status_chamada = 'chamado'
                cadastro.horario_chamada = datetime.now()
                cadastro.registrar_chamada(usuario, 'chamado')
                db.session.commit()
                
                # Emitir evento para todos os clientes
                socketio.emit('senha_chamada', {
                    'id': cadastro.id,
                    'senha': cadastro.senha_chamada,
                    'nome': cadastro.nome,
                    'prioridade': cadastro.prioridade,
                    'timestamp': datetime.now().isoformat()
                }, broadcast=True)
                
                logger.info(f"Senha chamada via WebSocket - ID: {cadastro_id} - Senha: {cadastro.senha_chamada}")
            else:
                emit('error', {'message': 'Cadastro não encontrado'})
                
    except Exception as e:
        logger.error(f"Erro ao chamar senha via WebSocket: {str(e)}")
        emit('error', {'message': 'Erro interno do servidor'})

@socketio.on('atender_senha')
def handle_atender_senha(data):
    """Evento para atender uma senha"""
    try:
        cadastro_id = data.get('cadastro_id')
        usuario = data.get('usuario', 'Sistema')
        
        with app.app_context():
            cadastro = Cadastro.query.get(cadastro_id)
            if cadastro:
                cadastro.status_chamada = 'em_atendimento'
                cadastro.atendente_id = current_user.id if current_user.is_authenticated else None
                cadastro.registrar_chamada(usuario, 'em_atendimento')
                db.session.commit()
                
                # Emitir evento para todos os clientes
                socketio.emit('senha_atendida', {
                    'id': cadastro.id,
                    'senha': cadastro.senha_chamada,
                    'nome': cadastro.nome,
                    'timestamp': datetime.now().isoformat()
                }, broadcast=True)
                
                logger.info(f"Senha atendida via WebSocket - ID: {cadastro_id} - Senha: {cadastro.senha_chamada}")
            else:
                emit('error', {'message': 'Cadastro não encontrado'})
                
    except Exception as e:
        logger.error(f"Erro ao atender senha via WebSocket: {str(e)}")
        emit('error', {'message': 'Erro interno do servidor'})

@socketio.on('finalizar_atendimento')
def handle_finalizar_atendimento(data):
    """Evento para finalizar atendimento de uma senha"""
    try:
        cadastro_id = data.get('cadastro_id')
        usuario = data.get('usuario', 'Sistema')
        
        with app.app_context():
            cadastro = Cadastro.query.get(cadastro_id)
            if cadastro:
                cadastro.status_chamada = 'atendido'
                cadastro.atendida = True
                cadastro.registrar_chamada(usuario, 'finalizado')
                db.session.commit()
                
                # Emitir evento para todos os clientes
                socketio.emit('atendimento_finalizado', {
                    'id': cadastro.id,
                    'senha': cadastro.senha_chamada,
                    'nome': cadastro.nome,
                    'timestamp': datetime.now().isoformat()
                }, broadcast=True)
                
                logger.info(f"Atendimento finalizado via WebSocket - ID: {cadastro_id} - Senha: {cadastro.senha_chamada}")
            else:
                emit('error', {'message': 'Cadastro não encontrado'})
                
    except Exception as e:
        logger.error(f"Erro ao finalizar atendimento via WebSocket: {str(e)}")
        emit('error', {'message': 'Erro interno do servidor'})

@socketio.on('marcar_ausente')
def handle_marcar_ausente(data):
    """Evento para marcar uma senha como ausente"""
    try:
        cadastro_id = data.get('cadastro_id')
        usuario = data.get('usuario', 'Sistema')
        
        with app.app_context():
            cadastro = Cadastro.query.get(cadastro_id)
            if cadastro:
                cadastro.status_chamada = 'ausente'
                cadastro.registrar_chamada(usuario, 'ausente')
                db.session.commit()
                
                # Emitir evento para todos os clientes
                socketio.emit('senha_ausente', {
                    'id': cadastro.id,
                    'senha': cadastro.senha_chamada,
                    'nome': cadastro.nome,
                    'timestamp': datetime.now().isoformat()
                }, broadcast=True)
                
                logger.info(f"Senha marcada como ausente via WebSocket - ID: {cadastro_id} - Senha: {cadastro.senha_chamada}")
            else:
                emit('error', {'message': 'Cadastro não encontrado'})
                
    except Exception as e:
        logger.error(f"Erro ao marcar ausente via WebSocket: {str(e)}")
        emit('error', {'message': 'Erro interno do servidor'})

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

# Filtro Jinja para classes de log
def get_log_class(acao):
    classes = {
        'criou': 'log-success',
        'deletou': 'log-danger',
        'editou': 'log-warning',
        # Adicione mais conforme necessário
    }
    return classes.get(acao, 'log-default')

app.jinja_env.filters['get_log_class'] = get_log_class

def get_log_icon(acao):
    icons = {
        'criou': 'fa-plus-circle',
        'deletou': 'fa-trash',
        'editou': 'fa-edit',
        # Adicione mais conforme necessário
    }
    return icons.get(acao, 'fa-file-alt')

app.jinja_env.filters['get_log_icon'] = get_log_icon

logger.info("Filtros Jinja configurados")

# Inicialização do banco e diretórios

def create_backup_dirs():
    logger.info("Criando diretórios de backup...")
    try:
        os.makedirs(app.config['BACKUP_FOLDER'], exist_ok=True)
        os.makedirs(app.config['LOG_FOLDER'], exist_ok=True)
        for subdir in ['daily', 'weekly', 'monthly', 'manual', 'safety']:
            os.makedirs(os.path.join(app.config['BACKUP_FOLDER'], subdir), exist_ok=True)
        logger.info("Diretórios de backup criados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao criar diretórios de backup: {str(e)}")
        raise

def init_system_status():
    logger.info("Inicializando status do sistema...")
    try:
        from app.models.system_status import SystemStatus
        from datetime import datetime, UTC
        status = SystemStatus.query.first()
        if not status:
            logger.info("Criando registro de status do sistema...")
            status = SystemStatus()
            db.session.add(status)
            db.session.commit()
            logger.info("Status do sistema inicializado com sucesso")
        else:
            logger.info("Status do sistema já existe")
    except Exception as e:
        logger.error(f"Erro ao inicializar status do sistema: {str(e)}")
        raise

# def check_and_fix_system_status_table(db_path):
#     import sqlite3
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#     # Sempre remove e recria a tabela para garantir estrutura correta
#     cursor.execute("DROP TABLE IF EXISTS system_status;")
#     cursor.execute('''
#         CREATE TABLE system_status (
#             id INTEGER PRIMARY KEY,
#             status VARCHAR(64) NOT NULL DEFAULT 'OK',
#             last_update DATETIME,
#             maintenance_mode BOOLEAN DEFAULT 0,
#             maintenance_message VARCHAR(500) DEFAULT 'Sistema em manutenção. Por favor, tente novamente mais tarde.'
#         );
#     ''')
#     conn.commit()
#     conn.close()

if __name__ == '__main__':
    import socket
    
    # Importar todos os modelos explicitamente antes de criar as tabelas
    logger.info("Importando modelos para criação de tabelas...")
    from app.models.system_status import SystemStatus
    from app.models.user import User
    from app.models.cadastro import Cadastro
    from app.models.municipio import Municipio
    from app.models.estado import Estado
    from app.models.descricao import Descricao
    from app.models.instituicao import Instituicao
    from app.models.atendente import Atendente
    from app.models.log import Log

    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    local_ip = get_local_ip()
    logger.info(f"IP local detectado: {local_ip}")
    
    try:
        os.makedirs(app.instance_path, exist_ok=True)
        logger.info(f"Diretório instance criado: {app.instance_path}")
    except Exception as e:
        logger.error(f"Erro ao criar diretório instance: {str(e)}")
        raise
    
    db_path = app.config['DATABASE_FOLDER']
    logger.info(f"USANDO BANCO: {db_path}")
    
    if not os.path.exists(db_path):
        logger.info("Arquivo de banco não existe, criando...")
        open(db_path, 'a').close()
        logger.info("Arquivo de banco criado")
    
    with app.app_context():
        logger.info("Iniciando criação das tabelas...")
        try:
            db.create_all()  # Cria todas as tabelas primeiro
            logger.info("Todas as tabelas criadas com sucesso")
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {str(e)}")
            raise
        
        try:
            create_backup_dirs()
        except Exception as e:
            logger.error(f"Erro ao criar diretórios de backup: {str(e)}")
            raise
        
        try:
            init_system_status()  # Só inicializa o status depois das tabelas existirem
        except Exception as e:
            logger.error(f"Erro ao inicializar status do sistema: {str(e)}")
            raise
    
    log_system_event("INICIALIZAÇÃO", "Sistema iniciado com sucesso", "INFO")
    
    print("\n" + "=" * 50)
    print("🌱 SISTEMA MUTIRÃO DA MULHER RURAL")
    print("=" * 50)
    print("✅ Sistema iniciado com sucesso!")
    print("🌐 Acesso Local:  http://127.0.0.1:5000")
    print(f"🌐 Acesso Rede:   http://{local_ip}:5000")
    print("🔌 WebSocket habilitado para atualizações em tempo real")
    print("=" * 50 + "\n")
    
    logger.info("Iniciando servidor Flask com SocketIO...")
    try:
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {str(e)}")
        raise
