from datetime import datetime, timedelta
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import WeatherCacheDB
from core.config import settings


class WeatherService:
    def __init__(self):
        self.api_key = settings.openweather_api_key

    def get_weather_data(self, db: Session, location: str):
        cached = db.query(WeatherCacheDB).filter(
            WeatherCacheDB.location == location.lower()
        ).first()

        if cached and (datetime.now() - cached.timestamp) < timedelta(minutes=30):
            return cached.data

        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.api_key}&units=metric"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            weather_data = {
                "location": location,
                "temperature": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'],
                "timestamp": datetime.now()
            }

            if cached:
                cached.data = weather_data
                cached.timestamp = datetime.now()
            else:
                new_cache = WeatherCacheDB(
                    location=location.lower(),
                    data=weather_data,
                    timestamp=datetime.now()
                )
                db.add(new_cache)
            db.commit()
            return weather_data

        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Weather API error: {str(e)}")