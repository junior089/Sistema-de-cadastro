from datetime import datetime, UTC
from typing import Dict, Any, Optional
from app import db
from app.models.log import Log
from app.models.user import User
from flask_login import current_user
import json

class AuditLogger:
    """Sistema de auditoria para rastrear ações do sistema"""
    
    @staticmethod
    def log_action(action: str, details: str = "", entity_type: str = "", 
                   entity_id: Optional[int] = None, user_id: Optional[int] = None,
                   ip_address: str = "", user_agent: str = "", 
                   additional_data: Optional[Dict[str, Any]] = None):
        """
        Registra uma ação no sistema de auditoria
        
        Args:
            action: Ação realizada
            details: Detalhes da ação
            entity_type: Tipo da entidade afetada (ex: 'user', 'cadastro', 'estado')
            entity_id: ID da entidade afetada
            user_id: ID do usuário que realizou a ação
            ip_address: Endereço IP do usuário
            user_agent: User agent do navegador
            additional_data: Dados adicionais em formato JSON
        """
        try:
            # Se não foi fornecido user_id, usa o usuário atual
            if user_id is None and hasattr(current_user, 'id'):
                user_id = current_user.id
            
            # Se não foi fornecido username, usa o usuário atual
            username = "Sistema"
            if hasattr(current_user, 'username'):
                username = current_user.username
            elif user_id:
                user = User.query.get(user_id)
                if user:
                    username = user.username
            
            # Prepara os dados adicionais
            extra_data = {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'timestamp': datetime.now(UTC).isoformat()
            }
            
            if additional_data:
                extra_data.update(additional_data)
            
            # Cria a mensagem de log
            log_message = f"{action}"
            if details:
                log_message += f": {details}"
            
            # Adiciona dados extras como JSON na mensagem
            if extra_data:
                log_message += f" | {json.dumps(extra_data, ensure_ascii=False)}"
            
            # Cria o registro de log
            log_entry = Log(
                usuario=username,
                acao=log_message
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            # Em caso de erro, tenta registrar pelo menos o erro
            try:
                error_log = Log(
                    usuario="Sistema",
                    acao=f"Erro ao registrar log: {str(e)} | Ação original: {action}"
                )
                db.session.add(error_log)
                db.session.commit()
            except:
                pass  # Se não conseguir nem registrar o erro, ignora
    
    @staticmethod
    def log_user_login(user_id: int, username: str, ip_address: str = "", 
                      user_agent: str = "", success: bool = True):
        """Registra login de usuário"""
        action = "Login realizado" if success else "Tentativa de login falhou"
        AuditLogger.log_action(
            action=action,
            details=f"Usuário: {username}",
            entity_type="user",
            entity_id=user_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            additional_data={'success': success}
        )
    
    @staticmethod
    def log_user_logout(user_id: int, username: str, ip_address: str = ""):
        """Registra logout de usuário"""
        AuditLogger.log_action(
            action="Logout realizado",
            details=f"Usuário: {username}",
            entity_type="user",
            entity_id=user_id,
            user_id=user_id,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_user_creation(created_user_id: int, created_username: str, 
                         created_by_user_id: int, ip_address: str = ""):
        """Registra criação de usuário"""
        AuditLogger.log_action(
            action="Usuário criado",
            details=f"Novo usuário: {created_username}",
            entity_type="user",
            entity_id=created_user_id,
            user_id=created_by_user_id,
            ip_address=ip_address,
            additional_data={'created_username': created_username}
        )
    
    @staticmethod
    def log_user_update(user_id: int, username: str, updated_by_user_id: int,
                       changes: Dict[str, Any], ip_address: str = ""):
        """Registra atualização de usuário"""
        AuditLogger.log_action(
            action="Usuário atualizado",
            details=f"Usuário: {username}",
            entity_type="user",
            entity_id=user_id,
            user_id=updated_by_user_id,
            ip_address=ip_address,
            additional_data={'changes': changes}
        )
    
    @staticmethod
    def log_user_deletion(user_id: int, username: str, deleted_by_user_id: int,
                         ip_address: str = ""):
        """Registra exclusão de usuário"""
        AuditLogger.log_action(
            action="Usuário deletado",
            details=f"Usuário: {username}",
            entity_type="user",
            entity_id=user_id,
            user_id=deleted_by_user_id,
            ip_address=ip_address,
            additional_data={'deleted_username': username}
        )
    
    @staticmethod
    def log_cadastro_creation(cadastro_id: int, nome: str, cpf: str,
                             created_by_user_id: int, ip_address: str = ""):
        """Registra criação de cadastro"""
        AuditLogger.log_action(
            action="Cadastro criado",
            details=f"Nome: {nome}, CPF: {cpf}",
            entity_type="cadastro",
            entity_id=cadastro_id,
            user_id=created_by_user_id,
            ip_address=ip_address,
            additional_data={'nome': nome, 'cpf': cpf}
        )
    
    @staticmethod
    def log_cadastro_update(cadastro_id: int, nome: str, cpf: str,
                           updated_by_user_id: int, changes: Dict[str, Any],
                           ip_address: str = ""):
        """Registra atualização de cadastro"""
        AuditLogger.log_action(
            action="Cadastro atualizado",
            details=f"Nome: {nome}, CPF: {cpf}",
            entity_type="cadastro",
            entity_id=cadastro_id,
            user_id=updated_by_user_id,
            ip_address=ip_address,
            additional_data={'changes': changes}
        )
    
    @staticmethod
    def log_data_creation(entity_type: str, entity_id: int, entity_name: str,
                          created_by_user_id: int, ip_address: str = ""):
        """Registra criação de dados do sistema (estado, município, etc.)"""
        AuditLogger.log_action(
            action=f"{entity_type.title()} criado",
            details=f"Nome: {entity_name}",
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=created_by_user_id,
            ip_address=ip_address,
            additional_data={'entity_name': entity_name}
        )
    
    @staticmethod
    def log_backup_creation(backup_type: str, backup_path: str,
                           created_by_user_id: int, ip_address: str = ""):
        """Registra criação de backup"""
        AuditLogger.log_action(
            action="Backup criado",
            details=f"Tipo: {backup_type}, Arquivo: {backup_path}",
            entity_type="backup",
            user_id=created_by_user_id,
            ip_address=ip_address,
            additional_data={'backup_type': backup_type, 'backup_path': backup_path}
        )
    
    @staticmethod
    def log_backup_restore(backup_path: str, restored_by_user_id: int,
                          ip_address: str = ""):
        """Registra restauração de backup"""
        AuditLogger.log_action(
            action="Backup restaurado",
            details=f"Arquivo: {backup_path}",
            entity_type="backup",
            user_id=restored_by_user_id,
            ip_address=ip_address,
            additional_data={'backup_path': backup_path}
        )
    
    @staticmethod
    def log_system_maintenance(enabled: bool, message: str = "",
                              changed_by_user_id: int = None, ip_address: str = ""):
        """Registra mudança no modo de manutenção"""
        action = "Modo de manutenção ativado" if enabled else "Modo de manutenção desativado"
        AuditLogger.log_action(
            action=action,
            details=message,
            entity_type="system",
            user_id=changed_by_user_id,
            ip_address=ip_address,
            additional_data={'maintenance_enabled': enabled, 'message': message}
        )

# Instância global do sistema de auditoria
audit_logger = AuditLogger() 