"""
Script para adicionar coluna 'atendida' na tabela Cadastro
Execute este script após fazer backup do banco de dados
"""

import os
import sqlite3
from datetime import datetime

def get_db_path():
    # Tenta localizar o banco em locais comuns
    paths = [
        os.path.join('app', 'cadastro.db'),
        os.path.join('instance', 'cadastro.db'),
        'cadastro.db'
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

def add_atendida_field(db_path):
    """Adiciona o campo atendida na tabela cadastro"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(cadastro)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'atendida' in columns:
            print("Coluna 'atendida' já existe na tabela!")
            return True
        cursor.execute("""
            ALTER TABLE cadastro
                ADD COLUMN atendida BOOLEAN NOT NULL DEFAULT 0
        """)
        conn.commit()
        print("✅ Coluna 'atendida' adicionada com sucesso!")
        # Atualiza todos os registros antigos explicitamente
        cursor.execute("UPDATE cadastro SET atendida = 0 WHERE atendida IS NULL")
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM cadastro")
        total_registros = cursor.fetchone()[0]
        print(f"📈 Total de registros na tabela: {total_registros}")
        return True
    except sqlite3.Error as e:
        print(f"❌ Erro ao modificar banco de dados: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def create_backup(db_path):
    """Cria backup do banco antes da modificação"""
    backup_dir = os.path.dirname(db_path) or '.'
    backup_name = f"cadastro_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    backup_path = os.path.join(backup_dir, backup_name)
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup criado: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {e}")
        return False

def add_chamada_fields(db_path):
    if not os.path.exists(db_path):
        print(f"Arquivo de banco não encontrado: {db_path}")
        return
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Adiciona coluna senha_chamada
        cursor.execute("ALTER TABLE cadastro ADD COLUMN senha_chamada VARCHAR(8);")
    except Exception as e:
        print(f"Coluna senha_chamada: {e}")
    try:
        # Adiciona coluna status_chamada
        cursor.execute("ALTER TABLE cadastro ADD COLUMN status_chamada VARCHAR(20) DEFAULT 'aguardando';")
    except Exception as e:
        print(f"Coluna status_chamada: {e}")
    try:
        # Adiciona coluna horario_chamada
        cursor.execute("ALTER TABLE cadastro ADD COLUMN horario_chamada DATETIME;")
    except Exception as e:
        print(f"Coluna horario_chamada: {e}")
    try:
        # Adiciona coluna historico_chamadas
        cursor.execute("ALTER TABLE cadastro ADD COLUMN historico_chamadas TEXT;")
    except Exception as e:
        print(f"Coluna historico_chamadas: {e}")
    try:
        # Adiciona coluna prioridade
        cursor.execute("ALTER TABLE cadastro ADD COLUMN prioridade INTEGER DEFAULT 0;")
    except Exception as e:
        print(f"Coluna prioridade: {e}")
    try:
        # Adiciona coluna posicao_fila
        cursor.execute("ALTER TABLE cadastro ADD COLUMN posicao_fila INTEGER;")
    except Exception as e:
        print(f"Coluna posicao_fila: {e}")
    try:
        # Adiciona coluna observacoes
        cursor.execute("ALTER TABLE cadastro ADD COLUMN observacoes TEXT;")
    except Exception as e:
        print(f"Coluna observacoes: {e}")
    
    conn.commit()
    conn.close()
    print("✅ Campos de chamada adicionados com sucesso!")

if __name__ == "__main__":
    print("🔄 Iniciando modificação do banco de dados...")
    db_path = get_db_path()
    if not db_path:
        print("❌ Banco de dados não encontrado em app/cadastro.db, instance/cadastro.db ou ./cadastro.db")
        exit(1)
    print(f"📋 Usando banco de dados: {db_path}")
    if create_backup(db_path):
        if add_atendida_field(db_path):
            print("\n✅ Modificação concluída com sucesso!")
            print("🔄 Reinicie a aplicação Flask para aplicar as mudanças")
            add_chamada_fields(db_path)
        else:
            print("\n❌ Falha na modificação do banco de dados")
    else:
        print("\n❌ Falha ao criar backup. Operação cancelada por segurança.")
