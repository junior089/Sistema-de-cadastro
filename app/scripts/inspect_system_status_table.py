import sqlite3
import os

# Caminho correto para o banco na raiz do projeto
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'cadastro.db'))

def inspect_system_status_table():
    if not os.path.exists(DB_PATH):
        print(f"Arquivo de banco não encontrado: {DB_PATH}")
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(system_status);")
        columns = cursor.fetchall()
        if not columns:
            print("Tabela 'system_status' não existe.")
        else:
            print("Colunas da tabela 'system_status':")
            for col in columns:
                print(f"- {col[1]} (type: {col[2]})")
    except Exception as e:
        print(f"Erro ao inspecionar tabela: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_system_status_table()
