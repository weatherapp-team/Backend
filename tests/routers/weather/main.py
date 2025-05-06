def mocked_weather_request(*args):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def raise_for_status(self):
            pass

        def json(self):
            return self.json_data

    if args[0].startswith(
        "http://api.openweathermap.org/data/2.5/weather?q=Moscow"
    ) or args[0].startswith(
        "http://api.openweathermap.org/data/2.5/weather?q=Innopolis"
    ):
        weather_data = {
            "coord": {
                "lat": 55.7522,
                "lon": 37.6156,
            },
            "weather": [
                {
                    "main": "Clouds",
                    "icon": "04d",
                    "description": "overcast clouds",
                }
            ],
            "main": {
                "temp": 12.79,
                "feels_like": 11.61,
                "temp_min": 11.24,
                "temp_max": 12.97,
                "pressure": 999.0,
                "humidity": 57.0,
            },
            "visibility": 10000.0,
            "wind": {
                "speed": 3.45,
                "deg": 154.0,
            },
            "sys": {
                "sunrise": "2025-05-06T04:35:54Z",
                "sunset": "2025-05-06T20:17:12Z",
            },
        }
        return MockResponse(weather_data, 200)
    else:
        return MockResponse(None, 404)
