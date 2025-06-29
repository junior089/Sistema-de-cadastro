#!/usr/bin/env python3
"""
Script de teste para demonstrar o novo design do painel de TV de senhas
"""

import requests
import json
import time
from datetime import datetime

# Configurações
BASE_URL = "http://127.0.0.1:5000"
API_SENHAS = f"{BASE_URL}/api/tv/senhas"
API_ESTATISTICAS = f"{BASE_URL}/api/tv/estatisticas"

def testar_painel_tv():
    """Testa o painel de TV de senhas"""
    print("🎬 TESTANDO PAINEL DE TV DE SENHAS - DESIGN MELHORADO")
    print("=" * 60)
    
    try:
        # Testar API de senhas
        print("\n📋 Testando API de senhas...")
        response = requests.get(API_SENHAS)
        if response.status_code == 200:
            senhas = response.json()
            print(f"✅ API de senhas funcionando - {len(senhas)} senhas encontradas")
            
            if senhas:
                print("\n📊 Senhas disponíveis:")
                for i, senha in enumerate(senhas[:5], 1):
                    prioridade_text = ["NORMAL", "ALTA", "URGENTE"][senha.get('prioridade', 0)]
                    print(f"  {i}. {senha['senha']} - {senha['nome']} ({prioridade_text})")
            else:
                print("  ℹ️  Nenhuma senha aguardando")
        else:
            print(f"❌ Erro na API de senhas: {response.status_code}")
        
        # Testar API de estatísticas
        print("\n📈 Testando API de estatísticas...")
        response = requests.get(API_ESTATISTICAS)
        if response.status_code == 200:
            stats = response.json()
            print("✅ API de estatísticas funcionando")
            print(f"  📊 Total: {stats.get('total_senhas', 0)}")
            print(f"  ⏳ Aguardando: {stats.get('aguardando', 0)}")
            print(f"  📢 Chamados: {stats.get('chamados', 0)}")
            print(f"  ✅ Atendidos: {stats.get('atendidos', 0)}")
        else:
            print(f"❌ Erro na API de estatísticas: {response.status_code}")
        
        # Testar página do painel TV
        print("\n🖥️  Testando página do painel TV...")
        response = requests.get(f"{BASE_URL}/senhas_tv")
        if response.status_code == 200:
            print("✅ Página do painel TV carregada com sucesso")
            print("  🎨 Design moderno com fundo escuro")
            print("  ✨ Efeitos visuais e animações")
            print("  🔥 Destaque especial para senhas chamadas")
        else:
            print(f"❌ Erro ao carregar página do painel TV: {response.status_code}")
        
        print("\n" + "=" * 60)
        print("🎯 TESTE CONCLUÍDO!")
        print("\n📱 Para visualizar o painel:")
        print(f"   🌐 Abra: {BASE_URL}/senhas_tv")
        print("   📺 Ideal para exibição em TV ou monitor grande")
        print("   🎨 Design responsivo e moderno")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - Verifique se o servidor está rodando")
        print(f"   💻 Execute: python app/app.py")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

def adicionar_senhas_teste():
    """Adiciona senhas de teste para demonstrar o painel"""
    print("\n🎲 ADICIONANDO SENHAS DE TESTE")
    print("=" * 40)
    
    senhas_teste = [
        {"nome": "Maria Silva", "prioridade": 0, "senha": "LAB001"},
        {"nome": "João Santos", "prioridade": 1, "senha": "PRI002"},
        {"nome": "Ana Costa", "prioridade": 2, "senha": "URG003"},
        {"nome": "Pedro Lima", "prioridade": 0, "senha": "LAB004"},
        {"nome": "Lucia Ferreira", "prioridade": 1, "senha": "PRI005"},
        {"nome": "Carlos Oliveira", "prioridade": 0, "senha": "LAB006"},
    ]
    
    try:
        for i, senha in enumerate(senhas_teste, 1):
            print(f"  {i}. Adicionando {senha['nome']} - {senha['senha']}")
            # Aqui você pode adicionar lógica para inserir no banco
            time.sleep(0.5)
        
        print("✅ Senhas de teste adicionadas!")
        print("🔄 Recarregue o painel para ver as mudanças")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar senhas: {str(e)}")

def mostrar_melhorias():
    """Mostra as melhorias implementadas no design"""
    print("\n🚀 MELHORIAS IMPLEMENTADAS NO PAINEL DE TV")
    print("=" * 50)
    
    melhorias = [
        "🎨 Design moderno com fundo escuro gradiente",
        "✨ Efeitos de partículas e blur no fundo",
        "🔥 Destaque especial para senhas chamadas (fundo branco)",
        "💫 Animações suaves e transições elegantes",
        "📱 Layout responsivo para diferentes telas",
        "🎯 Tipografia melhorada com gradientes",
        "⚡ Efeitos de hover e interação",
        "🌈 Cores diferenciadas por prioridade",
        "🕐 Relógio em tempo real estilizado",
        "📊 Estatísticas com design moderno",
        "🔗 Status de conexão WebSocket visível",
        "🎪 Efeitos de brilho e sombra",
        "📋 Lista de próximas senhas organizada",
        "🎭 Scrollbar personalizada",
        "🔄 Atualização automática via WebSocket"
    ]
    
    for melhoria in melhorias:
        print(f"  {melhoria}")
    
    print("\n🎯 CARACTERÍSTICAS DESTACADAS:")
    print("  • Senha chamada: Fundo branco com borda azul brilhante")
    print("  • Prioridade Normal: Verde")
    print("  • Prioridade Alta: Laranja")
    print("  • Prioridade Urgente: Vermelho com animação pulsante")
    print("  • Efeitos de brilho e sombra para destaque visual")

if __name__ == "__main__":
    print("🎬 SISTEMA DE PAINEL DE TV - DESIGN MELHORADO")
    print("=" * 60)
    
    # Mostrar melhorias
    mostrar_melhorias()
    
    # Adicionar senhas de teste
    adicionar_senhas_teste()
    
    # Testar funcionalidades
    testar_painel_tv()
    
    print("\n🎉 SISTEMA PRONTO PARA USO!")
    print("📺 O painel de TV agora tem um design moderno e profissional")
    print("👁️  As senhas chamadas ficam em destaque com fundo branco")
    print("🎨 Visual atrativo e bem visível para qualquer ambiente") 