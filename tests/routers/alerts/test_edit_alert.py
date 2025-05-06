from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401

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


def create_test_alert(client, token):
    return client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "Moscow",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 75,
        },
    )


def test_edit_alert(_):  # noqa: F811
    """Test editing alert."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    edits = [{
            "field": "location",
            "data": {"id": 1, "location": "London",
                     "column_name": "humidity", "comparator": ">=",
                     "number": 25,
            }
        },
        {
            "field": "column_name",
            "data": {"id": 1, "location": "London",
                     "column_name": "temperature", "comparator": ">=",
                     "number": 25,
            }
        },
        {
            "field": "comparator",
            "data": {"id": 1, "location": "London",
                     "column_name": "temperature",
                     "comparator": "<=", "number": 25,
            }
        },
        {
            "field": "number",
            "data": {"id": 1, "location": "London",
                     "column_name": "temperature", "comparator": "<=",
                     "number": 26,
            }
        }]
    for edit in edits:
        response = client.put(url="/alerts",
            headers={"Authorization": f"Bearer {token}"},
            json=edit["data"],
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Alert edited successfully"

    alerts = client.get(
        url="/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    alert = alerts.json()[0]
    assert alert["id"] == 1
    assert alert["location"] == "London"
    assert alert["column_name"] == "temperature"
    assert alert["comparator"] == "<="
    assert alert["number"] == 26


def test_edit_alert_not_authenticated(_):  # noqa: F811
    """Test editing alert when not authenticated."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    response = client.put(
        url="/alerts",
        json={
            "id": 1,
            "location": "London",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 25,
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


def test_edit_alert_wrong_comparator(_):  # noqa: F811
    """Test editing alert with wrong comparator."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "humidity",
            "comparator": "kmemrkio998",
            "number": 25,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Comparator or column is invalid"


def test_edit_alert_wrong_column(_):  # noqa: F811
    """Test editing alert with wrong column."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "visibility",
            "comparator": ">=",
            "number": 25,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Comparator or column is invalid"


def test_edit_alert_number_as_string(_):  # noqa: F811
    """Test editing alert with number as string."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "visibility",
            "comparator": ">=",
            "number": "very_yummy_honey",
        },
    )
    assert response.status_code == 422


def test_edit_alert_empty_fields(_):  # noqa: F811
    """Test editing alert with empty fields."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "",
            "column_name": "",
            "comparator": "",
            "number": "",
        },
    )
    assert response.status_code == 422


def test_edit_alert_empty_object(_):  # noqa: F811
    """Test editing alert with empty object."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )
    assert response.status_code == 422


def test_edit_alert_invalid_id(_):  # noqa: F811
    """Test editing alert with invalid id."""
    token = register_and_login_user(client)
    create_test_alert(client, token)

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": -1,
            "location": "London",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 75,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Alert not found"
