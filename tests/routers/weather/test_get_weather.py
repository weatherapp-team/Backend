from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401
from tests.routers.weather.main import mocked_weather_request
import time

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_weather(monkeypatch, _):  # noqa: F811:
    """
    Test getting weather
    This test tries to get weather.
    """
    user_data = {
        "username": "test_user",
        "email": "test_user@test.example",
        "password": "testpassword",
    }
    client.post("/auth/register", json=user_data)

    user = client.post(
        "/auth/login",
        json={"username": "test_user", "password": "testpassword"},
    )
    token = user.json()["access_token"]

    monkeypatch.setattr("requests.get", mocked_weather_request)

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
        "timestamp",
    ]

    response = client.get(
        "/weather/Moscow", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    for field in weather_fields:
        assert field in response.json()


def test_get_weather_not_authenticated(monkeypatch, _):  # noqa: F811:
    """
    Test getting weather when not authenticated

    This test tries to get weather when user is not authenticated,
    so API should return error.
    """
    monkeypatch.setattr("requests.get", mocked_weather_request)

    response = client.get("/weather/Moscow")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_get_weather_cache(monkeypatch, _):  # noqa: F811:
    """
    Test getting weather from cache

    This test tries to get weather two times.
    Second time timestamp should be the same as first
    """
    user_data = {
        "username": "test_user",
        "email": "test_user@test.example",
        "password": "testpassword",
    }
    client.post("/auth/register", json=user_data)

    user = client.post(
        "/auth/login",
        json={"username": "test_user", "password": "testpassword"},
    )
    token = user.json()["access_token"]

    monkeypatch.setattr("requests.get", mocked_weather_request)

    response1 = client.get(
        "/weather/Moscow", headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 200

    time.sleep(1)

    response2 = client.get(
        "/weather/Moscow", headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200

    history = client.get(
        "/weather/Moscow/history", headers={"Authorization": f"Bearer {token}"}
    )

    assert response1.json()["timestamp"] == response2.json()["timestamp"]
    assert len(history.json()) == 1


def test_get_weather_from_different_locations(monkeypatch, _):  # noqa: F811:
    """
    Test getting weather from different locations

    This test tries to get weather two times.
    In both cases it should be from different locations
    """
    user_data = {
        "username": "test_user",
        "email": "test_user@test.example",
        "password": "testpassword",
    }
    client.post("/auth/register", json=user_data)

    user = client.post(
        "/auth/login",
        json={"username": "test_user", "password": "testpassword"},
    )
    token = user.json()["access_token"]

    monkeypatch.setattr("requests.get", mocked_weather_request)

    response1 = client.get(
        "/weather/Innopolis", headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 200
    assert response1.json()["location"] == "Innopolis"

    time.sleep(1)

    response2 = client.get(
        "/weather/Moscow", headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200
    assert response2.json()["location"] == "Moscow"


def test_get_weather_from_nonexistent_location(monkeypatch, _):  # noqa: F811:
    """
    Test getting weather from nonexistent location

    This test tries to get weather from nonexistent location,
    so API should return error message.
    """
    user_data = {
        "username": "test_user",
        "email": "test_user@test.example",
        "password": "testpassword",
    }
    client.post("/auth/register", json=user_data)

    user = client.post(
        "/auth/login",
        json={"username": "test_user", "password": "testpassword"},
    )
    token = user.json()["access_token"]

    monkeypatch.setattr("requests.get", mocked_weather_request)

    response1 = client.get(
        "/weather/Bebrapolis", headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 500

    time.sleep(1)

    response2 = client.get(
        "/weather/Moscow", headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200
    assert response2.json()["location"] == "Moscow"
