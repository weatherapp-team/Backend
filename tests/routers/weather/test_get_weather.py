from core.database import get_db
from main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_get_weather(_):
    """
    Test getting weather
    This test tries to get weather.
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]

    weather_fields = [
        "lat",
        "lon",
        "location",
        "main_weather",
        "icon",
        "description",
        "temperature",
        "temperature_feels_like",
        "temperature_min",
        "temperature_max",
        "pressure",
        "visibility",
        "wind_speed",
        "wind_deg",
        "sunrise",
        "sunset",
        "timestamp"
    ]
    
    response = client.get("/weather/Moscow", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    for field in weather_fields:
        assert field in response.json()
