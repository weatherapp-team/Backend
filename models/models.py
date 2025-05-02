from datetime import datetime

from sqlalchemy import (Column, Integer, String,
                        Boolean, DateTime, ForeignKey, JSON)
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
    column_name = Column(String)
    comparator = Column(String)
    number = Column(Integer)


class WeatherCacheDB(Base):
    __tablename__ = "weather_cache"
    location = Column(String, primary_key=True)
    data = Column(JSON)
    timestamp = Column(DateTime)

    def __init__(self, location: str, data: dict, timestamp: datetime):
        self.location = location.lower()
        self.data = self.serialize_data(data)
        self.timestamp = timestamp

    @staticmethod
    def serialize_data(data: dict) -> dict:
        """Convert datetime objects to ISO format
         strings for JSON serialization"""
        serialized = data.copy()
        if ('timestamp' in serialized
                and isinstance(serialized['timestamp'], datetime)):
            serialized['timestamp'] = serialized['timestamp'].isoformat()
        return serialized

    def deserialize_data(self) -> dict:
        """Convert ISO format strings back to
         datetime objects when retrieving"""
        deserialized = self.data.copy()
        if 'timestamp' in deserialized:
            deserialized['timestamp'] = (
                datetime.fromisoformat(deserialized['timestamp']))
        return deserialized
