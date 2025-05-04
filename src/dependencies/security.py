from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from core.config import settings
from core.database import get_db
from models.models import UserDB
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(plain_password: str, hashed_password: str):
    """
    Verification of password.
    :param plain_password: password in plain text.
    :param hashed_password: password that is already hashed
    :return: is the plain password correct.
    """
    print(plain_password, hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    """
    Function that gets hash from plain text password.
    :param password: password.
    :return: hashed password.
    """
    return pwd_context.hash(password)


def get_user(db: Session, username: str):
    """
    Get user by username.
    :param db: db Session
    :param username: username
    :return: UserDb object
    """
    return db.query(UserDB).filter_by(username=username).first()


def authenticate_user(db: Session, username: str, password: str):
    """
    Function that authenticates user.
    :param db: db session.
    :param username: username.
    :param password: password.
    :return: user if correct.
    """
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict):
    """
    Creating access token for data.
    :param data: data for token.
    :return: access token.
    """
    to_encode = data.copy()
    expire = (datetime.now(timezone.utc)
              + timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key,
                      algorithm=settings.algorithm)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
):
    """
    Getting current user from token.
    :param token: token.
    :param db: db session.
    :return: user if everything is correct
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user
