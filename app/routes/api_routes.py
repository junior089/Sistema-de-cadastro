from flask import Blueprint, jsonify, Response, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.cadastro import Cadastro
from app.models.municipio import Municipio
from app.models.estado import Estado
from app.models.descricao import Descricao
from app.models.instituicao import Instituicao
from app.models.user import User
from app.models.log import Log
from app.utils.logger_config import get_logger, log_api_request, log_database_operation
from datetime import datetime, timedelta
import json
import threading
import time

api_bp = Blueprint('api', __name__)
logger = get_logger('api')

@api_bp.route('/api/stats')
@login_required
def get_stats():
    user = current_user.username
    logger.info(f"Estatísticas solicitadas - Usuário: {user}")
    
    try:
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)
        hoje_str = hoje.strftime("%Y-%m-%d")
        inicio_semana_str = inicio_semana.strftime("%Y-%m-%d")
        inicio_mes_str = inicio_mes.strftime("%Y-%m-%d")
        
        logger.debug(f"Calculando estatísticas para usuário: {user}")
        
        today_count = Cadastro.query.filter(Cadastro.data_hora.like(f"{hoje_str}%")).count()
        week_count = Cadastro.query.filter(Cadastro.data_hora >= inicio_semana_str).count()
        month_count = Cadastro.query.filter(Cadastro.data_hora >= inicio_mes_str).count()
        total_count = Cadastro.query.count()
        attended_count = Cadastro.query.filter(Cadastro.atendida == True).count()
        users_count = User.query.count()
        
        stats = {
            'today': today_count,
            'week': week_count,
            'month': month_count,
            'total': total_count,
            'attended': attended_count,
            'users': users_count
        }
        
        logger.info(f"Estatísticas calculadas com sucesso - Usuário: {user} - Total: {total_count}")
        log_api_request('GET', '/api/stats', user, 200)
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas - Usuário: {user} - Erro: {str(e)}")
        log_api_request('GET', '/api/stats', user, 500, str(e))
        return jsonify({
            'today': 0,
            'week': 0,
            'month': 0,
            'total': 0,
            'attended': 0,
            'users': 0
        }), 500

@api_bp.route('/api/activities')
@login_required
def get_activities():
    user = current_user.username
    logger.info(f"Atividades solicitadas - Usuário: {user}")
    
    try:
        logs = Log.query.order_by(Log.data_hora.desc()).limit(20).all()
        activities = []
        
        for log in logs:
            activities.append({
                'timestamp': log.data_hora.isoformat(),
                'description': f"{log.usuario} {log.acao}",
                'user': log.usuario,
                'action': log.acao
            })
        
        logger.info(f"Atividades retornadas com sucesso - Usuário: {user} - Quantidade: {len(activities)}")
        log_api_request('GET', '/api/activities', user, 200)
        
        return jsonify(activities)
    except Exception as e:
        logger.error(f"Erro ao buscar atividades - Usuário: {user} - Erro: {str(e)}")
        log_api_request('GET', '/api/activities', user, 500, str(e))
        return jsonify([]), 500

@api_bp.route('/events')
@login_required
def events():
    user = current_user.username
    
    if current_user.role not in ['visor', 'admin']:
        logger.warning(f"Acesso negado a eventos - Usuário: {user} - Role: {current_user.role}")
        log_api_request('GET', '/events', user, 403, "Acesso negado")
        return "Acesso negado!", 403
    
    logger.info(f"Stream de eventos iniciado - Usuário: {user}")
    notification_queue = current_app.config.get('notification_queue')
    connected_clients = current_app.config.get('connected_clients')
    
    def event_stream():
        client_id = id(threading.current_thread())
        if connected_clients:
            connected_clients.add(client_id)
        logger.debug(f"Cliente conectado ao stream - ID: {client_id} - Usuário: {user}")
        
        try:
            while True:
                try:
                    if notification_queue and not notification_queue.empty():
                        notification = notification_queue.get_nowait()
                        yield f"data: {json.dumps(notification)}\n\n"
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Erro no event stream - Cliente: {client_id} - Erro: {str(e)}")
                    break
        finally:
            if connected_clients:
                connected_clients.discard(client_id)
            logger.debug(f"Cliente desconectado do stream - ID: {client_id} - Usuário: {user}")
    
    return Response(event_stream(), mimetype='text/event-stream')

