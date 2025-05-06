from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401
from tests.routers.alerts.main import mocked_weather_request
import time

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def register_and_login_user(client):
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
    return user.json()["access_token"]


def test_get_notifications(monkeypatch, _):  # noqa: F811
    """Test getting list of notifications."""
    token = register_and_login_user(client)
    monkeypatch.setattr("requests.get", mocked_weather_request)

    empty_notifications = client.get(
        "/alerts/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert empty_notifications.json() == []

    client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "Moscow",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 75,
        },
    )

    client.get(
        "/weather/Moscow",
        headers={"Authorization": f"Bearer {token}"}
    )
    time.sleep(1)

    notifications = client.get(
        "/alerts/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(notifications.json()) == 1
    assert notifications.json()[0]["location"] == "Moscow"
    assert notifications.json()[0]["column_name"] == "humidity"
    assert notifications.json()[0]["comparator"] == ">="
    assert notifications.json()[0]["number"] == 75
    assert notifications.json()[0]["actual_number"] == 78
    assert notifications.json()[0]["id"] == 1


def test_get_notifications_not_authenticated(monkeypatch, _):  # noqa: F811
    """Test getting notifications when not authenticated."""
    monkeypatch.setattr("requests.get", mocked_weather_request)
    response = client.get("/alerts/notifications")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_get_empty_notifications(monkeypatch, _):  # noqa: F811
    """Test getting empty list of notifications."""
    token = register_and_login_user(client)
    monkeypatch.setattr("requests.get", mocked_weather_request)

    client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "Moscow",
            "column_name": "temperature",
            "comparator": ">=",
            "number": 20,
        },
    )

    client.get(
        "/weather/Moscow",
        headers={"Authorization": f"Bearer {token}"}
    )
    time.sleep(1)

    notifications = client.get(
        "/alerts/notifications",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert len(notifications.json()) == 0
