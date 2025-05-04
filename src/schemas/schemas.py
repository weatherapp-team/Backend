from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class Token(BaseModel):
    """
    Schema for token.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for token data.
    """
    username: Optional[str] = None


class WeatherData(BaseModel):
    """
    Schema for weather data.
    """
    location: str
    main_weather: str
    icon: str
    description: str
    temperature: float
    temperature_feels_like: float
    temperature_min: float
    temperature_max: float
    pressure: float
    humidity: float
    visibility: float
    wind_speed: float
    wind_deg: float
    timestamp: datetime
    lat: float
    lon: float
    sunrise: datetime
    sunset: datetime


class AlertBase(BaseModel):
    """
    Base schema for alerts.
    """
    location: str
    column_name: str
    comparator: str
    number: int


class NotificationGet(AlertBase):
    """
    Schema for getting notifications.
    """
    id: int
    actual_number: float
    timestamp: datetime


class AlertCreate(AlertBase):
    """
    Schema for creating alerts.
    """
    pass


class AlertUpdate(AlertBase):
    """
    Schema for updating alerts.
    """
    id: int


class AlertGet(AlertBase):
    """
    Schema for getting alert by id.
    """
    id: int


class AlertDelete(BaseModel):
    """
    Schema for deleting alert.
    """
    id: int


class UserBase(BaseModel):
    """
    Base schema for user.
    """
    username: str = Field(..., min_length=5)
    email: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """
    Schema for creating user.
    """
    password: str = Field(..., min_length=5)


class UserLogin(BaseModel):
    """
    User login schema
    """
    username: str = Field(..., min_length=5)
    password: str = Field(..., min_length=5)


class User(UserBase):
    """
    User schema
    """
    disabled: Optional[bool] = None


class UserInDB(User):
    """
    User in db schema
    """
    hashed_password: str
