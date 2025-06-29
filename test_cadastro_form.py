#!/usr/bin/env python3
"""
Script de teste para verificar o formulário de cadastro
"""

import requests
import json
from datetime import datetime

def test_cadastro_form():
    """Testa o formulário de cadastro"""
    
    print("🧪 TESTE DO FORMULÁRIO DE CADASTRO")
    print("=" * 50)
    
    # URL base da aplicação
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Testar se a página de cadastro está acessível
        print("1. Testando acesso à página de cadastro...")
        response = requests.get(f"{base_url}/index_cadastro")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Página de cadastro acessível")
            
            # Verificar se o formulário está presente
            if 'cadastroForm' in response.text:
                print("   ✅ Formulário encontrado no HTML")
            else:
                print("   ❌ Formulário NÃO encontrado no HTML")
                
            # Verificar se o botão está presente
            if 'submit-button' in response.text:
                print("   ✅ Botão de submit encontrado no HTML")
            else:
                print("   ❌ Botão de submit NÃO encontrado no HTML")
                
            # Verificar se o validators.js está sendo carregado
            if 'validators.js' in response.text:
                print("   ✅ validators.js está sendo carregado")
            else:
                print("   ❌ validators.js NÃO está sendo carregado")
                
        else:
            print("   ❌ Página de cadastro não acessível")
            print(f"   Resposta: {response.text[:200]}...")
            return
        
        # 2. Testar se o usuário está logado (simular login)
        print("\n2. Testando autenticação...")
        
        # Primeiro, tentar fazer login com o usuário CADASTRADOR
        login_data = {
            'username': 'CADASTRADOR',
            'password': '123456'
        }
        
        session = requests.Session()
        login_response = session.post(f"{base_url}/", data=login_data)
        
        if login_response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print("   ❌ Falha no login")
            print(f"   Status: {login_response.status_code}")
            return
        
        # 3. Testar acesso à página de cadastro com sessão
        print("\n3. Testando acesso à página de cadastro com sessão...")
        cadastro_response = session.get(f"{base_url}/index_cadastro")
        
        if cadastro_response.status_code == 200:
            print("   ✅ Página de cadastro acessível com sessão")
        else:
            print("   ❌ Página de cadastro não acessível com sessão")
            print(f"   Status: {cadastro_response.status_code}")
            return
        
        # 4. Testar envio de formulário
        print("\n4. Testando envio de formulário...")
        
        form_data = {
            'nome': 'TESTE USUARIO',
            'cpf': '12345678901',
            'telefone': '61992445034',
            'assentamento': 'TESTE ASSENTAMENTO',
            'estado': '1',
            'descricao': '1',
            'instituicao': '1'
        }
        
        cadastro_post_response = session.post(f"{base_url}/cadastro", data=form_data)
        print(f"   Status: {cadastro_post_response.status_code}")
        
        try:
            result = cadastro_post_response.json()
            print(f"   Resposta: {result}")
            
            if result.get('success'):
                print("   ✅ Cadastro realizado com sucesso!")
            else:
                print(f"   ❌ Falha no cadastro: {result.get('message', 'Erro desconhecido')}")
        except:
            print(f"   ❌ Resposta não é JSON válido: {cadastro_post_response.text[:200]}...")
        
        print("\n" + "=" * 50)
        print("✅ Teste concluído!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Verifique se o Flask está rodando em http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    test_cadastro_form() 