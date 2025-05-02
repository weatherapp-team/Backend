from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from schemas.schemas import Token, UserLogin, UserCreate, User
from models.models import UserDB
from dependencies.security import (
    authenticate_user,
    create_access_token,
    get_current_user
)
from services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(UserDB).filter(
        UserDB.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    UserService.create_user(db, user_data)
    return {"message": "User created successfully"}


@router.get("/me", response_model=User)
async def read_current_user(
    current_user: UserDB = Depends(get_current_user)
):
    return current_user
