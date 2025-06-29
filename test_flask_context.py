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

print("Testando criação de tabelas dentro do contexto Flask...")
print(f"URI do banco: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NÃO CONFIGURADO')}")

with app.app_context():
    print("Dentro do contexto Flask")
    print(f"db.engine.url: {db.engine.url}")
    
    # Criar todas as tabelas
    db.create_all()
    print("db.create_all() executado")
    
    # Verificar se as tabelas foram criadas
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"Tabelas criadas pelo SQLAlchemy: {tables}")

print("Teste concluído!") 