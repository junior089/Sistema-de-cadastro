from app import db
from app.models.system_status import SystemStatus
from app.app import app

with app.app_context():
    db.drop_all()
    db.create_all()
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    print('Colunas da tabela system_status:')
    for col in inspector.get_columns('system_status'):
        print(f"- {col['name']} ({col['type']})") 