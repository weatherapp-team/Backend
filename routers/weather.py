from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from models.models import UserDB, WeatherCacheDB
from schemas.schemas import WeatherData
from dependencies.security import get_current_user
from services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])
weather_service = WeatherService()


@router.get("/{location}", response_model=WeatherData)
async def get_weather(
    location: str,
    db: Session = Depends(get_db),
    _current_user: UserDB = Depends(get_current_user)
):
    try:
        return weather_service.get_weather_data(db, location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{location}/history", response_model=List[WeatherData])
async def get_weather_history(
    location: str,
    db: Session = Depends(get_db),
    _current_user: UserDB = Depends(get_current_user)
):
    try:
        weather_service.get_weather_data(db, location)

        weather_history = db.query(WeatherCacheDB).filter_by(
            location=location.lower()
        ).all()

        return [i.data for i in weather_history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

