import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import db
from app.models.system_status import SystemStatus
from sqlalchemy import inspect

# Configurar o app
from app.app import app

with app.app_context():
    # Verificar se a tabela existe
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tabelas no banco: {tables}")
    
    if 'system_status' in tables:
        columns = inspector.get_columns('system_status')
        print(f"\nColunas da tabela system_status:")
        for col in columns:
            print(f"- {col['name']} ({col['type']})")
    
    # Verificar o modelo SQLAlchemy
    print(f"\nModelo SystemStatus:")
    print(f"- __tablename__: {SystemStatus.__tablename__}")
    print(f"- Colunas do modelo:")
    for column in SystemStatus.__table__.columns:
        print(f"  - {column.name}: {column.type}")
    
    # Tentar fazer uma consulta simples
    try:
        result = db.session.execute(db.select(SystemStatus)).first()
        print(f"\nConsulta bem-sucedida: {result}")
    except Exception as e:
        print(f"\nErro na consulta: {e}")
        print(f"Tipo do erro: {type(e)}") 