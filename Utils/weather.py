from datetime import datetime, timedelta
from fastapi import HTTPException
import requests

weather_cache = {}

class WeatherMonitor:
    def __init__(self, api_key):
        self.api_key = api_key

    def fetch_weather_data(self, location: str):
        cache_key = f"{location.lower()}_current"
        if cache_key in weather_cache:
            cached_data = weather_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(minutes=30):
                return cached_data['data']

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

            weather_cache[cache_key] = {
                "data": weather_data,
                "timestamp": datetime.now()
            }
            return weather_data
        except requests.RequestException as e:
            raise HTTPException(status_code=502, detail=f"Weather API error: {str(e)}")