#!/usr/bin/env python3
"""
Script para adicionar senhas de teste para demonstrar o WebSocket
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app
from app import db
from app.models.cadastro import Cadastro
from app.models.municipio import Municipio
from app.models.estado import Estado
from app.models.descricao import Descricao
from app.models.instituicao import Instituicao
from app.models.user import User
from app.utils.logger_config import get_logger

logger = get_logger('teste_websocket')

def criar_dados_teste():
    """Cria dados de teste para demonstrar o WebSocket"""
    
    with app.app_context():
        try:
            # Verificar se já existem dados de teste
            if Cadastro.query.count() > 0:
                print("⚠️ Já existem cadastros no banco. Pulando criação de dados de teste.")
                return
            
            print("🔧 Criando dados de teste para WebSocket...")
            
            # Criar estado e município se não existirem
            estado = Estado.query.filter_by(nome='Distrito Federal').first()
            if not estado:
                estado = Estado(nome='Distrito Federal')
                db.session.add(estado)
                db.session.commit()
                print("✅ Estado criado: Distrito Federal")
            
            municipio = Municipio.query.filter_by(nome='Brasília').first()
            if not municipio:
                municipio = Municipio(nome='Brasília', estado_id=estado.id)
                db.session.add(municipio)
                db.session.commit()
                print("✅ Município criado: Brasília")
            
            # Criar descrição se não existir
            descricao = Descricao.query.filter_by(nome='Assistência Técnica').first()
            if not descricao:
                descricao = Descricao(nome='Assistência Técnica')
                db.session.add(descricao)
                db.session.commit()
                print("✅ Descrição criada: Assistência Técnica")
            
            # Criar instituição se não existir
            instituicao = Instituicao.query.filter_by(nome='INCRA').first()
            if not instituicao:
                instituicao = Instituicao(nome='INCRA')
                db.session.add(instituicao)
                db.session.commit()
                print("✅ Instituição criada: INCRA")
            
            # Lista de pessoas para teste
            pessoas_teste = [
                {
                    'nome': 'Maria Silva Santos',
                    'cpf': '12345678901',
                    'telefone': '(61) 99999-1111',
                    'assentamento': 'Assentamento Boa Vista',
                    'prioridade': 0
                },
                {
                    'nome': 'Ana Oliveira Costa',
                    'cpf': '12345678902',
                    'telefone': '(61) 99999-2222',
                    'assentamento': 'Assentamento Santa Fé',
                    'prioridade': 1
                },
                {
                    'nome': 'Joana Pereira Lima',
                    'cpf': '12345678903',
                    'telefone': '(61) 99999-3333',
                    'assentamento': 'Assentamento Nova Esperança',
                    'prioridade': 2
                },
                {
                    'nome': 'Lucia Ferreira Alves',
                    'cpf': '12345678904',
                    'telefone': '(61) 99999-4444',
                    'assentamento': 'Assentamento São João',
                    'prioridade': 0
                },
                {
                    'nome': 'Rosa Mendes Souza',
                    'cpf': '12345678905',
                    'telefone': '(61) 99999-5555',
                    'assentamento': 'Assentamento Campo Verde',
                    'prioridade': 1
                },
                {
                    'nome': 'Carmen Rodrigues Silva',
                    'cpf': '12345678906',
                    'telefone': '(61) 99999-6666',
                    'assentamento': 'Assentamento Vista Alegre',
                    'prioridade': 0
                },
                {
                    'nome': 'Isabela Costa Santos',
                    'cpf': '12345678907',
                    'telefone': '(61) 99999-7777',
                    'assentamento': 'Assentamento Primavera',
                    'prioridade': 2
                },
                {
                    'nome': 'Fernanda Almeida Lima',
                    'cpf': '12345678908',
                    'telefone': '(61) 99999-8888',
                    'assentamento': 'Assentamento Sol Nascente',
                    'prioridade': 0
                }
            ]
            
            # Criar cadastros de teste
            for i, pessoa in enumerate(pessoas_teste):
                cadastro = Cadastro(
                    nome=pessoa['nome'],
                    cpf=pessoa['cpf'],
                    telefone=pessoa['telefone'],
                    assentamento=pessoa['assentamento'],
                    municipio_id=municipio.id,
                    estado_id=estado.id,
                    descricao_id=descricao.id,
                    instituicao_id=instituicao.id,
                    prioridade=pessoa['prioridade'],
                    status_chamada='aguardando'
                )
                
                # Gerar senha de chamada
                cadastro.gerar_senha_chamada()
                
                # Entrar na fila
                cadastro.entrar_fila()
                
                db.session.add(cadastro)
                print(f"✅ Cadastro criado: {pessoa['nome']} - Senha: {cadastro.senha_chamada}")
            
            db.session.commit()
            print(f"\n🎉 {len(pessoas_teste)} cadastros de teste criados com sucesso!")
            
            # Mostrar estatísticas
            total = Cadastro.query.count()
            aguardando = Cadastro.query.filter_by(status_chamada='aguardando').count()
            normal = Cadastro.query.filter_by(prioridade=0).count()
            alta = Cadastro.query.filter_by(prioridade=1).count()
            urgente = Cadastro.query.filter_by(prioridade=2).count()
            
            print(f"\n📊 Estatísticas:")
            print(f"   Total de cadastros: {total}")
            print(f"   Aguardando: {aguardando}")
            print(f"   Prioridade Normal: {normal}")
            print(f"   Prioridade Alta: {alta}")
            print(f"   Prioridade Urgente: {urgente}")
            
            print(f"\n🔗 URLs para teste:")
            print(f"   Painel TV: http://127.0.0.1:5000/senhas_tv")
            print(f"   Painel Atendente: http://127.0.0.1:5000/painel_atendente")
            
            print(f"\n💡 Instruções:")
            print(f"1. Inicie o servidor: python app/app.py")
            print(f"2. Abra o painel TV em uma aba")
            print(f"3. Faça login como atendente e abra o painel do atendente")
            print(f"4. Teste as ações de chamar, atender e finalizar senhas")
            print(f"5. Observe as atualizações em tempo real no painel TV")
            
        except Exception as e:
            logger.error(f"Erro ao criar dados de teste: {str(e)}")
            print(f"❌ Erro ao criar dados de teste: {e}")
            db.session.rollback()

def limpar_dados_teste():
    """Remove os dados de teste"""
    
    with app.app_context():
        try:
            print("🧹 Removendo dados de teste...")
            
            # Remover cadastros de teste
            cadastros_teste = Cadastro.query.filter(
                Cadastro.cpf.in_(['12345678901', '12345678902', '12345678903', '12345678904', 
                                '12345678905', '12345678906', '12345678907', '12345678908'])
            ).all()
            
            for cadastro in cadastros_teste:
                db.session.delete(cadastro)
                print(f"🗑️ Removido: {cadastro.nome}")
            
            db.session.commit()
            print(f"✅ {len(cadastros_teste)} cadastros de teste removidos")
            
        except Exception as e:
            logger.error(f"Erro ao remover dados de teste: {str(e)}")
            print(f"❌ Erro ao remover dados de teste: {e}")
            db.session.rollback()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Script para gerenciar dados de teste do WebSocket')
    parser.add_argument('--limpar', action='store_true', help='Remove os dados de teste')
    
    args = parser.parse_args()
    
    if args.limpar:
        limpar_dados_teste()
    else:
        criar_dados_teste() 