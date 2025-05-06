from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_edit_alert(_):
    """
    Test editing alert

    This test tries to edit alert.
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
            "number": 25,
        }
    )

    edited_location = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 25,
        }
    )
    assert edited_location.status_code == 200
    assert edited_location.json()['message'] == "Alert edited successfully"

    edited_column_name = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "temperature",
            "comparator": ">=",
            "number": 25,
        }
    )
    assert edited_column_name.status_code == 200
    assert edited_column_name.json()['message'] == "Alert edited successfully"

    edited_comparator = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "temperature",
            "comparator": "<=",
            "number": 25,
        }
    )
    assert edited_comparator.status_code == 200
    assert edited_comparator.json()['message'] == "Alert edited successfully"

    edited_number = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "temperature",
            "comparator": "<=",
            "number": 26,
        }
    )
    assert edited_number.status_code == 200
    assert edited_number.json()['message'] == "Alert edited successfully"

    alerts = client.get(url="/alerts", headers={"Authorization": f"Bearer {token}"})
    assert alerts.status_code == 200
    assert alerts.json()[0]['id'] == 1
    assert alerts.json()[0]['location'] == 'London'
    assert alerts.json()[0]['column_name'] == 'temperature'
    assert alerts.json()[0]['comparator'] == '<='
    assert alerts.json()[0]['number'] == 26


def test_edit_alert_not_authenticated(_):
    """
    Test editing alert when not authenticated.

    This test tries to edit alert when user is not authenticated, so API should return error message.
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
        }
    )

    response = client.put(
        url="/alerts",
        json={
            "id": 1,
            "location": "London",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 25,
        }
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"


    
def test_edit_alert_wrong_comparator(_):
    """
    Test editing alert with wrong comparator.

    This test tries to edit alert when user specified wrong comparator, so API should return error message.
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
        }
    )

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "humidity",
            "comparator": "kmemrkio998",
            "number": 25,
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Comparator or column is invalid"

def test_edit_alert_wrong_column(_):
    """
    Test editing alert with wrong column.

    This test tries to edit alert when user specified wrong column, so API should return error message.
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
        }
    )

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "visibility",
            "comparator": ">=",
            "number": 25,
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Comparator or column is invalid"

def test_edit_alert_number_as_string(_):
    """
    Test editing alert with number as string.

    This test tries to edit alert when user specified string instead of number, so API should return error message.
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
        }
    )

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "London",
            "column_name": "visibility",
            "comparator": ">=",
            "number": "very_yummy_honey",
        }
    )
    
    assert response.status_code == 422

def test_edit_alert_empty_fields(_):
    """
    Test editing alert with empty fields.

    This test tries to edit alert when user specified empty fields, so API should return error message.
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
        }
    )

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": 1,
            "location": "",
            "column_name": "",
            "comparator": "",
            "number": "",
        }
    )

    assert response.status_code == 422

def test_edit_alert_empty_object(_):
    """
    Test editing alert with empty object.

    This test tries to edit alert when user specified empty object, so API should return error message.
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
        }
    )

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={}
    )
    assert response.status_code == 422

def test_edit_alert_invalid_id(_):
    """
    Test editing alert with invalid id.

    This test tries to edit alert when user specified invalid id, so API should return error message.
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
        }
    )

    response = client.put(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "id": -1,
            "location": "London",
            "column_name": "humidity",
            "comparator": ">=",
            "number": 75,
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Alert not found"
