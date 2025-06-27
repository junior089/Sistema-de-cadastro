from flask import Blueprint, jsonify, Response, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Cadastro, Municipio, Estado, Descricao, instituicao, User, Log
from datetime import datetime, timedelta
import json
import threading
import time

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/stats')
@login_required
def get_stats():
    try:
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio_mes = hoje.replace(day=1)
        hoje_str = hoje.strftime("%Y-%m-%d")
        inicio_semana_str = inicio_semana.strftime("%Y-%m-%d")
        inicio_mes_str = inicio_mes.strftime("%Y-%m-%d")
        today_count = Cadastro.query.filter(Cadastro.data_hora.like(f"{hoje_str}%")).count()
        week_count = Cadastro.query.filter(Cadastro.data_hora >= inicio_semana_str).count()
        month_count = Cadastro.query.filter(Cadastro.data_hora >= inicio_mes_str).count()
        total_count = Cadastro.query.count()
        attended_count = Cadastro.query.filter(Cadastro.atendida == True).count()
        return jsonify({
            'today': today_count,
            'week': week_count,
            'month': month_count,
            'total': total_count,
            'attended': attended_count
        })
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {str(e)}")
        return jsonify({
            'today': 0,
            'week': 0,
            'month': 0,
            'total': 0,
            'attended': 0
        }), 500

@api_bp.route('/events')
@login_required
def events():
    if current_user.role not in ['visor', 'admin']:
        return "Acesso negado!", 403
    notification_queue = current_app.notification_queue
    connected_clients = current_app.connected_clients
    def event_stream():
        client_id = id(threading.current_thread())
        connected_clients.add(client_id)
        try:
            while True:
                try:
                    if not notification_queue.empty():
                        notification = notification_queue.get_nowait()
                        yield f"data: {json.dumps(notification)}\n\n"
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': datetime.now().isoformat()})}\n\n"
                    time.sleep(1)
                except Exception as e:
                    print(f"Erro no event stream: {e}")
                    break
        finally:
            connected_clients.discard(client_id)
    return Response(event_stream(), mimetype='text/event-stream')

@api_bp.route('/api/cadastros')
@login_required
def get_cadastros():
    if current_user.role not in ['visor', 'admin']:
        return jsonify({"error": "Acesso negado"}), 403
    cadastros = Cadastro.query.order_by(Cadastro.data_hora.asc()).all()
    return jsonify([{
        'id': c.id,
        'data_hora': c.data_hora,
        'nome': c.nome,
        'cpf': c.cpf,
        'telefone': c.telefone,
        'assentamento': c.assentamento,
        'municipio': {
            'id': c.municipio.id if c.municipio else None,
            'nome': c.municipio.nome if c.municipio else 'N/A'
        },
        'estado': {
            'id': c.estado.id,
            'nome': c.estado.nome
        },
    } for c in cadastros])

@api_bp.route('/api/cadastro/<int:id>')
@login_required
def get_cadastro(id):
    if current_user.role not in ['visor', 'admin']:
        return jsonify({"error": "Acesso negado"}), 403
    cadastro = Cadastro.query.get_or_404(id)
    return jsonify({
        'id': cadastro.id,
        'data_hora': cadastro.data_hora,
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
            'id': cadastro.estado.id,
            'nome': cadastro.estado.nome
        },
        'descricao': {
            'id': cadastro.descricao.id,
            'nome': cadastro.descricao.nome
        },
        'instituicao': {
            'id': cadastro.instituicao.id,
            'nome': cadastro.instituicao.nome
        },
    })

@api_bp.route('/get_municipios/<int:estado_id>')
@login_required
def get_municipios(estado_id):
    municipios = Municipio.query.filter_by(estado_id=estado_id).all()
    municipios_json = [{'id': municipio.id, 'nome': municipio.nome} for municipio in municipios]
    return jsonify(municipios_json)

@api_bp.route('/buscar_nome', methods=['POST'])
@login_required
def buscar_nome():
    try:
        data = request.get_json()
        cpf = data.get('cpf')
        telefone = data.get('telefone')
        if not cpf and not telefone:
            return jsonify({'error': 'CPF ou telefone não fornecido'}), 400
        cadastro = None
        if cpf:
            cadastro = Cadastro.query.filter_by(cpf=cpf).first()
        if telefone:
            cadastro = Cadastro.query.filter_by(telefone=telefone).first()
        if cadastro:
            return jsonify({
                'success': True,
                'nome': cadastro.nome,
                'cpf': cadastro.cpf,
                'telefone': cadastro.telefone,
                'assentamento': cadastro.assentamento,
                'estado_id': cadastro.estado_id,
                'municipio_id': cadastro.municipio_id
            })
        return jsonify({
            'success': False,
            'message': 'Cadastro não encontrado'
        })
    except Exception as e:
        print(f"Erro ao buscar nome: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@api_bp.route('/buscar_cpf', methods=['POST'])
@login_required
def buscar_cpf():
    try:
        data = request.get_json()
        nome = data.get('nome')
        telefone = data.get('telefone')
        if not nome and not telefone:
            return jsonify({'error': 'Nome ou telefone não fornecido'}), 400
        cadastro = None
        if nome:
            cadastro = Cadastro.query.filter(Cadastro.nome.ilike(nome)).first()
        if telefone:
            cadastro = Cadastro.query.filter_by(telefone=telefone).first()
        if cadastro:
            return jsonify({
                'success': True,
                'cpf': cadastro.cpf,
                'nome': cadastro.nome,
                'telefone': cadastro.telefone,
                'assentamento': cadastro.assentamento,
                'estado_id': cadastro.estado_id,
                'municipio_id': cadastro.municipio_id
            })
        return jsonify({
            'success': False,
            'message': 'Cadastro não encontrado'
        })
    except Exception as e:
        print(f"Erro ao buscar CPF: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@api_bp.route('/buscar_telefone', methods=['POST'])
@login_required
def buscar_telefone():
    try:
        data = request.get_json()
        telefone = data.get('telefone')
        if not telefone:
            return jsonify({'error': 'Telefone não fornecido'}), 400
        cadastro = Cadastro.query.filter_by(telefone=telefone).first()
        if cadastro:
            return jsonify({
                'success': True,
                'cpf': cadastro.cpf,
                'nome': cadastro.nome,
                'telefone': cadastro.telefone,
                'assentamento': cadastro.assentamento,
                'estado_id': cadastro.estado_id,
                'municipio_id': cadastro.municipio_id
            })
        return jsonify({
            'success': False,
            'message': 'Cadastro não encontrado'
        })
    except Exception as e:
        print(f"Erro ao buscar telefone: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500
