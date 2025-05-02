from core.database import SessionLocal
from models.models import UserDB
from dependencies.security import get_password_hash
from core.config import settings


def init_admin_user():
    db = SessionLocal()
    try:
        admin = (db.query(UserDB)
                 .filter(UserDB.email == settings.admin_email).first())
        if not admin:
            admin_user = UserDB(
                username=settings.admin_username,
                email=settings.admin_email,
                hashed_password=get_password_hash(settings.admin_password),
                full_name="Administrator",
                disabled=False
            )
            db.add(admin_user)
            db.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()
