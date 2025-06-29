import json
import threading
import time
from datetime import datetime, UTC
from typing import Dict, List, Optional, Set
from queue import Queue
import logging

class NotificationSystem:
    def __init__(self):
        self.notification_queue = Queue()
        self.connected_clients: Set[int] = set()
        self.logger = logging.getLogger('NotificationSystem')
        
    def send_notification(self, notification_type: str, message: str, data: Optional[Dict] = None, 
                         user_id: Optional[int] = None, broadcast: bool = True):
        """
        Envia uma notificação para os clientes conectados
        
        Args:
            notification_type: Tipo da notificação (info, warning, error, success)
            message: Mensagem da notificação
            data: Dados adicionais (opcional)
            user_id: ID do usuário específico (opcional)
            broadcast: Se deve enviar para todos os clientes
        """
        notification = {
            'type': notification_type,
            'message': message,
            'timestamp': datetime.now(UTC).isoformat(),
            'data': data or {},
            'user_id': user_id,
            'broadcast': broadcast
        }
        
        self.notification_queue.put(notification)
        self.logger.info(f"Notificação enviada: {notification_type} - {message}")
    
    def add_client(self, client_id: int):
        """Adiciona um cliente à lista de conectados"""
        self.connected_clients.add(client_id)
        self.logger.info(f"Cliente {client_id} conectado. Total: {len(self.connected_clients)}")
    
    def remove_client(self, client_id: int):
        """Remove um cliente da lista de conectados"""
        self.connected_clients.discard(client_id)
        self.logger.info(f"Cliente {client_id} desconectado. Total: {len(self.connected_clients)}")
    
    def get_connected_clients_count(self) -> int:
        """Retorna o número de clientes conectados"""
        return len(self.connected_clients)
    
    def broadcast_system_status(self, status: str, message: str = ""):
        """Envia status do sistema para todos os clientes"""
        self.send_notification(
            notification_type='system_status',
            message=message or f"Sistema: {status}",
            data={'status': status},
            broadcast=True
        )
    
    def notify_user_activity(self, user_id: int, action: str, details: str = ""):
        """Notifica atividade de um usuário específico"""
        self.send_notification(
            notification_type='user_activity',
            message=f"Atividade: {action}",
            data={'action': action, 'details': details},
            user_id=user_id,
            broadcast=False
        )
    
    def notify_data_change(self, change_type: str, entity: str, details: str = ""):
        """Notifica mudanças nos dados do sistema"""
        self.send_notification(
            notification_type='data_change',
            message=f"{change_type}: {entity}",
            data={'change_type': change_type, 'entity': entity, 'details': details},
            broadcast=True
        )

# Instância global do sistema de notificações
notification_system = NotificationSystem()

def format_cadastro_for_notification(cadastro):
    """
    Formata os dados do cadastro para envio de notificação.
    """
    return {
        'id': cadastro.id,
        'name': cadastro.nome,
        'cpf': cadastro.cpf,
        'service': cadastro.descricao.nome if hasattr(cadastro, 'descricao') and cadastro.descricao else '',
        'datetime': cadastro.data_hora,
        'attendant': cadastro.atendente_id
    }

def broadcast_notification(event, data):
    """
    Função mock para broadcast de notificação (exemplo: websocket, fila, etc).
    """
    # Aqui você pode integrar com um sistema real de notificações, se desejar
    print(f"[NOTIFICATION] Event: {event} | Data: {data}")
