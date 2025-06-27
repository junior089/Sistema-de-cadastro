from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User, Log

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].upper().strip()
        password = request.form['password'].strip()
        print(f"Tentando login: username={username} password={password}")
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('login.html')
        user = User.query.filter_by(username=username).first()
        print(f"Resultado da busca no banco: {user}")
        if user and user.password == password:
            login_user(user)
            print(f"Login bem-sucedido para {user.username} (id={user.id})")
            try:
                log = Log(usuario=user.username, acao="Login realizado")
                db.session.add(log)
                db.session.commit()
            except Exception as e:
                print(f"Erro ao registrar log: {e}")
            if user.role == 'admin':
                return redirect(url_for('admin.index_admin'))
            elif user.role == 'visor':
                return redirect(url_for('cadastro.ver_cadastros'))
            else:
                return redirect(url_for('cadastro.index_cadastro'))
        else:
            flash('Credenciais inválidas! Tente novamente.', 'danger')
            return render_template('login.html')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        log = Log(usuario=current_user.username, acao="Logout")
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar logout: {e}")
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/trocar_senha', methods=['GET', 'POST'])
@login_required
def trocar_senha():
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        user = User.query.get(current_user.id)
        if user and user.password == senha_atual:
            user.password = nova_senha
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            log = Log(usuario=current_user.username, acao="Alteração de senha")
            db.session.add(log)
            db.session.commit()
            return redirect(url_for('cadastro.index_cadastro'))
        else:
            flash('Senha atual incorreta!', 'danger')
    return render_template('trocar_senha.html')
