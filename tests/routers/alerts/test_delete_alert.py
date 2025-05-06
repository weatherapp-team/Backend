from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_delete_alert(_):
    """
    Test deleting alert

    This test tries to create and shortly delete alert
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
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

    response = client.request(
        method="DELETE",
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1
        }
    )

    alerts = client.get("/alerts", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "Alert deleted successfully"
    assert isinstance(alerts.json(), list)
    assert len(alerts.json()) == 0

def test_delete_alert_not_authenticated(_):
    """
    Test deleting alert when not authenticated.

    This test tries to delete alert when user is not authenticated, so API should return error message.
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
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

    response = client.request(
        method="DELETE",
        url="/alerts",
        json={
            "id": 1
        }
    )

    alerts = client.get("/alerts", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"
    assert isinstance(alerts.json(), list)
    assert len(alerts.json()) == 1

def test_delete_alert_missing_field(_):
    """
    Test deleting alert when missing field

    This test tries to create and shortly delete alert with missing field, so API should return error message
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
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

    response = client.request(
        method="DELETE",
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )

    assert response.status_code == 422

def test_delete_alert_empty_field(_):
    """
    Test deleting alert with empty field

    This test tries to create and shortly delete alert with empty field, so API should return error message
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
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

    response = client.request(
        method="DELETE",
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": ""
        }
    )

    assert response.status_code == 422

def test_delete_alert_invalid_id(_):
    """
    Test deleting alert with invalid id

    This test tries to create and shortly delete alert with invalid id, so API should return error message
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
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

    response = client.request(
        method="DELETE",
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": -1
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Alert not found"
