import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'app/cadastro.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("ALTER TABLE user ADD COLUMN password_hash VARCHAR(128);")
    print("Coluna 'password_hash' adicionada com sucesso.")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print("Coluna 'password_hash' já existe.")
    else:
        print(f"Erro: {e}")

# Opcional: migrar senhas existentes para hash padrão (inseguro, apenas para não quebrar o login)
try:
    c.execute("SELECT id, password FROM user;")
    users = c.fetchall()
    for user_id, plain_password in users:
        if plain_password:
            hash_ = generate_password_hash(plain_password)
            c.execute("UPDATE user SET password_hash = ? WHERE id = ?", (hash_, user_id))
    print("Senhas migradas para password_hash.")
except Exception as e:
    print(f"Erro ao migrar senhas: {e}")

conn.commit()
conn.close()
print("Migração concluída.")
