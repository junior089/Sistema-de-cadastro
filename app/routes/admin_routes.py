from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models import SystemStatus
from app.models.log import Log
from app.models.estado import Estado
from app.models.municipio import Municipio
from app.models.descricao import Descricao
from app.models.instituicao import Instituicao
from app.models.cadastro import Cadastro
from datetime import datetime, UTC
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/index_admin')
@login_required
def index_admin():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    users = User.query.all()
    status = SystemStatus.query.first()
    return render_template('admin_dashboard.html', users=users, status=status)

@admin_bp.route('/gerenciar_usuarios', methods=['GET', 'POST'])
@login_required
def gerenciar_usuarios():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    users = User.query.all()
    return render_template('user_manage.html', users=users)

@admin_bp.route('/create_user', methods=['GET', 'POST'])
@login_required
def create_user():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    if request.method == 'POST':
        novo_usuario = request.form.get('username', '').strip().upper()
        nova_senha = request.form.get('password', '').strip()
        novo_role = request.form.get('role', '').strip().lower()
        if not novo_usuario or not nova_senha or not novo_role:
            flash("Nome de usuário, senha e perfil são obrigatórios!", 'error')
            return render_template('user_create.html')
        if len(novo_usuario) < 3 or len(nova_senha) < 4:
            flash("Usuário deve ter pelo menos 3 letras e senha pelo menos 4 caracteres.", 'error')
            return render_template('user_create.html')
        if not novo_role in ['admin', 'cadastrador', 'visor']:
            flash("Perfil inválido!", 'error')
            return render_template('user_create.html')
        if User.query.filter_by(username=novo_usuario).first():
            flash("Usuário já existe!", 'error')
            return render_template('user_create.html')
        user = User(username=novo_usuario, password=nova_senha, role=novo_role)
        db.session.add(user)
        db.session.commit()
        log = Log(usuario=current_user.username, acao=f"Criação de usuário: {novo_usuario}")
        db.session.add(log)
        db.session.commit()
        flash(f"Usuário '{novo_usuario}' criado com sucesso!", 'success')
        return redirect(url_for('admin.index_admin'))
    return render_template('user_create.html')

