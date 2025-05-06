from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401
from tests.routers.weather.main import mocked_weather_request

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_history(monkeypatch, _):  # noqa: F811
    """
    Test getting weather history.
    Test tries to get weather two times
    and these results should appear in the history.
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

    empty_history = client.get(
        "/weather/Moscow/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert empty_history.status_code == 200
    assert empty_history.json() == []

    monkeypatch.setattr("requests.get", mocked_weather_request)

    response1 = client.get(
        "/weather/Moscow", headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 200

    response2 = client.get(
        "/weather/Moscow", headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code == 200

    nonempty_history = client.get(
        "/weather/Moscow/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert nonempty_history.status_code == 200
    assert len(nonempty_history.json()) == 2

    assert (
        nonempty_history.json()[0]["timestamp"]
        == response1.json()["timestamp"]
    )
    assert (
        nonempty_history.json()[1]["timestamp"]
        == response2.json()["timestamp"]
    )


def test_get_history_from_nonexistent_location(monkeypatch, _):  # noqa: F811
    """
    Test getting weather history from nonexistent location.

    This test gets weather from nonexistent location,
    so API should return error
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

    empty_history = client.get(
        "/weather/Bebraversity/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert empty_history.status_code == 200
    assert empty_history.json() == []

    monkeypatch.setattr("requests.get", mocked_weather_request)

    response1 = client.get(
        "/weather/Bebraversity", headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code == 500

    still_empty_history = client.get(
        "/weather/Moscow/history", headers={"Authorization": f"Bearer {token}"}
    )
    assert still_empty_history.status_code == 200
    assert still_empty_history.json() == []


def test_get_history_not_authenticated(_):  # noqa: F811
    """
    Test getting weather history when user is not authenticated

    This test gets weather history when user is not authenticated,
    so API should return error message.
    """
    empty_history = client.get("/weather/Moscow/history")
    assert empty_history.status_code == 403
    assert empty_history.json()["detail"] == "Not authenticated"
