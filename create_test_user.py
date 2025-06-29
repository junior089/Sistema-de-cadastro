#!/usr/bin/env python3
"""
Script para criar um usuário de teste para cadastro
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.app import app, db
from app.models.user import User
from app.models.estado import Estado
from app.models.municipio import Municipio
from app.models.descricao import Descricao
from app.models.instituicao import Instituicao
from app.models.atendente import Atendente

def create_test_data():
    """Cria dados de teste para o sistema"""
    
    with app.app_context():
        print("🔧 CRIANDO DADOS DE TESTE")
        print("=" * 50)
        
        # 1. Criar usuário de teste
        print("1. Criando usuário de teste...")
        
        # Verificar se o usuário já existe
        existing_user = User.query.filter_by(username='CADASTRADOR').first()
        if existing_user:
            print("   ✅ Usuário CADASTRADOR já existe")
        else:
            user = User(username='CADASTRADOR', role='cadastrador')
            user.password = '123456'
            db.session.add(user)
            db.session.commit()
            print("   ✅ Usuário CADASTRADOR criado com sucesso")
            print("   📝 Login: CADASTRADOR")
            print("   📝 Senha: 123456")
        
        # 2. Criar estados de teste
        print("\n2. Criando estados de teste...")
        
        estados_data = [
            {'nome': 'DISTRITO FEDERAL'},
            {'nome': 'GOIÁS'},
            {'nome': 'MINAS GERAIS'},
            {'nome': 'SÃO PAULO'},
            {'nome': 'RIO DE JANEIRO'}
        ]
        
        for estado_data in estados_data:
            existing_estado = Estado.query.filter_by(nome=estado_data['nome']).first()
            if not existing_estado:
                estado = Estado(nome=estado_data['nome'])
                db.session.add(estado)
                print(f"   ✅ Estado {estado_data['nome']} criado")
            else:
                print(f"   ✅ Estado {estado_data['nome']} já existe")
        
        db.session.commit()
        
        # 3. Criar municípios de teste
        print("\n3. Criando municípios de teste...")
        
        df_estado = Estado.query.filter_by(nome='DISTRITO FEDERAL').first()
        if df_estado:
            municipios_df = [
                'BRASÍLIA',
                'CEILÂNDIA',
                'TAGUATINGA',
                'SAMAMBAIA',
                'PLANALTINA'
            ]
            
            for municipio_nome in municipios_df:
                existing_municipio = Municipio.query.filter_by(
                    nome=municipio_nome, 
                    estado_id=df_estado.id
                ).first()
                
                if not existing_municipio:
                    municipio = Municipio(nome=municipio_nome, estado_id=df_estado.id)
                    db.session.add(municipio)
                    print(f"   ✅ Município {municipio_nome} criado")
                else:
                    print(f"   ✅ Município {municipio_nome} já existe")
        
        db.session.commit()
        
        # 4. Criar descrições de teste
        print("\n4. Criando descrições de teste...")
        
        descricoes_data = [
            'ASSISTÊNCIA TÉCNICA',
            'CRÉDITO RURAL',
            'REGULARIZAÇÃO FUNDIÁRIA',
            'INFRAESTRUTURA',
            'CAPACITAÇÃO'
        ]
        
        for descricao_nome in descricoes_data:
            existing_descricao = Descricao.query.filter_by(nome=descricao_nome).first()
            if not existing_descricao:
                descricao = Descricao(nome=descricao_nome)
                db.session.add(descricao)
                print(f"   ✅ Descrição {descricao_nome} criada")
            else:
                print(f"   ✅ Descrição {descricao_nome} já existe")
        
        db.session.commit()
        
        # 5. Criar instituições de teste
        print("\n5. Criando instituições de teste...")
        
        instituicoes_data = [
            'INCRA',
            'EMATER',
            'SEBRAE',
            'SENAR',
            'PREFEITURA'
        ]
        
        for instituicao_nome in instituicoes_data:
            existing_instituicao = Instituicao.query.filter_by(nome=instituicao_nome).first()
            if not existing_instituicao:
                instituicao = Instituicao(nome=instituicao_nome)
                db.session.add(instituicao)
                print(f"   ✅ Instituição {instituicao_nome} criada")
            else:
                print(f"   ✅ Instituição {instituicao_nome} já existe")
        
        db.session.commit()
        
        # 6. Criar atendentes de teste
        print("\n6. Criando atendentes de teste...")
        
        atendentes_data = [
            'MARIA SILVA',
            'JOÃO SANTOS',
            'ANA COSTA',
            'PEDRO OLIVEIRA',
            'LUCIA FERREIRA'
        ]
        
        for atendente_nome in atendentes_data:
            existing_atendente = Atendente.query.filter_by(nome=atendente_nome).first()
            if not existing_atendente:
                atendente = Atendente(nome=atendente_nome)
                db.session.add(atendente)
                print(f"   ✅ Atendente {atendente_nome} criado")
            else:
                print(f"   ✅ Atendente {atendente_nome} já existe")
        
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("✅ DADOS DE TESTE CRIADOS COM SUCESSO!")
        print("\n📋 RESUMO:")
        print("   👤 Usuário: CADASTRADOR")
        print("   🔑 Senha: 123456")
        print("   🎯 Role: cadastrador")
        print("\n🌐 Para testar:")
        print("   1. Acesse: http://127.0.0.1:5000")
        print("   2. Faça login com: CADASTRADOR / 123456")
        print("   3. Clique em 'Cadastrar' no menu")
        print("   4. Preencha o formulário e clique em 'Cadastrar'")
        print("\n" + "=" * 50)

if __name__ == "__main__":
    create_test_data() 