@admin_bp.route('/editar_usuario/<int:user_id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(user_id):
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    user = User.query.get(user_id)
    if not user:
        flash("Usuário não encontrado!", 'error')
        return render_template('error.html', mensagem="Usuário não encontrado!", codigo=404), 404
    if request.method == 'POST':
        username = request.form.get('username', '').strip().upper()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip().lower()
        if not username or not password or not role:
            flash("Todos os campos são obrigatórios!", 'error')
            return render_template('admin_dashboard.html', action='editar', user=user)
        if len(username) < 3 or len(password) < 4:
            flash("Usuário deve ter pelo menos 3 letras e senha pelo menos 4 caracteres.", 'error')
            return render_template('admin_dashboard.html', action='editar', user=user)
        if not role in ['admin', 'cadastrador', 'visor']:
            flash("Perfil inválido!", 'error')
            return render_template('admin_dashboard.html', action='editar', user=user)
        user.username = username
        user.password = password
        user.role = role
        db.session.commit()
        log = Log(usuario=current_user.username, acao=f"Editou usuário: {user.username}")
        db.session.add(log)
        db.session.commit()
        flash(f"Usuário '{user.username}' atualizado com sucesso!", 'success')
        return redirect(url_for('admin.index_admin'))
    return render_template('admin_dashboard.html', action='editar', user=user)

@admin_bp.route('/editar_senha/<int:user_id>', methods=['POST'])
@login_required
def editar_senha(user_id):
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    user = User.query.get(user_id)
    if not user:
        flash("Usuário não encontrado!", 'error')
        return render_template('error.html', mensagem="Usuário não encontrado!", codigo=404), 404
    if request.method == 'POST':
        nova_senha = request.form.get('password', '').strip()
        if not nova_senha or len(nova_senha) < 4:
            flash("Senha deve ter pelo menos 4 caracteres.", 'error')
            return render_template('user_password_edit.html', user=user)
        user.password = nova_senha
        db.session.commit()
        log = Log(usuario=current_user.username, acao=f"Alterou a senha de {user.username}")
        db.session.add(log)
        db.session.commit()
        flash(f"Senha de '{user.username}' alterada com sucesso!", 'success')
        return redirect(url_for('admin.index_admin'))
    return render_template('user_password_edit.html', user=user)

@admin_bp.route('/deletar_usuario/<int:user_id>', methods=['POST'])
@login_required
def deletar_usuario(user_id):
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    user = User.query.get(user_id)
    if not user:
        flash("Usuário não encontrado!", 'error')
        return render_template('error.html', mensagem="Usuário não encontrado!", codigo=404), 404
    # Remove a verificação de cadastros vinculados: permite deletar o usuário mesmo se houver cadastros com atendente_id
    db.session.delete(user)
    db.session.commit()
    log = Log(usuario=current_user.username, acao=f"Deletou usuário: {user.username}")
    db.session.add(log)
    db.session.commit()
    flash(f"Usuário '{user.username}' deletado com sucesso!", 'success')
    return redirect(url_for('admin.index_admin'))

@admin_bp.route('/gerenciar_dados', methods=['GET', 'POST'])
@login_required
def gerenciar_dados():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    estados = Estado.query.all()
    municipios = Municipio.query.all()
    descricoes = Descricao.query.all()
    instituicoes = Instituicao.query.all()
    if request.method == 'POST':
        tipo_dado = request.form.get('tipo_dado', '').strip().lower()
        nome = request.form.get('nome', '').strip().upper()
        mensagem = ""
        if not tipo_dado or not nome:
            flash("Tipo de dado e nome são obrigatórios!", 'error')
            return render_template('data_manage.html', estados=estados, municipios=municipios, descricoes=descricoes, instituicoes=instituicoes)
        if tipo_dado == 'estado':
            novo_estado = Estado(nome=nome)
            db.session.add(novo_estado)
            db.session.commit()
            mensagem = f"Estado '{nome}' adicionado com sucesso!"
            log = Log(usuario=current_user.username, acao=f"Adicionou estado: {nome}")
        elif tipo_dado == 'municipio':
            estado_id = request.form.get('estado_id', '').strip()
            if not estado_id:
                flash("Estado é obrigatório para município!", 'error')
                return render_template('data_manage.html', estados=estados, municipios=municipios, descricoes=descricoes, instituicoes=instituicoes)
            novo_municipio = Municipio(nome=nome, estado_id=estado_id)
            db.session.add(novo_municipio)
            db.session.commit()
            estado = Estado.query.get(estado_id)
            mensagem = f"Município '{nome}' adicionado com sucesso ao estado {estado.nome}!"
            log = Log(usuario=current_user.username, acao=f"Adicionou município: {nome} ao estado {estado.nome}")
        elif tipo_dado == 'descricao':
            novo_descricao = Descricao(nome=nome)
            db.session.add(novo_descricao)
            db.session.commit()
            mensagem = f"Descrição '{nome}' adicionada com sucesso!"
            log = Log(usuario=current_user.username, acao=f"Adicionou descricao: {nome}")
        elif tipo_dado == 'instituicao':
            novo_instituicao = Instituicao(nome=nome)
            db.session.add(novo_instituicao)
            db.session.commit()
            mensagem = f"Instituição '{nome}' adicionada com sucesso!"
            log = Log(usuario=current_user.username, acao=f"Adicionou instituicao: {nome}")
        else:
            flash("Tipo de dado inválido!", 'error')
            return render_template('data_manage.html', estados=estados, municipios=municipios, descricoes=descricoes, instituicoes=instituicoes)
        db.session.add(log)
        db.session.commit()
        flash(mensagem, 'success')
        return redirect(url_for('admin.gerenciar_dados'))
    return render_template('data_manage.html', estados=estados, municipios=municipios, descricoes=descricoes, instituicoes=instituicoes)

@admin_bp.route('/view_logs')
@login_required
def view_logs():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    logs = Log.query.order_by(Log.data_hora.desc()).limit(100).all()
    return render_template('log_list.html', logs=logs)

@admin_bp.route('/backup', methods=['POST'])
@login_required
def backup():
    if current_user.role != 'admin':
        return jsonify({"success": False, "message": "Acesso negado!"}), 403
    try:
        backup_system = current_app.config.get('BACKUP_SYSTEM')
        if backup_system:
            success, message = backup_system.create_backup('manual')
            if success:
                log = Log(usuario=current_user.username, acao="Backup manual criado")
                db.session.add(log)
                db.session.commit()
                return jsonify({"success": True, "message": message})
            else:
                return jsonify({"success": False, "message": message})
        else:
            return jsonify({"success": False, "message": "Sistema de backup não disponível"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Erro ao criar backup: {str(e)}"})

@admin_bp.route('/manage_backups')
@login_required
def manage_backups():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    try:
        backup_system = current_app.config.get('BACKUP_SYSTEM')
        if backup_system:
            backups = backup_system.list_backups()
        else:
            backups = []
        return render_template('manage_backups.html', backups=backups)
    except Exception as e:
        flash(f"Erro ao carregar backups: {str(e)}", 'error')
        return render_template('manage_backups.html', backups=[])

@admin_bp.route('/toggle_maintenance', methods=['POST'])
@login_required
def toggle_maintenance():
    if current_user.role != 'admin':
        return jsonify({"success": False, "message": "Acesso negado!"}), 403
    
    try:
        status = SystemStatus.query.first()
        if not status:
            status = SystemStatus()
            db.session.add(status)
        
        status.maintenance_mode = not status.maintenance_mode
        status.last_update = datetime.now(UTC)
        
        if status.maintenance_mode:
            status.maintenance_message = "Sistema em manutenção. Por favor, tente novamente mais tarde."
        
        db.session.commit()
        
        log = Log(
            usuario=current_user.username, 
            acao=f"{'Ativou' if status.maintenance_mode else 'Desativou'} modo manutenção"
        )
        db.session.add(log)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "maintenance_mode": status.maintenance_mode,
            "message": f"Modo manutenção {'ativado' if status.maintenance_mode else 'desativado'} com sucesso!"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Erro: {str(e)}"}), 500
