from datetime import datetime, timedelta
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.models import WeatherCacheDB
from core.config import settings
from services.alert_service import BackgroundService


class WeatherService:
    def __init__(self):
        self.api_key = settings.openweather_api_key
        self.service = BackgroundService()
        self.service.start()

    def get_weather_data(self, db: Session, location: str):
        cached = db.query(WeatherCacheDB).filter_by(
            location=location.lower()
        ).first()

        if cached and (datetime.now()
                       - cached.timestamp) < timedelta(minutes=30):
            return cached.data

        try:
            url = (f"http://api.openweathermap.org/data/2.5/"
                   f"weather?q={location}&appid={self.api_key}&units=metric")
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            weather_data = {
                "lat": data['coord']['lat'],
                "lon": data['coord']['lon'],
                "location": location,
                "main_weather": data['weather'][0]['main'],
                "icon": data['weather'][0]['icon'],
                "description": data['weather'][0]['description'],
                "temperature": data['main']['temp'],
                "temperature_feels_like": data['main']['feels_like'],
                "temperature_min": data['main']['temp_min'],
                "temperature_max": data['main']['temp_max'],
                "pressure": data['main']['pressure'],
                "humidity": data['main']['humidity'],
                "visibility": data['visibility'],
                "wind_speed": data['wind']['speed'],
                "wind_deg": data['wind']['deg'],
                "sunrise": data['sys']['sunrise'],
                "sunset": data['sys']['sunset'],
                "timestamp": datetime.now()
            }

            new_cache = WeatherCacheDB(
                location=location.lower(),
                data=weather_data,
                timestamp=datetime.now()
            )
            self.service.add_item(weather_data)
            db.add(new_cache)
            db.commit()
            return weather_data
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=502,
                                detail=str(e))

        except requests.RequestException as e:
            raise HTTPException(status_code=502,
                                detail=f"Weather API error: {str(e)}")
