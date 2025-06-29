#!/usr/bin/env python3
"""
Script para testar o painel de TV de senhas
"""

import requests
import json
from datetime import datetime

def test_painel_tv():
    """Testa as APIs do painel de TV"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("=" * 60)
    print("🧪 TESTE DO PAINEL DE TV DE SENHAS")
    print("=" * 60)
    
    # Teste 1: Acesso à página do painel TV
    print("\n1. Testando acesso à página do painel TV...")
    try:
        response = requests.get(f"{base_url}/senhas_tv")
        if response.status_code == 200:
            print("✅ Página do painel TV acessível")
        else:
            print(f"❌ Erro ao acessar página: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
    
    # Teste 2: API de senhas para TV
    print("\n2. Testando API de senhas para TV...")
    try:
        response = requests.get(f"{base_url}/api/tv/senhas")
        if response.status_code == 200:
            senhas = response.json()
            print(f"✅ API de senhas funcionando - {len(senhas)} senhas encontradas")
            if senhas:
                print(f"   Primeira senha: {senhas[0]['senha']} - {senhas[0]['nome']}")
        else:
            print(f"❌ Erro na API de senhas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
    
    # Teste 3: API de estatísticas para TV
    print("\n3. Testando API de estatísticas para TV...")
    try:
        response = requests.get(f"{base_url}/api/tv/estatisticas")
        if response.status_code == 200:
            stats = response.json()
            print("✅ API de estatísticas funcionando")
            print(f"   Total de senhas: {stats.get('total_senhas', 0)}")
            print(f"   Aguardando: {stats.get('por_status', {}).get('aguardando', 0)}")
            print(f"   Chamados: {stats.get('por_status', {}).get('chamados', 0)}")
            print(f"   Atendidos: {stats.get('por_status', {}).get('atendidos', 0)}")
        else:
            print(f"❌ Erro na API de estatísticas: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro de conexão: {str(e)}")
    
    # Teste 4: Verificar se as APIs são públicas (sem autenticação)
    print("\n4. Verificando se as APIs são públicas...")
    try:
        # Teste sem cookies de sessão
        session = requests.Session()
        
        response = session.get(f"{base_url}/api/tv/senhas")
        if response.status_code == 200:
            print("✅ API de senhas é pública (sem autenticação)")
        else:
            print(f"❌ API de senhas requer autenticação: {response.status_code}")
        
        response = session.get(f"{base_url}/api/tv/estatisticas")
        if response.status_code == 200:
            print("✅ API de estatísticas é pública (sem autenticação)")
        else:
            print(f"❌ API de estatísticas requer autenticação: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro ao testar APIs públicas: {str(e)}")
    
    print("\n" + "=" * 60)
    print("📺 INSTRUÇÕES PARA USAR O PAINEL DE TV")
    print("=" * 60)
    print("1. Abra o navegador em tela cheia")
    print("2. Acesse: http://127.0.0.1:5000/senhas_tv")
    print("3. Pressione F11 para modo tela cheia")
    print("4. O painel atualiza automaticamente a cada 10 segundos")
    print("5. Indicador verde no canto superior direito = conexão OK")
    print("6. Indicador vermelho = problema de conexão")
    print("\n🎯 CARACTERÍSTICAS DO PAINEL:")
    print("- Design otimizado para TV com letras grandes")
    print("- Sem botões ou elementos de navegação")
    print("- Atualização automática em tempo real")
    print("- Cores diferentes por prioridade (Normal/Alta/Urgente)")
    print("- Estatísticas em tempo real")
    print("- Relógio e data atualizados")
    print("=" * 60)

if __name__ == "__main__":
    test_painel_tv() 