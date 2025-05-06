from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401
from tests.routers.alerts.main import mocked_weather_request
import time

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_notifications(monkeypatch, _):  # noqa: F811:
    """
    Test getting list of notifications

    This test tries to test thoroughly endpoint for getting notifications.
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

    empty_notifications = client.get(
        "/alerts/notifications", headers={"Authorization": f"Bearer {token}"}
    )
    assert empty_notifications.json() == []

    no_alerts = client.get(
        "/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(no_alerts.json(), list)
    assert len(no_alerts.json()) == 0

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

    have_alerts = client.get(
        "/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(have_alerts.json(), list)
    assert len(have_alerts.json()) == 1

    empty_notifications2 = client.get(
        "/alerts/notifications", headers={"Authorization": f"Bearer {token}"}
    )
    assert empty_notifications2.json() == []

    client.get("/weather/Moscow", headers={"Authorization": f"Bearer {token}"})

    time.sleep(1)

    not_empty_notifications = client.get(
        "/alerts/notifications", headers={"Authorization": f"Bearer {token}"}
    )
    assert len(not_empty_notifications.json()) == 1
    assert not_empty_notifications.json()[0]["location"] == "Moscow"
    assert not_empty_notifications.json()[0]["column_name"] == "humidity"
    assert not_empty_notifications.json()[0]["comparator"] == ">="
    assert not_empty_notifications.json()[0]["number"] == 75
    assert not_empty_notifications.json()[0]["actual_number"] == 78
    assert not_empty_notifications.json()[0]["id"] == 1


def test_get_notifications_not_authenticated(monkeypatch, _):  # noqa: F811:
    """
    Test getting list of notifications when user is not authenticated

    This test tries to get list
     of notifications when user is not authenticated,
      so API should return error message.
    """
    monkeypatch.setattr("requests.get", mocked_weather_request)

    response = client.get("/alerts/notifications")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_get_empty_notifications(monkeypatch, _):  # noqa: F811:
    """
    Test getting empty list of notifications

    This test tries to add irrelevant alert,
     so the list should remain empty.
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

    empty_notifications = client.get(
        "/alerts/notifications", headers={"Authorization": f"Bearer {token}"}
    )
    assert empty_notifications.json() == []

    no_alerts = client.get(
        "/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(no_alerts.json(), list)
    assert len(no_alerts.json()) == 0

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

    have_alerts = client.get(
        "/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(have_alerts.json(), list)
    assert len(have_alerts.json()) == 1

    empty_notifications2 = client.get(
        "/alerts/notifications", headers={"Authorization": f"Bearer {token}"}
    )
    assert empty_notifications2.json() == []

    client.get("/weather/Moscow", headers={"Authorization": f"Bearer {token}"})

    time.sleep(1)

    empty_notifications = client.get(
        "/alerts/notifications", headers={"Authorization": f"Bearer {token}"}
    )
    assert len(empty_notifications.json()) == 0
