#!/usr/bin/env python3
"""
Script para criar um usuário com role 'senhas'
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app, db
from app.models.user import User

def create_senhas_user():
    """Cria um usuário com role 'senhas'"""
    
    with app.app_context():
        print("🔧 CRIANDO USUÁRIO DE SENHAS")
        print("=" * 50)
        
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(username='SENHAS').first()
        
        if existing_user:
            print("✅ Usuário SENHAS já existe")
            print(f"   ID: {existing_user.id}")
            print(f"   Role: {existing_user.role}")
            return
        
        # Criar novo usuário
        print("1. Criando usuário SENHAS...")
        
        user = User(
            username='SENHAS',
            role='senhas'
        )
        user.password = '123456'
        
        try:
            db.session.add(user)
            db.session.commit()
            
            print("✅ Usuário SENHAS criado com sucesso!")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role}")
            print(f"   Password: 123456")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao criar usuário: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        create_senhas_user()
        print("\n🎉 Usuário de senhas criado com sucesso!")
        print("📋 Credenciais de acesso:")
        print("   Usuário: SENHAS")
        print("   Senha: 123456")
        print("   URL: http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        sys.exit(1) 