@api_bp.route('/api/cadastros')
@login_required
def get_cadastros():
    user = current_user.username
    
    if current_user.role not in ['visor', 'admin']:
        logger.warning(f"Acesso negado a cadastros - Usuário: {user} - Role: {current_user.role}")
        log_api_request('GET', '/api/cadastros', user, 403, "Acesso negado")
        return jsonify({"error": "Acesso negado"}), 403
    
    logger.info(f"Lista de cadastros solicitada - Usuário: {user}")
    
    try:
        cadastros = Cadastro.query.order_by(Cadastro.data_hora.desc()).all()
        result = [{
            'id': c.id,
            'data_hora': c.data_hora.isoformat(),
            'nome': c.nome,
            'cpf': c.cpf,
            'telefone': c.telefone,
            'assentamento': c.assentamento,
            'municipio': {
                'id': c.municipio.id if c.municipio else None,
                'nome': c.municipio.nome if c.municipio else 'N/A'
            },
            'estado': {
                'id': c.estado.id if c.estado else None,
                'nome': c.estado.nome if c.estado else 'N/A'
            },
            'atendida': c.atendida
        } for c in cadastros]
        
        logger.info(f"Cadastros retornados com sucesso - Usuário: {user} - Quantidade: {len(result)}")
        log_api_request('GET', '/api/cadastros', user, 200)
        log_database_operation('READ', 'cadastro', None, user)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao buscar cadastros - Usuário: {user} - Erro: {str(e)}")
        log_api_request('GET', '/api/cadastros', user, 500, str(e))
        return jsonify([]), 500

@api_bp.route('/api/cadastro/<int:id>')
@login_required
def get_cadastro(id):
    user = current_user.username
    
    if current_user.role not in ['visor', 'admin']:
        logger.warning(f"Acesso negado a cadastro específico - Usuário: {user} - Role: {current_user.role}")
        log_api_request('GET', f'/api/cadastro/{id}', user, 403, "Acesso negado")
        return jsonify({"error": "Acesso negado"}), 403
    
    logger.info(f"Cadastro específico solicitado - Usuário: {user} - ID: {id}")
    
    try:
        cadastro = Cadastro.query.get_or_404(id)
        result = {
            'id': cadastro.id,
            'data_hora': cadastro.data_hora.isoformat(),
            'nome': cadastro.nome,
            'cpf': cadastro.cpf,
            'telefone': cadastro.telefone,
            'assentamento': cadastro.assentamento,
            'atendida': cadastro.atendida,
            'municipio': {
                'id': cadastro.municipio.id if cadastro.municipio else None,
                'nome': cadastro.municipio.nome if cadastro.municipio else 'N/A'
            },
            'estado': {
                'id': cadastro.estado.id if cadastro.estado else None,
                'nome': cadastro.estado.nome if cadastro.estado else 'N/A'
            },
            'descricao': {
                'id': cadastro.descricao.id if cadastro.descricao else None,
                'nome': cadastro.descricao.nome if cadastro.descricao else 'N/A'
            },
            'instituicao': {
                'id': cadastro.instituicao.id if cadastro.instituicao else None,
                'nome': cadastro.instituicao.nome if cadastro.instituicao else 'N/A'
            },
        }
        
        logger.info(f"Cadastro retornado com sucesso - Usuário: {user} - ID: {id}")
        log_api_request('GET', f'/api/cadastro/{id}', user, 200)
        log_database_operation('READ', 'cadastro', id, user)
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Erro ao buscar cadastro - Usuário: {user} - ID: {id} - Erro: {str(e)}")
        log_api_request('GET', f'/api/cadastro/{id}', user, 404, str(e))
        return jsonify({"error": "Cadastro não encontrado"}), 404

