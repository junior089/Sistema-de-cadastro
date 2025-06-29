import sqlite3
from datetime import datetime
import os

DB_PATH = 'instance/cadastro.db'  # Caminho padrão do banco para Flask

def force_recreate_system_status_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Remove a tabela se existir
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_status'")
    if cursor.fetchone():
        print('Removendo tabela antiga system_status...')
        cursor.execute("DROP TABLE system_status")
    # Cria a tabela do zero
    cursor.execute('''
        CREATE TABLE system_status (
            id INTEGER PRIMARY KEY,
            status VARCHAR(64) NOT NULL DEFAULT 'OK',
            last_update DATETIME,
            maintenance_mode BOOLEAN DEFAULT 0,
            maintenance_message VARCHAR(500) DEFAULT 'Sistema em manutenção. Por favor, tente novamente mais tarde.'
        )
    ''')
    # Insere registro padrão
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO system_status (status, last_update, maintenance_mode, maintenance_message) VALUES (?, ?, ?, ?)", 
                   ('OK', now, 0, 'Sistema em manutenção. Por favor, tente novamente mais tarde.'))
    conn.commit()
    conn.close()
    print('Tabela system_status recriada com sucesso!')

if __name__ == '__main__':
    force_recreate_system_status_table()
