import sqlite3

try:
    conn = sqlite3.connect('instance/cadastro.db')
    cursor = conn.cursor()
    
    # Verificar se a tabela user existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
    if cursor.fetchone():
        print("✅ Tabela 'user' existe")
        
        # Listar todos os usuários
        cursor.execute('SELECT id, username, role, password_hash FROM user')
        users = cursor.fetchall()
        
        print(f"\n📋 Usuários no banco ({len(users)} encontrados):")
        print("-" * 50)
        
        for user in users:
            print(f"ID: {user[0]}")
            print(f"Username: '{user[1]}'")
            print(f"Role: {user[2]}")
            print(f"Password Hash: {user[3][:20]}..." if user[3] else "Password Hash: None")
            print("-" * 30)
    else:
        print("❌ Tabela 'user' não existe")
        
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}") 