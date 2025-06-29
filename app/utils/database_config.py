from flask import Flask
from pathlib import Path
from typing import Tuple
from app.utils.backup_utils import DatabaseBackup  # Importa a classe correta
import os


def configure_database_path(app: Flask) -> str:
    # Usa a pasta instance da raiz do projeto
    base_dir = Path(app.instance_path)
    db_path = base_dir / 'cadastro.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    db_path.parent.mkdir(exist_ok=True)
    return str(db_path)


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