#!/usr/bin/env python3
"""
Script para adicionar cadastros de teste com senhas
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app, db
from app.models.cadastro import Cadastro
from app.models.user import User
from app.models.estado import Estado
from app.models.municipio import Municipio
from app.models.descricao import Descricao
from app.models.instituicao import Instituicao
from datetime import datetime

def adicionar_senhas_teste():
    """Adiciona cadastros de teste com senhas"""
    
    with app.app_context():
        print("🔧 ADICIONANDO SENHAS DE TESTE")
        print("=" * 50)
        
        # Verificar se já existem cadastros
        cadastros_existentes = Cadastro.query.count()
        if cadastros_existentes > 0:
            print(f"⚠️  Já existem {cadastros_existentes} cadastros no sistema")
            print("   Pulando criação de cadastros de teste...")
            return
        
        # Buscar dados necessários
        print("1. Buscando dados de referência...")
        
        # Buscar ou criar estado
        estado = Estado.query.first()
        if not estado:
            estado = Estado(nome="Distrito Federal")
            db.session.add(estado)
            db.session.commit()
            print("   ✅ Estado criado: Distrito Federal")
        
        # Buscar ou criar município
        municipio = Municipio.query.filter_by(estado_id=estado.id).first()
        if not municipio:
            municipio = Municipio(nome="Brasília", estado_id=estado.id)
            db.session.add(municipio)
            db.session.commit()
            print("   ✅ Município criado: Brasília")
        
        # Buscar ou criar descrição
        descricao = Descricao.query.first()
        if not descricao:
            descricao = Descricao(nome="Consulta Geral")
            db.session.add(descricao)
            db.session.commit()
            print("   ✅ Descrição criada: Consulta Geral")
        
        # Buscar ou criar instituição
        instituicao = Instituicao.query.first()
        if not instituicao:
            instituicao = Instituicao(nome="INCRA")
            db.session.add(instituicao)
            db.session.commit()
            print("   ✅ Instituição criada: INCRA")
        
        # Buscar usuário para ser atendente
        atendente = User.query.first()
        if not atendente:
            print("   ❌ Nenhum usuário encontrado para ser atendente")
            return
        
        print("2. Criando cadastros de teste...")
        
        # Lista de cadastros de teste
        cadastros_teste = [
            {
                'nome': 'Maria Silva Santos',
                'cpf': '12345678901',
                'telefone': '61992445034',
                'assentamento': 'Assentamento Boa Vista',
                'prioridade': 0,
                'observacoes': 'Primeira consulta'
            },
            {
                'nome': 'Ana Oliveira Costa',
                'cpf': '98765432109',
                'telefone': '61987654321',
                'assentamento': 'Assentamento Santa Maria',
                'prioridade': 1,
                'observacoes': 'Prioridade alta - Documentação urgente'
            },
            {
                'nome': 'Joana Pereira Lima',
                'cpf': '45678912345',
                'telefone': '61955556666',
                'assentamento': 'Assentamento Nova Esperança',
                'prioridade': 2,
                'observacoes': 'URGENTE - Problema com terra'
            },
            {
                'nome': 'Lucia Ferreira Rodrigues',
                'cpf': '78912345678',
                'telefone': '61977778888',
                'assentamento': 'Assentamento São João',
                'prioridade': 0,
                'observacoes': 'Consulta regular'
            },
            {
                'nome': 'Rosa Almeida Souza',
                'cpf': '32165498732',
                'telefone': '61999990000',
                'assentamento': 'Assentamento Cidade Nova',
                'prioridade': 1,
                'observacoes': 'Prioridade alta - Benefícios'
            }
        ]
        
        cadastros_criados = 0
        
        for i, dados in enumerate(cadastros_teste, 1):
            try:
                # Criar cadastro
                cadastro = Cadastro(
                    data_hora=datetime.now(),
                    nome=dados['nome'],
                    cpf=dados['cpf'],
                    telefone=dados['telefone'],
                    assentamento=dados['assentamento'],
                    municipio_id=municipio.id,
                    estado_id=estado.id,
                    descricao_id=descricao.id,
                    instituicao_id=instituicao.id,
                    atendente_id=atendente.id,
                    observacoes=dados['observacoes']
                )
                
                # Gerar senha
                cadastro.gerar_senha_chamada()
                
                # Definir prioridade
                cadastro.definir_prioridade(dados['prioridade'], dados['observacoes'])
                
                # Entrar na fila
                cadastro.entrar_fila()
                
                db.session.add(cadastro)
                db.session.commit()
                
                cadastros_criados += 1
                print(f"   ✅ Cadastro {i}: {dados['nome']} - Senha: {cadastro.senha_chamada}")
                
            except Exception as e:
                db.session.rollback()
                print(f"   ❌ Erro ao criar cadastro {i}: {str(e)}")
        
        print(f"\n🎉 {cadastros_criados} cadastros de teste criados com sucesso!")
        print("📋 Senhas geradas:")
        
        # Listar todas as senhas criadas
        senhas = Cadastro.query.filter(Cadastro.senha_chamada.isnot(None)).all()
        for senha in senhas:
            prioridade_texto = ['NORMAL', 'ALTA', 'URGENTE'][senha.prioridade]
            print(f"   🎫 {senha.senha_chamada} - {senha.nome} ({prioridade_texto})")

if __name__ == "__main__":
    try:
        adicionar_senhas_teste()
        print("\n✅ Script de senhas de teste concluído!")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        sys.exit(1) 