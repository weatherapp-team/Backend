from core.database import get_db
from main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_delete_location(_):
    """
    Test deleting location

    This test tries to create and shortly delete location
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
    client.post("/locations?location=Moscow", headers={"Authorization": f"Bearer {token}"})

    response = client.delete("/locations?location=Moscow", headers={"Authorization": f"Bearer {token}"})

    locations = client.get("/locations", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["message"] == "Location deleted successfully"

    assert isinstance(locations.json(), list)
    assert len(locations.json()) == 0


def test_delete_location_not_authenticated(_):
    """
    Test deleting location when not authenticated.

    This test tries to delete location when user is not authenticated, so API should return error message.
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
    client.post("/locations?location=Moscow", headers={"Authorization": f"Bearer {token}"})

    response = client.delete("/locations?location=Moscow")

    locations = client.get("/locations", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"
    assert isinstance(locations.json(), list)
    assert len(locations.json()) == 1

def test_delete_location_missing_field(_):
    """
    Test deleting location when missing field

    This test tries to delete location with missing field, so API should return error message.
    """
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
    client.post("/locations?location=Moscow", headers={"Authorization": f"Bearer {token}"})

    response = client.delete("/locations", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 422
