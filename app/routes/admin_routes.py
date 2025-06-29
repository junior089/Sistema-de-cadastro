from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models import User, Log, Estado, Municipio, Descricao, Instituicao, SystemStatus
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

@admin_bp.route('/criar_usuario', methods=['GET', 'POST'])
@login_required
def criar_usuario():
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
    if request.method == 'POST':
        tipo_dado = request.form.get('tipo_dado', '').strip().lower()
        nome = request.form.get('nome', '').strip().upper()
        mensagem = ""
        if not tipo_dado or not nome:
            flash("Tipo de dado e nome são obrigatórios!", 'error')
            return render_template('data_manage.html', estados=estados)
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
                return render_template('data_manage.html', estados=estados)
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
            return render_template('data_manage.html', estados=estados)
        db.session.add(log)
        db.session.commit()
        flash(mensagem, 'success')
        return redirect(url_for('admin.gerenciar_dados'))
    return render_template('data_manage.html', estados=estados)

@admin_bp.route('/ver_logs')
@login_required
def ver_logs():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    logs = Log.query.order_by(Log.data_hora.desc()).all()
    return render_template('log_list.html', logs=logs)

@admin_bp.route('/backup/<backup_type>')
@login_required
def create_backup(backup_type='manual'):
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    if backup_type not in ['manual', 'daily', 'weekly', 'monthly']:
        backup_type = 'manual'
    backup_system = current_app.backup_system
    success, message = backup_system.create_backup(backup_type)
    if success:
        log = Log(usuario=current_user.username,
                  acao=f"Backup {backup_type} realizado: {message}")
        db.session.add(log)
        db.session.commit()
        flash(message, 'success')
    else:
        flash(f"Erro ao criar backup: {message}", 'error')
    return redirect(url_for('admin.manage_backups'))

@admin_bp.route('/backups/manage')
@login_required
def manage_backups():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    backup_system = current_app.backup_system
    backups = backup_system.list_backups()
    return render_template('backup_manage.html', backups=backups)

@admin_bp.route('/backup/restore/<path:backup_file>')
@login_required
def restore_backup(backup_file):
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    backup_system = current_app.backup_system
    backup_path = os.path.join(backup_system.backup_dir, backup_file)
    success, message = backup_system.restore_backup(backup_path)
    if success:
        log = Log(usuario=current_user.username,
                  acao=f"Restauração realizada: {message}")
        db.session.add(log)
        db.session.commit()
        flash(message, 'success')
    else:
        flash(f"Erro ao restaurar backup: {message}", 'error')
    return redirect(url_for('admin.manage_backups'))

@admin_bp.route('/backup/download/<path:backup_file>')
@login_required
def download_backup(backup_file):
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    backup_system = current_app.backup_system
    backup_path = os.path.join(backup_system.backup_dir, backup_file)
    try:
        return send_file(backup_path, as_attachment=True)
    except Exception as e:
        flash(f"Erro ao baixar backup: {str(e)}", 'error')
        return redirect(url_for('admin.manage_backups'))

@admin_bp.route('/manage_maintenance', methods=['POST'])
@login_required
def manage_maintenance():
    if current_user.role != 'admin':
        flash("Acesso negado!", 'error')
        return render_template('error.html', mensagem="Acesso negado!", codigo=403), 403
    status = SystemStatus.query.first()
    if not status:
        status = SystemStatus(
            maintenance_mode=False,
            maintenance_message="Sistema em manutenção. Por favor, tente novamente mais tarde.",
            last_updated=datetime.now(UTC)
        )
        db.session.add(status)
    status.maintenance_mode = not status.maintenance_mode
    status.last_updated = datetime.now(UTC)
    status.updated_by = current_user.id
    db.session.commit()
    log = Log(
        usuario=current_user.username,
        acao=f"{'Ativou' if status.maintenance_mode else 'Desativou'} modo de manutenção"
    )
    db.session.add(log)
    db.session.commit()
    flash(
        f"Modo de manutenção {'ativado' if status.maintenance_mode else 'desativado'} com sucesso!",
        'success'
    )
    return redirect(url_for('admin.index_admin'))
