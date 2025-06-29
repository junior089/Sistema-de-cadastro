import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = 'app/cadastro.db'
NEW_PASSWORD = '1234'  # Altere para a senha padrão desejada

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

hash_ = generate_password_hash(NEW_PASSWORD)
try:
    c.execute("UPDATE user SET password_hash = ?", (hash_,))
    print(f"Todas as senhas foram redefinidas para: {NEW_PASSWORD}")
except Exception as e:
    print(f"Erro ao redefinir senhas: {e}")

conn.commit()
conn.close()
print("Redefinição de senhas concluída.")
