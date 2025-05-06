from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_add_alert(_):  # noqa: F811
    """
    Test adding alert

    This test tries to save alerts.
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

    tests_alerts = [
        {
            "location": "Moscow",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 75,
        },
        {
            "location": "London",
            "column_name": "temperature",
            "comparator": "<=",
            "number": 15,
        },
        {
            "location": "Paris",
            "column_name": "pressure",
            "comparator": ">",
            "number": 600,
        },
        {
            "location": "Innopolis",
            "column_name": "temperature",
            "comparator": "<",
            "number": 18,
        },
    ]

    i = 1
    for test in tests_alerts:
        idx = i - 1
        response = client.post(
            url="/alerts",
            headers={"Authorization": f"Bearer {token}"},
            json=test,
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Alert created successfully"

        locations = client.get(
            "/alerts", headers={"Authorization": f"Bearer {token}"}
        )
        assert isinstance(locations.json(), list)
        assert len(locations.json()) == i
        assert locations.json()[idx]["location"] == test["location"]
        assert locations.json()[idx]["column_name"] == test["column_name"]
        assert locations.json()[idx]["comparator"] == test["comparator"]
        assert locations.json()[idx]["number"] == test["number"]
        assert locations.json()[idx]["id"] == i
        i += 1


def test_add_alert_not_authenticated(_):  # noqa: F811
    """
    Test adding alert when not authenticated.

    This test tries to save alert when
     user is not authenticated, so API should return error message.
    """

    response = client.post(
        url="/alerts",
        json={
            "location": "Moscow",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 75,
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_add_alert_wrong_comparator(_):  # noqa: F811
    """
    Test adding alert with wrong comparator.

    This test tries to save alert when
     user specified wrong comparator, so API should return error message.
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

    response = client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "Moscow",
            "column_name": "humidity",
            "comparator": "!~9409dfokj",
            "number": 75,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Comparator or column is invalid"


def test_add_alert_wrong_column(_):  # noqa: F811
    """
    Test adding alert with wrong column.

    This test tries to save alert when
    user specified wrong column, so API should return error message.
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

    response = client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "Moscow",
            "column_name": "visibility",
            "comparator": ">=",
            "number": 75,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Comparator or column is invalid"


def test_add_alert_number_as_string(_):  # noqa: F811
    """
    Test adding alert with number as string.

    This test tries to save alert when
     user specified string instead of number,
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

    response = client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "Moscow",
            "column_name": "visibility",
            "comparator": ">=",
            "number": "very_yummy_honey",
        },
    )
    assert response.status_code == 422


def test_add_alert_empty_fields(_):  # noqa: F811
    """
    Test adding alert with empty fields.

    This test tries to save alert when
     user specified empty fields, so API should return error message.
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

    response = client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "",
            "column_name": "",
            "comparator": "",
            "number": 23,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Comparator or column is invalid"


def test_add_alert_empty_object(_):  # noqa: F811
    """
    Test adding alert with empty object.

    This test tries to save alert when
    user specified empty object, so API should return error message.
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

    response = client.post(
        url="/alerts", headers={"Authorization": f"Bearer {token}"}, json={}
    )
    assert response.status_code == 422
