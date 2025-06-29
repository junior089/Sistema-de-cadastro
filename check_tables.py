import sqlite3

try:
    conn = sqlite3.connect('instance/cadastro.db')
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("📋 Tabelas no banco de dados:")
    print("-" * 30)
    
    for table in tables:
        print(f"✅ {table[0]}")
        
        # Mostrar estrutura da tabela
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"   Colunas: {[col[1] for col in columns]}")
        print()
        
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}") 