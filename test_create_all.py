import os
import sys
sys.path.insert(0, os.path.abspath('.'))

from app import db
from app.app import app
# Importar todos os modelos explicitamente
from app.models.system_status import SystemStatus
from app.models.user import User
from app.models.cadastro import Cadastro
from app.models.municipio import Municipio
from app.models.estado import Estado
from app.models.descricao import Descricao
from app.models.instituicao import Instituicao
from app.models.atendente import Atendente
from app.models.log import Log

# Remover banco se existir
db_path = os.path.join('instance', 'cadastro.db')
if os.path.exists(db_path):
    os.remove(db_path)
    print("Banco removido")

# Garantir que o diretório existe
os.makedirs('instance', exist_ok=True)

print("Testando db.create_all()...")

with app.app_context():
    # Verificar os modelos antes de criar
    print("Modelos:")
    for model in [SystemStatus, User, Cadastro, Municipio, Estado, Descricao, Instituicao, Atendente, Log]:
        print(f"- {model.__tablename__}")
        for column in model.__table__.columns:
            print(f"  - {column.name}: {column.type}")
    
    # Criar todas as tabelas
    db.create_all()
    
    # Verificar se as tabelas foram criadas corretamente
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    print("\nTabelas criadas:")
    for table_name in inspector.get_table_names():
        print(f"- {table_name}")
        columns = inspector.get_columns(table_name)
        print(f"  Colunas: {[col['name'] for col in columns]}")

print("Teste concluído!") 