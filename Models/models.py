from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

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

class AlertCreate(BaseModel):
    location: str
    condition: str

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str
    saved_locations: List[str] = []
    weather_alerts: List[dict] = []

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    full_name: Optional[str] = None