from datetime import datetime
from flask import current_app

def broadcast_notification(event_type, data):
    """Envia notificação para todos os clientes conectados"""
    notification = {
        'type': event_type,
        'data': data,
        'timestamp': datetime.now().isoformat()
    }
    notification_queue = current_app.config['notification_queue']
    notification_queue.put(notification)

def format_cadastro_for_notification(cadastro):
    """Formata um cadastro para envio via SSE"""
    return {
        'id': cadastro.id,
        'data_hora': cadastro.data_hora,
        'nome': cadastro.nome,
        'cpf': cadastro.cpf,
        'telefone': cadastro.telefone,
        'municipio': {
            'id': cadastro.municipio.id if cadastro.municipio else None,
            'nome': cadastro.municipio.nome if cadastro.municipio else 'N/A'
        },
        'estado': {
            'id': cadastro.estado.id,
            'nome': cadastro.estado.nome
        },
        'descricao': {
            'id': cadastro.descricao.id,
            'nome': cadastro.descricao.nome
        },
        'atendida': cadastro.atendida
    }
