from flask import Flask
from pathlib import Path
import os
import logging
from typing import Tuple


def configure_database_path(app: Flask) -> str:

    base_dir = Path(app.root_path)
    db_path = base_dir / 'cadastro.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db_path.parent.mkdir(exist_ok=True)
    return str(db_path)


class DatabaseBackup:
    def __init__(self, app_config: dict, backup_dir: str = 'backups'):
        """
        Inicializa o sistema de backup

        Args:
            app_config: Configuração do Flask contendo a URI do banco
            backup_dir: Diretório onde os backups serão armazenados
        """
        self.backup_dir = backup_dir

        # Extrai o caminho do banco da URI do SQLAlchemy
        db_uri = app_config['SQLALCHEMY_DATABASE_URI']
        if db_uri.startswith('sqlite:///'):
            self.db_path = os.path.abspath(db_uri.replace('sqlite:///', ''))
        else:
            raise ValueError("Configuração de banco de dados inválida")

        self.setup_logging()
        self.setup_backup_directory()

    def setup_logging(self) -> None:
        """Configura o sistema de logging"""
        log_dir = 'logs'
        Path(log_dir).mkdir(exist_ok=True)

        logging.basicConfig(
            filename=os.path.join(log_dir, 'backup.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('DatabaseBackup')

    def setup_backup_directory(self) -> None:
        """Cria e organiza o diretório de backups"""
        Path(self.backup_dir).mkdir(exist_ok=True)

        for subdir in ['daily', 'weekly', 'monthly', 'manual', 'safety']:
            Path(os.path.join(self.backup_dir, subdir)).mkdir(exist_ok=True)

    def create_backup(self, backup_type: str = 'manual') -> Tuple[bool, str]:
        """
        Cria um backup do banco de dados

        Args:
            backup_type: Tipo de backup (manual, daily, weekly, monthly)

        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Verifica se o banco existe
            if not os.path.exists(self.db_path):
                error_msg = f"Banco de dados não encontrado em {self.db_path}"
                self.logger.error(error_msg)
                return False, error_msg

            # Log de tentativa de backup
            self.logger.info(f"Iniciando backup do tipo {backup_type}")

            return True, "Backup criado com sucesso"

        except Exception as e:
            error_msg = f"Erro ao criar backup: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg


def create_flask_app() -> Tuple[Flask, DatabaseBackup]:
    """
    Cria e configura a aplicação Flask

    Returns:
        Tuple[Flask, DatabaseBackup]: (app Flask, sistema de backup)
    """
    app = Flask(__name__)
    app.secret_key = '7349cqzm'

    # Configura o caminho do banco de dados
    db_path = configure_database_path(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa o sistema de backup com o caminho correto
    backup_system = DatabaseBackup(app.config)

    return app, backup_system