import sqlite3

DB_PATH = 'app/cadastro.db'

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("ALTER TABLE cadastro ADD COLUMN atendida BOOLEAN NOT NULL DEFAULT 0;")
    print("Coluna 'atendida' adicionada com sucesso.")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print("Coluna 'atendida' já existe.")
    else:
        print(f"Erro: {e}")

conn.commit()
conn.close()
