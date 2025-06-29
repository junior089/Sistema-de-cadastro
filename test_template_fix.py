#!/usr/bin/env python3
"""
Teste para verificar se o template está funcionando
"""

import requests
import json

def test_template_fix():
    """Testa se o template está funcionando"""
    
    print("🧪 TESTE DO TEMPLATE CORRIGIDO")
    print("=" * 50)
    
    # URL base da aplicação
    base_url = "http://127.0.0.1:5000"
    
    try:
        # 1. Fazer login como visor
        print("1. Fazendo login como visor...")
        login_data = {
            'username': 'LUKAS',
            'password': '12345'
        }
        
        session = requests.Session()
        response = session.post(f"{base_url}/", data=login_data)
        
        if response.status_code == 200:
            print("   ✅ Login realizado com sucesso")
        else:
            print(f"   ❌ Falha no login - Status: {response.status_code}")
            return
        
        # 2. Testar acesso à página de visualização
        print("2. Testando acesso à página de visualização...")
        response = session.get(f"{base_url}/ver_cadastros")
        
        if response.status_code == 200:
            print("   ✅ Página de visualização acessível")
            
            # Verificar se não há erro de template
            if "data_hora.split" not in response.text:
                print("   ✅ Template corrigido - sem erro de split")
            else:
                print("   ❌ Template ainda com erro de split")
                
        else:
            print(f"   ❌ Erro ao acessar página - Status: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}...")
        
        print("\n✅ Teste concluído!")
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")

if __name__ == "__main__":
    test_template_fix() 