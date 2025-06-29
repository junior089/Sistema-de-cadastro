from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models.user import User
from app.models.log import Log
from app.utils.logger_config import get_logger, log_security_event, log_api_request
from sqlalchemy import func

auth_bp = Blueprint('auth', __name__)
logger = get_logger('auth')

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].upper().strip()
        password = request.form['password'].strip()
        ip_address = request.remote_addr
        
        logger.info(f"Tentativa de login - Usuário: {username} - IP: {ip_address}")
        print(f"Tentando login: username={username} password={password}")
        
        if not username or not password:
            logger.warning(f"Login falhou - Campos vazios - Usuário: {username} - IP: {ip_address}")
            flash('Por favor, preencha todos os campos.', 'danger')
            return render_template('login.html')
        
        try:
            user = User.query.filter(func.upper(User.username) == username).first()
            print(f"Resultado da busca no banco: {user}")
            
            if user and user.verify_password(password):
                login_user(user)
                logger.info(f"Login bem-sucedido - Usuário: {user.username} (ID: {user.id}) - IP: {ip_address}")
                print(f"Login bem-sucedido para {user.username} (id={user.id})")
                
                try:
                    log = Log(usuario=user.username, acao="Login realizado")
                    db.session.add(log)
                    db.session.commit()
                    logger.debug(f"Log de login registrado no banco para usuário: {user.username}")
                except Exception as e:
                    logger.error(f"Erro ao registrar log de login: {str(e)}")
                    print(f"Erro ao registrar log: {e}")
                
                log_security_event("LOGIN_SUCCESS", user.username, f"IP: {ip_address}", ip_address)
                
                if user.role == 'admin':
                    logger.info(f"Redirecionando admin {user.username} para dashboard")
                    return redirect(url_for('admin.index_admin'))
                elif user.role == 'visor':
                    logger.info(f"Redirecionando visor {user.username} para visualização")
                    return redirect(url_for('cadastro.ver_cadastros'))
                elif user.role == 'senhas':
                    logger.info(f"Redirecionando usuário de senhas {user.username} para dashboard de senhas")
                    return redirect(url_for('senhas.senhas_dashboard'))
                else:
                    logger.info(f"Redirecionando cadastrador {user.username} para cadastro")
                    return redirect(url_for('cadastro.index_cadastro'))
            else:
                logger.warning(f"Login falhou - Credenciais inválidas - Usuário: {username} - IP: {ip_address}")
                flash('Credenciais inválidas! Tente novamente.', 'danger')
                log_security_event("LOGIN_FAILED", username, "Credenciais inválidas", ip_address)
                return render_template('login.html')
                
        except Exception as e:
            logger.error(f"Erro durante processo de login: {str(e)}")
            flash('Erro interno do sistema. Tente novamente.', 'danger')
            return render_template('login.html')
    
    logger.debug("Página de login acessada via GET")
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    ip_address = request.remote_addr
    
    logger.info(f"Logout solicitado - Usuário: {username} - IP: {ip_address}")
    
    try:
        log = Log(usuario=username, acao="Logout")
        db.session.add(log)
        db.session.commit()
        logger.debug(f"Log de logout registrado no banco para usuário: {username}")
    except Exception as e:
        logger.error(f"Erro ao registrar log de logout: {str(e)}")
        print(f"Erro ao registrar logout: {e}")
    
    logout_user()
    log_security_event("LOGOUT", username, f"IP: {ip_address}", ip_address)
    
    logger.info(f"Logout realizado com sucesso - Usuário: {username}")
    return redirect(url_for('auth.login'))

@auth_bp.route('/trocar_senha', methods=['GET', 'POST'])
@login_required
def trocar_senha():
    username = current_user.username
    ip_address = request.remote_addr
    
    if request.method == 'POST':
        logger.info(f"Troca de senha solicitada - Usuário: {username} - IP: {ip_address}")
        
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        
        try:
            user = User.query.get(current_user.id)
            if user and user.verify_password(senha_atual):
                user.password = nova_senha
                db.session.commit()
                
                logger.info(f"Senha alterada com sucesso - Usuário: {username}")
                flash('Senha alterada com sucesso!', 'success')
                
                try:
                    log = Log(usuario=username, acao="Alteração de senha")
                    db.session.add(log)
                    db.session.commit()
                    logger.debug(f"Log de alteração de senha registrado para usuário: {username}")
                except Exception as e:
                    logger.error(f"Erro ao registrar log de alteração de senha: {str(e)}")
                
                log_security_event("PASSWORD_CHANGE", username, "Senha alterada com sucesso", ip_address)
                return redirect(url_for('cadastro.index_cadastro'))
            else:
                logger.warning(f"Falha na troca de senha - Senha atual incorreta - Usuário: {username} - IP: {ip_address}")
                flash('Senha atual incorreta!', 'danger')
                log_security_event("PASSWORD_CHANGE_FAILED", username, "Senha atual incorreta", ip_address)
        except Exception as e:
            logger.error(f"Erro durante troca de senha: {str(e)}")
            flash('Erro interno do sistema. Tente novamente.', 'danger')
    
    logger.debug(f"Página de troca de senha acessada - Usuário: {username}")
    return render_template('user_password_change.html')
