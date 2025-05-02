from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class WeatherData(BaseModel):
    location: str
    temperature: float
    humidity: float
    description: str
    timestamp: datetime

class AlertBase(BaseModel):
    location: str
    condition: str

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    active: bool

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str