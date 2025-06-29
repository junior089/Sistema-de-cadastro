from app import db
from app.app import app
from app.models.user import User

with app.app_context():
    username = "admin"
    password = "admin123"  # Troque para uma senha forte depois!
    if not User.query.filter_by(username=username).first():
        user = User(username=username, role="admin")
        user.password = password
        db.session.add(user)
        db.session.commit()
        print(f"Usuário admin '{username}' criado com sucesso!")
    else:
        print("Usuário admin já existe.") 