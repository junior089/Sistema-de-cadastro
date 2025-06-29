import sqlite3
import os
import traceback

# Caminho do banco
db_path = os.path.join('instance', 'cadastro.db')

print(f"Verificando banco: {db_path}")
print(f"Banco existe: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Verificar se a tabela existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='system_status';")
    table_exists = cursor.fetchone()
    print(f"Tabela system_status existe: {table_exists is not None}")
    
    if table_exists:
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(system_status);")
        columns = cursor.fetchall()
        print("Estrutura atual da tabela system_status:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
else:
    print("Banco não existe ainda")

print("\nAgora vou executar o app.py para ver quando a tabela é criada...")
print("=" * 50)

# Importar e executar o app
try:
    from app.app import app
    print("App importado com sucesso")
    
    # Verificar se há algum código que cria a tabela
    with open('app/app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if 'CREATE TABLE system_status' in content:
            print("Encontrei CREATE TABLE system_status no app.py")
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'CREATE TABLE system_status' in line:
                    print(f"Linha {i+1}: {line.strip()}")
                    # Mostrar algumas linhas ao redor
                    for j in range(max(0, i-5), min(len(lines), i+10)):
                        print(f"  {j+1}: {lines[j].strip()}")
    
except Exception as e:
    print(f"Erro ao importar app: {e}")
    traceback.print_exc() 