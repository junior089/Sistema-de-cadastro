"""
Script para adicionar o campo 'atendida' na tabela Cadastro
Execute este script após fazer backup do banco de dados
"""

import sqlite3
import os
from datetime import datetime


def add_atendida_field():
    """Adiciona o campo atendida na tabela cadastro"""

    # Caminho do banco de dados
    db_path = 'cadastro.db'

    if not os.path.exists(db_path):
        print(f"Erro: Banco de dados {db_path} não encontrado!")
        return False

    try:
        # Conectar ao banco
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(cadastro)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'atendida' in columns:
            print("Campo 'atendida' já existe na tabela!")
            return True

        # Adicionar a coluna
        cursor.execute("""
                       ALTER TABLE cadastro
                           ADD COLUMN atendida BOOLEAN DEFAULT FALSE
                       """)

        # Confirmar as mudanças
        conn.commit()

        print("✅ Campo 'atendida' adicionado com sucesso!")
        print("📊 Todos os cadastros existentes foram marcados como 'Não Atendida' por padrão")

        # Verificar quantos registros foram afetados
        cursor.execute("SELECT COUNT(*) FROM cadastro")
        total_registros = cursor.fetchone()[0]
        print(f"📈 Total de registros na tabela: {total_registros}")

        return True

    except sqlite3.Error as e:
        print(f"❌ Erro ao modificar banco de dados: {e}")
        return False

    finally:
        if conn:
            conn.close()


def create_backup():
    """Cria backup do banco antes da modificação"""
    db_path = 'cadastro.db'
    backup_path = f'cadastro_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'

    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False


if __name__ == "__main__":
    print("🔄 Iniciando modificação do banco de dados...")
    print("📋 Adicionando campo 'atendida' na tabela cadastro")

    # Criar backup primeiro
    if create_backup():
        # Adicionar o campo
        if add_atendida_field():
            print("\n✅ Modificação concluída com sucesso!")
            print("🔄 Reinicie a aplicação Flask para aplicar as mudanças")
        else:
            print("\n❌ Falha na modificação do banco de dados")
    else:
        print("\n❌ Falha ao criar backup. Operação cancelada por segurança.")
