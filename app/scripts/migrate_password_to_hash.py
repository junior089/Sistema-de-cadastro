import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'app/cadastro.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("SELECT id, password FROM user WHERE password IS NOT NULL;")
    users = c.fetchall()
    for user_id, plain_password in users:
        if plain_password:
            hash_ = generate_password_hash(plain_password)
            c.execute("UPDATE user SET password_hash = ? WHERE id = ?", (hash_, user_id))
    print("Senhas convertidas para hash em password_hash.")
except Exception as e:
    print(f"Erro ao migrar senhas: {e}")

conn.commit()
conn.close()
print("Migração de senhas concluída.")
