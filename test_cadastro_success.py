#!/usr/bin/env python3
"""
Teste para verificar se o cadastro está funcionando
"""

import requests
import json

def test_cadastro_success():
    """Testa se o cadastro está funcionando"""
    
    print("🧪 TESTE DE CADASTRO")
    print("=" * 50)
    
    # URL base da aplicação
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Fazer login
        print("1. Fazendo login...")
        login_data = {
            'username': 'CADASTRADOR',
            'password': '123456'
        }
        
        session = requests.Session()
        response = session.post(f"{base_url}/", data=login_data)
        
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Falha no login - Status: {response.status_code}")
            return
        
        # 2. Testar cadastro
        print("2. Testando cadastro...")
        cadastro_data = {
            'nome': 'TESTE SISTEMA',
            'cpf': '12345678901',
            'telefone': '61992445034',
            'assentamento': 'TESTE ENDEREÇO',
            'estado': '1',
            'municipio': '1',
            'descricao': '1',
            'instituicao': '1'
        }
        
        response = session.post(f"{base_url}/cadastro", data=cadastro_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("   ✅ Cadastro realizado com sucesso!")
                print(f"   📝 Mensagem: {result.get('message')}")
            else:
                print(f"   ❌ Falha no cadastro: {result.get('message')}")
        else:
            print(f"   ❌ Erro no cadastro - Status: {response.status_code}")
            print(f"   📄 Resposta: {response.text}")
        
    except Exception as e:
        print(f"   ❌ Erro no teste: {str(e)}")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_cadastro_success() 