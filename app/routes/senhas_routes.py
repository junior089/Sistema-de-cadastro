from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models.cadastro import Cadastro
from app.models.user import User
from app.models.log import Log
from app.utils.logger_config import get_logger, log_api_request, log_database_operation
from datetime import datetime, timedelta
import json

senhas_bp = Blueprint('senhas', __name__)
logger = get_logger('senhas')

@senhas_bp.route('/senhas_tv')
def senhas_tv():
    """Painel de senhas para exibição em TV"""
    logger.info("Painel de TV de senhas acessado")
    
    try:
        # Buscar estatísticas básicas
        total_cadastros = Cadastro.query.count()
        aguardando = Cadastro.query.filter_by(status_chamada='aguardando').count()
        chamados = Cadastro.query.filter_by(status_chamada='chamado').count()
        atendidos = Cadastro.query.filter_by(status_chamada='atendido').count()
        
        stats = {
            'total': total_cadastros,
            'aguardando': aguardando,
            'chamados': chamados,
            'atendidos': atendidos
        }
        
        logger.info(f"Dados do painel TV carregados - Stats: {stats}")
        
        return render_template('senhas_tv.html', stats=stats)
                             
    except Exception as e:
        logger.error(f"Erro ao carregar painel TV: {str(e)}")
        return render_template('senhas_tv.html', stats={})

@senhas_bp.route('/senhas_dashboard')
@login_required
def senhas_dashboard():
    """Dashboard principal para gerenciamento de senhas"""
    if current_user.role not in ['senhas', 'admin']:
        logger.warning(f"Acesso negado ao dashboard de senhas - Usuário: {current_user.username} - Role: {current_user.role}")
        flash('Acesso negado. Você não tem permissão para acessar esta área.', 'danger')
        return redirect(url_for('auth.login'))
    
    logger.info(f"Dashboard de senhas acessado - Usuário: {current_user.username}")
    
    try:
        # Buscar estatísticas
        total_cadastros = Cadastro.query.count()
        aguardando = Cadastro.query.filter_by(status_chamada='aguardando').count()
        chamados = Cadastro.query.filter_by(status_chamada='chamado').count()
        atendidos = Cadastro.query.filter_by(status_chamada='atendido').count()
        
        # Buscar senhas por prioridade
        senhas_normal = Cadastro.listar_por_prioridade(0, current_user.username)
        senhas_alta = Cadastro.listar_por_prioridade(1, current_user.username)
        senhas_urgente = Cadastro.listar_por_prioridade(2, current_user.username)
        
        # Próximas senhas na fila
        proximas_senhas = Cadastro.listar_aguardando_chamada(current_user.username)[:10]
        
        stats = {
            'total': total_cadastros,
            'aguardando': aguardando,
            'chamados': chamados,
            'atendidos': atendidos,
            'normal': len(senhas_normal),
            'alta': len(senhas_alta),
            'urgente': len(senhas_urgente)
        }
        
        logger.info(f"Dados do dashboard carregados - Usuário: {current_user.username} - Stats: {stats}")
        
        return render_template('senhas_dashboard.html',
                             stats=stats,
                             senhas_normal=senhas_normal,
                             senhas_alta=senhas_alta,
                             senhas_urgente=senhas_urgente,
                             proximas_senhas=proximas_senhas)
                             
    except Exception as e:
        logger.error(f"Erro ao carregar dashboard de senhas - Usuário: {current_user.username} - Erro: {str(e)}")
        flash('Erro ao carregar dados do dashboard.', 'danger')
        return render_template('senhas_dashboard.html', stats={}, senhas_normal=[], senhas_alta=[], senhas_urgente=[], proximas_senhas=[])

