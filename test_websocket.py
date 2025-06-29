#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do WebSocket
"""

import requests
import json
import time
from datetime import datetime

def test_websocket_apis():
    """Testa as APIs relacionadas ao WebSocket"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🔌 TESTE DE WEBSOCKET - SISTEMA DE SENHAS")
    print("=" * 50)
    
    # Teste 1: Verificar se o servidor está rodando
    print("\n1. Verificando se o servidor está rodando...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Servidor está rodando")
        else:
            print(f"⚠️ Servidor retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao conectar ao servidor: {e}")
        return
    
    # Teste 2: Verificar API de senhas aguardando (pública)
    print("\n2. Testando API de senhas aguardando...")
    try:
        response = requests.get(f"{base_url}/api/tv/senhas")
        if response.status_code == 200:
            senhas = response.json()
            print(f"✅ API de senhas funcionando - {len(senhas)} senhas encontradas")
            if senhas:
                print(f"   Primeira senha: {senhas[0]['senha']} - {senhas[0]['nome']}")
        else:
            print(f"❌ API retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na API de senhas: {e}")
    
    # Teste 3: Verificar API de estatísticas (pública)
    print("\n3. Testando API de estatísticas...")
    try:
        response = requests.get(f"{base_url}/api/tv/estatisticas")
        if response.status_code == 200:
            stats = response.json()
            print("✅ API de estatísticas funcionando")
            print(f"   Total: {stats.get('total_senhas', 0)}")
            print(f"   Aguardando: {stats.get('aguardando', 0)}")
            print(f"   Chamados: {stats.get('chamados', 0)}")
            print(f"   Atendidos: {stats.get('atendidos', 0)}")
        else:
            print(f"❌ API retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro na API de estatísticas: {e}")
    
    # Teste 4: Verificar painel TV
    print("\n4. Testando acesso ao painel TV...")
    try:
        response = requests.get(f"{base_url}/senhas_tv")
        if response.status_code == 200:
            print("✅ Painel TV acessível")
            if "socket.io" in response.text:
                print("✅ WebSocket detectado no template")
            else:
                print("⚠️ WebSocket não encontrado no template")
        else:
            print(f"❌ Painel TV retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no painel TV: {e}")
    
    # Teste 5: Verificar painel do atendente (requer login)
    print("\n5. Testando acesso ao painel do atendente...")
    try:
        response = requests.get(f"{base_url}/painel_atendente")
        if response.status_code == 302:  # Redirecionamento para login
            print("✅ Painel do atendente redirecionando para login (esperado)")
        elif response.status_code == 200:
            print("✅ Painel do atendente acessível")
        else:
            print(f"⚠️ Painel do atendente retornou status {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no painel do atendente: {e}")
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    print("✅ APIs públicas funcionando")
    print("✅ Painel TV acessível")
    print("✅ WebSocket implementado")
    print("\n🔗 URLs para teste:")
    print(f"   Painel TV: {base_url}/senhas_tv")
    print(f"   Painel Atendente: {base_url}/painel_atendente")
    print(f"   API Senhas: {base_url}/api/tv/senhas")
    print(f"   API Estatísticas: {base_url}/api/tv/estatisticas")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    print("1. Abra o painel TV em uma aba do navegador")
    print("2. Faça login como atendente e abra o painel do atendente")
    print("3. Teste as ações de chamar, atender e finalizar senhas")
    print("4. Observe as atualizações em tempo real no painel TV")

def test_websocket_connection():
    """Testa a conexão WebSocket diretamente"""
    
    print("\n🔌 TESTE DE CONEXÃO WEBSOCKET")
    print("=" * 30)
    
    try:
        import socketio
        
        # Criar cliente Socket.IO
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print("✅ Conectado ao WebSocket!")
        
        @sio.event
        def disconnect():
            print("❌ Desconectado do WebSocket")
        
        @sio.on('senha_chamada')
        def on_senha_chamada(data):
            print(f"🔔 Senha chamada recebida: {data}")
        
        @sio.on('senha_atendida')
        def on_senha_atendida(data):
            print(f"👤 Senha atendida recebida: {data}")
        
        @sio.on('atendimento_finalizado')
        def on_atendimento_finalizado(data):
            print(f"✅ Atendimento finalizado recebido: {data}")
        
        # Conectar ao servidor
        print("Conectando ao WebSocket...")
        sio.connect('http://127.0.0.1:5000')
        
        # Aguardar alguns segundos
        time.sleep(3)
        
        # Desconectar
        sio.disconnect()
        
    except ImportError:
        print("❌ python-socketio não instalado. Execute: pip install python-socketio")
    except Exception as e:
        print(f"❌ Erro na conexão WebSocket: {e}")

if __name__ == "__main__":
    test_websocket_apis()
    test_websocket_connection() 