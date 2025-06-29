import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'instance', 'cadastro.db'))

def force_create_system_status_table():
    if not os.path.exists(DB_PATH):
        print(f"Arquivo de banco não encontrado: {DB_PATH}. Criando...")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        open(DB_PATH, 'a').close()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS system_status;")
        cursor.execute('''
            CREATE TABLE system_status (
                id INTEGER PRIMARY KEY,
                status VARCHAR(64) NOT NULL DEFAULT 'OK',
                last_update DATETIME,
                maintenance_mode BOOLEAN DEFAULT 0,
                maintenance_message VARCHAR(500) DEFAULT 'Sistema em manutenção. Por favor, tente novamente mais tarde.'
            );
        ''')
        conn.commit()
        print("Tabela 'system_status' criada com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    force_create_system_status_table()
