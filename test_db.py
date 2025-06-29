import sqlite3
import os

# Caminho do banco
db_path = os.path.join('instance', 'cadastro.db')

# Garantir que o diretório existe
os.makedirs('instance', exist_ok=True)

# Remover banco se existir
if os.path.exists(db_path):
    os.remove(db_path)
    print("Banco antigo removido")

# Criar novo banco
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Criar tabela system_status
cursor.execute('''
    CREATE TABLE system_status (
        id INTEGER PRIMARY KEY,
        status VARCHAR(64) NOT NULL DEFAULT 'OK',
        last_update DATETIME,
        maintenance_mode BOOLEAN DEFAULT 0,
        maintenance_message VARCHAR(500) DEFAULT 'Sistema em manutenção. Por favor, tente novamente mais tarde.'
    );
''')

# Inserir registro inicial
cursor.execute('''
    INSERT INTO system_status (status, last_update, maintenance_mode, maintenance_message)
    VALUES ('OK', datetime('now'), 0, 'Sistema em manutenção. Por favor, tente novamente mais tarde.')
''')

conn.commit()

# Verificar se foi criado corretamente
cursor.execute("PRAGMA table_info(system_status);")
columns = cursor.fetchall()
print("Colunas da tabela system_status:")
for col in columns:
    print(f"- {col[1]} ({col[2]})")

# Testar consulta
cursor.execute("SELECT * FROM system_status;")
result = cursor.fetchone()
print(f"\nRegistro encontrado: {result}")

conn.close()
print("\nBanco criado com sucesso!") 