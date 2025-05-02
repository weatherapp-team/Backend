from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from core.database import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean, default=False)

class SavedLocationDB(Base):
    __tablename__ = "saved_locations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location = Column(String)

class WeatherAlertDB(Base):
    __tablename__ = "weather_alerts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location = Column(String)
    condition = Column(String)
    active = Column(Boolean, default=True)

class WeatherCacheDB(Base):
    __tablename__ = "weather_cache"
    location = Column(String, primary_key=True)
    data = Column(JSON)
    timestamp = Column(DateTime)