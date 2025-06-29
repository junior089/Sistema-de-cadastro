#!/usr/bin/env python3
"""
Teste completo do sistema de senhas
"""

import requests
import json

def test_sistema_senhas():
    """Testa o sistema completo de senhas"""
    
    print("🧪 TESTE DO SISTEMA DE SENHAS")
    print("=" * 50)
    
    # URL base da aplicação
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Testar login com usuário de senhas
        print("1. Testando login com usuário SENHAS...")
        login_data = {
            'username': 'SENHAS',
            'password': '123456'
        }
        
        session = requests.Session()
        response = session.post(f"{base_url}/", data=login_data)
        
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Falha no login - Status: {response.status_code}")
            return
        
        # 2. Testar acesso ao dashboard de senhas
        print("2. Testando acesso ao dashboard de senhas...")
        response = session.get(f"{base_url}/senhas_dashboard")
        
        if response.status_code == 200:
            print("   ✅ Dashboard de senhas acessível")
        else:
            print(f"   ❌ Erro ao acessar dashboard - Status: {response.status_code}")
            return
        
        # 3. Testar API de senhas aguardando
        print("3. Testando API de senhas aguardando...")
        response = session.get(f"{base_url}/api/senhas/aguardando")
        
        if response.status_code == 200:
            senhas = response.json()
            print(f"   ✅ API funcionando - {len(senhas)} senhas aguardando")
            
            if senhas:
                print(f"   📋 Primeira senha: {senhas[0]['senha']} - {senhas[0]['nome']}")
        else:
            print(f"   ❌ Erro na API - Status: {response.status_code}")
        
        # 4. Testar busca por senha
        print("4. Testando busca por senha...")
        if senhas:
            primeira_senha = senhas[0]['senha']
            response = session.get(f"{base_url}/api/senhas/buscar/{primeira_senha}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Busca funcionando - Senha: {data['senha']} - Nome: {data['nome']}")
            else:
                print(f"   ❌ Erro na busca - Status: {response.status_code}")
        else:
            print("   ⚠️  Nenhuma senha para testar busca")
        
        # 5. Testar estatísticas
        print("5. Testando estatísticas de senhas...")
        response = session.get(f"{base_url}/api/senhas/estatisticas")
        
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Estatísticas funcionando")
            print(f"   📊 Total: {stats['total_senhas']}")
            print(f"   📊 Hoje: {stats['senhas_hoje']}")
            print(f"   📊 Semana: {stats['senhas_semana']}")
        else:
            print(f"   ❌ Erro nas estatísticas - Status: {response.status_code}")
        
        print("\n✅ Teste do sistema de senhas concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    test_sistema_senhas() 