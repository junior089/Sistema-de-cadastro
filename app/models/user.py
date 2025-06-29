from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.logger_config import get_logger, log_database_operation

logger = get_logger('models')

DEFAULT_ROLE = 'cadastrador'
DEFAULT_MAINTENANCE_MSG = "Sistema em manutenção. Por favor, tente novamente mais tarde."

class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=DEFAULT_ROLE)
    cadastros = db.relationship('Cadastro', back_populates='atendente', cascade="all, delete-orphan")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.debug(f"Novo objeto User criado - Username: {kwargs.get('username', 'N/A')}")

    def __repr__(self):
        return f'<User {self.username}>'

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        logger.debug(f"Definindo senha para usuário: {self.username}")
        self.password_hash = generate_password_hash(password)
        logger.info(f"Senha definida para usuário: {self.username}")

    def verify_password(self, password):
        logger.debug(f"Verificando senha para usuário: {self.username}")
        try:
            result = check_password_hash(self.password_hash, password)
            if result:
                logger.debug(f"Senha verificada com sucesso para usuário: {self.username}")
            else:
                logger.warning(f"Senha incorreta para usuário: {self.username}")
            return result
        except Exception as e:
            logger.error(f"Erro ao verificar senha para usuário: {self.username} - Erro: {str(e)}")
            return False

    def save(self, user=None):
        """Método personalizado para salvar com logging"""
        try:
            if self.id is None:
                # Novo usuário
                logger.info(f"Criando novo usuário - Username: {self.username} - Role: {self.role}")
                log_database_operation('CREATE', 'user', None, user)
            else:
                # Atualizando usuário existente
                logger.info(f"Atualizando usuário - ID: {self.id} - Username: {self.username}")
                log_database_operation('UPDATE', 'user', self.id, user)
            
            db.session.add(self)
            db.session.commit()
            
            logger.info(f"Usuário salvo com sucesso - ID: {self.id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao salvar usuário - Username: {self.username} - Erro: {str(e)}")
            return False

    def delete(self, user=None):
        """Método personalizado para deletar com logging"""
        try:
            user_id = self.id
            username = self.username
            
            logger.info(f"Deletando usuário - ID: {user_id} - Username: {username}")
            log_database_operation('DELETE', 'user', user_id, user)
            
            db.session.delete(self)
            db.session.commit()
            
            logger.info(f"Usuário deletado com sucesso - ID: {user_id}")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao deletar usuário - ID: {self.id} - Erro: {str(e)}")
            return False

    def change_password(self, new_password, user=None):
        """Método para alterar senha com logging"""
        logger.info(f"Alterando senha - Usuário: {self.username}")
        
        try:
            self.password = new_password
            db.session.commit()
            
            logger.info(f"Senha alterada com sucesso - Usuário: {self.username}")
            log_database_operation('UPDATE', 'user', self.id, user)
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao alterar senha - Usuário: {self.username} - Erro: {str(e)}")
            return False

    def change_role(self, new_role, user=None):
        """Método para alterar role com logging"""
        logger.info(f"Alterando role - Usuário: {self.username} - Nova role: {new_role}")
        
        try:
            role_anterior = self.role
            self.role = new_role
            db.session.commit()
            
            logger.info(f"Role alterada com sucesso - Usuário: {self.username} - Role anterior: {role_anterior} - Nova role: {new_role}")
            log_database_operation('UPDATE', 'user', self.id, user)
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Erro ao alterar role - Usuário: {self.username} - Erro: {str(e)}")
            return False

    @classmethod
    def buscar_por_username(cls, username, user=None):
        """Busca usuário por username com logging"""
        logger.debug(f"Buscando usuário por username - Username: {username}")
        
        try:
            usuario = cls.query.filter_by(username=username).first()
            if usuario:
                logger.info(f"Usuário encontrado por username - ID: {usuario.id} - Username: {usuario.username}")
                log_database_operation('READ', 'user', usuario.id, user)
            else:
                logger.info(f"Usuário não encontrado por username - Username: {username}")
            
            return usuario
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por username - Username: {username} - Erro: {str(e)}")
            return None

    @classmethod
    def buscar_por_id(cls, user_id, user=None):
        """Busca usuário por ID com logging"""
        logger.debug(f"Buscando usuário por ID - ID: {user_id}")
        
        try:
            usuario = cls.query.get(user_id)
            if usuario:
                logger.info(f"Usuário encontrado por ID - ID: {usuario.id} - Username: {usuario.username}")
                log_database_operation('READ', 'user', usuario.id, user)
            else:
                logger.info(f"Usuário não encontrado por ID - ID: {user_id}")
            
            return usuario
        except Exception as e:
            logger.error(f"Erro ao buscar usuário por ID - ID: {user_id} - Erro: {str(e)}")
            return None

    @classmethod
    def listar_por_role(cls, role, user=None):
        """Lista usuários por role com logging"""
        logger.debug(f"Listando usuários por role - Role: {role}")
        
        try:
            usuarios = cls.query.filter_by(role=role).all()
            logger.info(f"Usuários encontrados por role - Role: {role} - Quantidade: {len(usuarios)}")
            log_database_operation('READ', 'user', None, user)
            
            return usuarios
        except Exception as e:
            logger.error(f"Erro ao listar usuários por role - Role: {role} - Erro: {str(e)}")
            return []

    def get_cadastros_count(self):
        """Retorna o número de cadastros do usuário com logging"""
        logger.debug(f"Contando cadastros do usuário - Usuário: {self.username}")
        
        try:
            count = len(self.cadastros)
            logger.debug(f"Quantidade de cadastros - Usuário: {self.username} - Count: {count}")
            return count
        except Exception as e:
            logger.error(f"Erro ao contar cadastros do usuário - Usuário: {self.username} - Erro: {str(e)}")
            return 0

# Importa os demais modelos para facilitar o import externo
from .municipio import Municipio
from .estado import Estado
from .descricao import Descricao
from .instituicao import Instituicao
from .atendente import Atendente
from .cadastro import Cadastro
from .log import Log