@senhas_bp.route('/api/senhas/aguardando')
@login_required
def api_senhas_aguardando():
    """API para buscar senhas aguardando chamada"""
    if current_user.role not in ['senhas', 'admin']:
        logger.warning(f"Acesso negado à API de senhas - Usuário: {current_user.username}")
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        senhas = Cadastro.listar_aguardando_chamada(current_user.username)
        result = []
        
        for cadastro in senhas:
            result.append({
                'id': cadastro.id,
                'senha': cadastro.senha_chamada,
                'nome': cadastro.nome,
                'prioridade': cadastro.prioridade,
                'data_hora': cadastro.data_hora.isoformat(),
                'tempo_espera': str(cadastro.tempo_espera()) if cadastro.tempo_espera() else None,
                'observacoes': cadastro.observacoes
            })
        
        logger.info(f"Senhas aguardando retornadas - Usuário: {current_user.username} - Quantidade: {len(result)}")
        log_api_request('GET', '/api/senhas/aguardando', current_user.username, 200)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao buscar senhas aguardando - Usuário: {current_user.username} - Erro: {str(e)}")
        log_api_request('GET', '/api/senhas/aguardando', current_user.username, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500

@senhas_bp.route('/api/senhas/por_prioridade/<int:prioridade>')
@login_required
def api_senhas_por_prioridade(prioridade):
    """API para buscar senhas por prioridade"""
    if current_user.role not in ['senhas', 'admin']:
        logger.warning(f"Acesso negado à API de senhas por prioridade - Usuário: {current_user.username}")
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        senhas = Cadastro.listar_por_prioridade(prioridade, current_user.username)
        result = []
        
        for cadastro in senhas:
            result.append({
                'id': cadastro.id,
                'senha': cadastro.senha_chamada,
                'nome': cadastro.nome,
                'prioridade': cadastro.prioridade,
                'status_chamada': cadastro.status_chamada,
                'data_hora': cadastro.data_hora.isoformat(),
                'observacoes': cadastro.observacoes
            })
        
        logger.info(f"Senhas por prioridade retornadas - Usuário: {current_user.username} - Prioridade: {prioridade} - Quantidade: {len(result)}")
        log_api_request('GET', f'/api/senhas/por_prioridade/{prioridade}', current_user.username, 200)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao buscar senhas por prioridade - Usuário: {current_user.username} - Prioridade: {prioridade} - Erro: {str(e)}")
        log_api_request('GET', f'/api/senhas/por_prioridade/{prioridade}', current_user.username, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500

@senhas_bp.route('/api/senhas/buscar/<senha>')
@login_required
def api_buscar_por_senha(senha):
    """API para buscar cadastro por senha"""
    if current_user.role not in ['senhas', 'admin']:
        logger.warning(f"Acesso negado à busca por senha - Usuário: {current_user.username}")
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        cadastro = Cadastro.buscar_por_senha(senha, current_user.username)
        
        if cadastro:
            result = {
                'id': cadastro.id,
                'senha': cadastro.senha_chamada,
                'nome': cadastro.nome,
                'cpf': cadastro.cpf,
                'telefone': cadastro.telefone,
                'prioridade': cadastro.prioridade,
                'status_chamada': cadastro.status_chamada,
                'data_hora': cadastro.data_hora.isoformat(),
                'observacoes': cadastro.observacoes,
                'senhas_anteriores': cadastro.get_senhas_anteriores()
            }
            
            logger.info(f"Cadastro encontrado por senha - Usuário: {current_user.username} - Senha: {senha}")
            log_api_request('GET', f'/api/senhas/buscar/{senha}', current_user.username, 200)
            
            return jsonify(result)
        else:
            logger.info(f"Cadastro não encontrado por senha - Usuário: {current_user.username} - Senha: {senha}")
            log_api_request('GET', f'/api/senhas/buscar/{senha}', current_user.username, 404)
            
            return jsonify({'error': 'Senha não encontrada'}), 404
            
    except Exception as e:
        logger.error(f"Erro ao buscar por senha - Usuário: {current_user.username} - Senha: {senha} - Erro: {str(e)}")
        log_api_request('GET', f'/api/senhas/buscar/{senha}', current_user.username, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500

@senhas_bp.route('/api/senhas/alterar_prioridade/<int:cadastro_id>', methods=['POST'])
@login_required
def api_alterar_prioridade(cadastro_id):
    """API para alterar prioridade de uma senha"""
    if current_user.role not in ['senhas', 'admin']:
        logger.warning(f"Acesso negado à alteração de prioridade - Usuário: {current_user.username}")
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        data = request.get_json()
        nova_prioridade = data.get('prioridade')
        observacoes = data.get('observacoes')
        
        if nova_prioridade not in [0, 1, 2]:
            logger.warning(f"Prioridade inválida - Usuário: {current_user.username} - Prioridade: {nova_prioridade}")
            return jsonify({'error': 'Prioridade inválida'}), 400
        
        cadastro = Cadastro.query.get_or_404(cadastro_id)
        prioridade_anterior = cadastro.prioridade
        
        cadastro.definir_prioridade(nova_prioridade, observacoes)
        db.session.commit()
        
        # Registrar log
        log = Log(
            usuario=current_user.username,
            acao=f"Alterou prioridade de {prioridade_anterior} para {nova_prioridade} - Senha: {cadastro.senha_chamada}"
        )
        db.session.add(log)
        db.session.commit()
        
        logger.info(f"Prioridade alterada - Usuário: {current_user.username} - Cadastro ID: {cadastro_id} - Prioridade anterior: {prioridade_anterior} - Nova prioridade: {nova_prioridade}")
        log_api_request('POST', f'/api/senhas/alterar_prioridade/{cadastro_id}', current_user.username, 200)
        log_database_operation('UPDATE', 'cadastro', cadastro_id, current_user.username)
        
        return jsonify({
            'success': True,
            'message': f'Prioridade alterada para {["NORMAL", "ALTA", "URGENTE"][nova_prioridade]}',
            'nova_senha': cadastro.senha_chamada
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Erro ao alterar prioridade - Usuário: {current_user.username} - Cadastro ID: {cadastro_id} - Erro: {str(e)}")
        log_api_request('POST', f'/api/senhas/alterar_prioridade/{cadastro_id}', current_user.username, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500

@senhas_bp.route('/api/senhas/estatisticas')
@login_required
def api_estatisticas_senhas():
    """API para estatísticas de senhas"""
    if current_user.role not in ['senhas', 'admin']:
        logger.warning(f"Acesso negado às estatísticas de senhas - Usuário: {current_user.username}")
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        # Estatísticas gerais
        total_senhas = Cadastro.query.filter(Cadastro.senha_chamada.isnot(None)).count()
        senhas_hoje = Cadastro.query.filter(
            Cadastro.data_hora >= hoje,
            Cadastro.senha_chamada.isnot(None)
        ).count()
        senhas_semana = Cadastro.query.filter(
            Cadastro.data_hora >= inicio_semana,
            Cadastro.senha_chamada.isnot(None)
        ).count()
        
        # Por prioridade
        normal = Cadastro.query.filter_by(prioridade=0).count()
        alta = Cadastro.query.filter_by(prioridade=1).count()
        urgente = Cadastro.query.filter_by(prioridade=2).count()
        
        # Por status
        aguardando = Cadastro.query.filter_by(status_chamada='aguardando').count()
        chamados = Cadastro.query.filter_by(status_chamada='chamado').count()
        atendidos = Cadastro.query.filter_by(status_chamada='atendido').count()
        
        stats = {
            'total_senhas': total_senhas,
            'senhas_hoje': senhas_hoje,
            'senhas_semana': senhas_semana,
            'por_prioridade': {
                'normal': normal,
                'alta': alta,
                'urgente': urgente
            },
            'por_status': {
                'aguardando': aguardando,
                'chamados': chamados,
                'atendidos': atendidos
            }
        }
        
        logger.info(f"Estatísticas de senhas retornadas - Usuário: {current_user.username}")
        log_api_request('GET', '/api/senhas/estatisticas', current_user.username, 200)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas de senhas - Usuário: {current_user.username} - Erro: {str(e)}")
        log_api_request('GET', '/api/senhas/estatisticas', current_user.username, 500, str(e))
        return jsonify({'error': 'Erro interno do servidor'}), 500

@senhas_bp.route('/api/tv/senhas')
def api_tv_senhas():
    """API pública para painel de TV - senhas aguardando"""
    logger.info("API TV de senhas acessada")
    
    try:
        senhas = Cadastro.listar_aguardando_chamada()
        result = []
        
        for cadastro in senhas:
            result.append({
                'id': cadastro.id,
                'senha': cadastro.senha_chamada,
                'nome': cadastro.nome,
                'prioridade': cadastro.prioridade,
                'data_hora': cadastro.data_hora.isoformat(),
                'tempo_espera': str(cadastro.tempo_espera()) if cadastro.tempo_espera() else None,
                'observacoes': cadastro.observacoes
            })
        
        logger.info(f"Senhas TV retornadas - Quantidade: {len(result)}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erro ao buscar senhas TV: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@senhas_bp.route('/api/tv/estatisticas')
def api_tv_estatisticas():
    """API pública para painel de TV - estatísticas"""
    logger.info("API TV de estatísticas acessada")
    
    try:
        hoje = datetime.now().date()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        
        # Estatísticas gerais
        total_senhas = Cadastro.query.filter(Cadastro.senha_chamada.isnot(None)).count()
        senhas_hoje = Cadastro.query.filter(
            Cadastro.data_hora >= hoje,
            Cadastro.senha_chamada.isnot(None)
        ).count()
        senhas_semana = Cadastro.query.filter(
            Cadastro.data_hora >= inicio_semana,
            Cadastro.senha_chamada.isnot(None)
        ).count()
        
        # Por status
        aguardando = Cadastro.query.filter_by(status_chamada='aguardando').count()
        chamados = Cadastro.query.filter_by(status_chamada='chamado').count()
        atendidos = Cadastro.query.filter_by(status_chamada='atendido').count()
        
        stats = {
            'total_senhas': total_senhas,
            'senhas_hoje': senhas_hoje,
            'senhas_semana': senhas_semana,
            'por_status': {
                'aguardando': aguardando,
                'chamados': chamados,
                'atendidos': atendidos
            }
        }
        
        logger.info(f"Estatísticas TV retornadas")
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Erro ao buscar estatísticas TV: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor'}), 500 