@api_bp.route('/api/cadastro/<int:id>/toggle_atendida', methods=['POST'])
@login_required
def toggle_atendida(id):
    user = current_user.username
    
    if current_user.role not in ['visor', 'admin']:
        logger.warning(f"Acesso negado para alternar atendida - Usuário: {user} - Role: {current_user.role}")
        log_api_request('POST', f'/api/cadastro/{id}/toggle_atendida', user, 403, "Acesso negado")
        return jsonify({"error": "Acesso negado"}), 403
    
    logger.info(f"Alternar status atendida solicitado - Usuário: {user} - ID: {id}")
    
    try:
        cadastro = Cadastro.query.get_or_404(id)
        novo_status = not cadastro.atendida
        cadastro.atendida = novo_status
        
        # Registrar log
        log = Log(
            usuario=user,
            acao=f"{'Marcou como atendida' if cadastro.atendida else 'Marcou como pendente'} - {cadastro.nome}"
        )
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"Status atendida alterado com sucesso - Usuário: {user} - ID: {id} - Novo status: {novo_status}")
        log_api_request('POST', f'/api/cadastro/{id}/toggle_atendida', user, 200)
        log_database_operation('UPDATE', 'cadastro', id, user)
        
        return jsonify({
            'success': True,
            'atendida': cadastro.atendida,
            'message': f"Cadastro {'marcado como atendido' if cadastro.atendida else 'marcado como pendente'} com sucesso!"
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao alternar status atendida - Usuário: {user} - ID: {id} - Erro: {str(e)}")
        log_api_request('POST', f'/api/cadastro/{id}/toggle_atendida', user, 500, str(e))
        return jsonify({"error": "Erro ao atualizar status"}), 500

@api_bp.route('/get_municipios/<int:estado_id>')
@login_required
def get_municipios(estado_id):
    user = current_user.username
    logger.info(f"Municípios solicitados - Usuário: {user} - Estado ID: {estado_id}")
    
    try:
        municipios = Municipio.query.filter_by(estado_id=estado_id).all()
        municipios_json = [{'id': municipio.id, 'nome': municipio.nome} for municipio in municipios]
        
        logger.info(f"Municípios retornados com sucesso - Usuário: {user} - Estado ID: {estado_id} - Quantidade: {len(municipios_json)}")
        log_api_request('GET', f'/get_municipios/{estado_id}', user, 200)
        log_database_operation('READ', 'municipio', None, user)
        
        return jsonify(municipios_json)
    except Exception as e:
        logger.error(f"Erro ao buscar municípios - Usuário: {user} - Estado ID: {estado_id} - Erro: {str(e)}")
        log_api_request('GET', f'/get_municipios/{estado_id}', user, 500, str(e))
        return jsonify([]), 500

@api_bp.route('/buscar_nome', methods=['POST'])
@login_required
def buscar_nome():
    user = current_user.username
    logger.info(f"Busca por nome solicitada - Usuário: {user}")
    
    try:
        data = request.get_json()
        cpf = data.get('cpf')
        telefone = data.get('telefone')
        
        logger.debug(f"Parâmetros de busca - Usuário: {user} - CPF: {cpf} - Telefone: {telefone}")
        
        if not cpf and not telefone:
            logger.warning(f"Busca por nome falhou - Parâmetros vazios - Usuário: {user}")
            log_api_request('POST', '/buscar_nome', user, 400, "CPF ou telefone não fornecido")
            return jsonify({'error': 'CPF ou telefone não fornecido'}), 400
        
        cadastro = None
        if cpf:
            cadastro = Cadastro.query.filter_by(cpf=cpf).first()
            logger.debug(f"Busca por CPF - Usuário: {user} - CPF: {cpf} - Encontrado: {cadastro is not None}")
        if telefone and not cadastro:
            cadastro = Cadastro.query.filter_by(telefone=telefone).first()
            logger.debug(f"Busca por telefone - Usuário: {user} - Telefone: {telefone} - Encontrado: {cadastro is not None}")
        
        if cadastro:
            result = {
                'success': True,
                'nome': cadastro.nome,
                'cpf': cadastro.cpf,
                'telefone': cadastro.telefone,
                'assentamento': cadastro.assentamento,
                'estado_id': cadastro.estado_id,
                'municipio_id': cadastro.municipio_id
            }
            
            logger.info(f"Busca por nome bem-sucedida - Usuário: {user} - Nome encontrado: {cadastro.nome}")
            log_api_request('POST', '/buscar_nome', user, 200)
            log_database_operation('READ', 'cadastro', cadastro.id, user)
            
            return jsonify(result)
        
        logger.info(f"Busca por nome sem resultados - Usuário: {user}")
        log_api_request('POST', '/buscar_nome', user, 200)
        
        return jsonify({
            'success': False,
            'message': 'Cadastro não encontrado'
        })
    except Exception as e:
        logger.error(f"Erro ao buscar nome - Usuário: {user} - Erro: {str(e)}")
        log_api_request('POST', '/buscar_nome', user, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500

@api_bp.route('/buscar_cpf', methods=['POST'])
@login_required
def buscar_cpf():
    user = current_user.username
    logger.info(f"Busca por CPF solicitada - Usuário: {user}")
    
    try:
        data = request.get_json()
        nome = data.get('nome')
        telefone = data.get('telefone')
        
        logger.debug(f"Parâmetros de busca - Usuário: {user} - Nome: {nome} - Telefone: {telefone}")
        
        if not nome and not telefone:
            logger.warning(f"Busca por CPF falhou - Parâmetros vazios - Usuário: {user}")
            log_api_request('POST', '/buscar_cpf', user, 400, "Nome ou telefone não fornecido")
            return jsonify({'error': 'Nome ou telefone não fornecido'}), 400
        
        cadastro = None
        if nome:
            cadastro = Cadastro.query.filter(Cadastro.nome.ilike(nome)).first()
            logger.debug(f"Busca por nome - Usuário: {user} - Nome: {nome} - Encontrado: {cadastro is not None}")
        if telefone and not cadastro:
            cadastro = Cadastro.query.filter_by(telefone=telefone).first()
            logger.debug(f"Busca por telefone - Usuário: {user} - Telefone: {telefone} - Encontrado: {cadastro is not None}")
        
        if cadastro:
            result = {
                'success': True,
                'cpf': cadastro.cpf,
                'nome': cadastro.nome,
                'telefone': cadastro.telefone,
                'assentamento': cadastro.assentamento,
                'estado_id': cadastro.estado_id,
                'municipio_id': cadastro.municipio_id
            }
            
            logger.info(f"Busca por CPF bem-sucedida - Usuário: {user} - CPF encontrado: {cadastro.cpf}")
            log_api_request('POST', '/buscar_cpf', user, 200)
            log_database_operation('READ', 'cadastro', cadastro.id, user)
            
            return jsonify(result)
        
        logger.info(f"Busca por CPF sem resultados - Usuário: {user}")
        log_api_request('POST', '/buscar_cpf', user, 200)
        
        return jsonify({
            'success': False,
            'message': 'Cadastro não encontrado'
        })
    except Exception as e:
        logger.error(f"Erro ao buscar CPF - Usuário: {user} - Erro: {str(e)}")
        log_api_request('POST', '/buscar_cpf', user, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500

@api_bp.route('/buscar_telefone', methods=['POST'])
@login_required
def buscar_telefone():
    user = current_user.username
    logger.info(f"Busca por telefone solicitada - Usuário: {user}")
    
    try:
        data = request.get_json()
        telefone = data.get('telefone')
        
        logger.debug(f"Parâmetros de busca - Usuário: {user} - Telefone: {telefone}")
        
        if not telefone:
            logger.warning(f"Busca por telefone falhou - Telefone não fornecido - Usuário: {user}")
            log_api_request('POST', '/buscar_telefone', user, 400, "Telefone não fornecido")
            return jsonify({'error': 'Telefone não fornecido'}), 400
        
        cadastro = Cadastro.query.filter_by(telefone=telefone).first()
        logger.debug(f"Busca por telefone - Usuário: {user} - Telefone: {telefone} - Encontrado: {cadastro is not None}")
        
        if cadastro:
            result = {
                'success': True,
                'cpf': cadastro.cpf,
                'nome': cadastro.nome,
                'telefone': cadastro.telefone,
                'assentamento': cadastro.assentamento,
                'estado_id': cadastro.estado_id,
                'municipio_id': cadastro.municipio_id
            }
            
            logger.info(f"Busca por telefone bem-sucedida - Usuário: {user} - Telefone: {telefone}")
            log_api_request('POST', '/buscar_telefone', user, 200)
            log_database_operation('READ', 'cadastro', cadastro.id, user)
            
            return jsonify(result)
        
        logger.info(f"Busca por telefone sem resultados - Usuário: {user} - Telefone: {telefone}")
        log_api_request('POST', '/buscar_telefone', user, 200)
        
        return jsonify({
            'success': False,
            'message': 'Cadastro não encontrado'
        })
    except Exception as e:
        logger.error(f"Erro ao buscar telefone - Usuário: {user} - Erro: {str(e)}")
        log_api_request('POST', '/buscar_telefone', user, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500
