from sqlalchemy.orm import Session
from models.models import UserDB
from dependencies.security import get_password_hash


class UserService:
    """
    Service for handling users.
    """
    @staticmethod
    def create_user(db: Session, user_data):
        """
        Creating user.
        :param db: db session
        :param user_data: user data
        :return: user in db
        """
        hashed_password = get_password_hash(user_data.password)
        db_user = UserDB(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
