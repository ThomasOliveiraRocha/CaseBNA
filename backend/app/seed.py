from database import SessionLocal, init_db
from app.models import User
from crud import get_user_by_username
from sqlalchemy.orm import Session
from passlib.context import CryptContext

def seed_admin():
    init_db()
    db: Session = SessionLocal()

    admin_username = "admin"
    admin_password = "admin123"

    existing_user = get_user_by_username(db, admin_username)
    if existing_user:
        print(f"Usuário '{admin_username}' já existe.")
    else:
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(admin_password)

        user = User(username=admin_username, hashed_password=hashed_password, is_admin=1)
        db.add(user)
        db.commit()
        print(f"Usuário administrador '{admin_username}' criado com sucesso.")

    db.close()

if __name__ == "__main__":
    seed_admin()
