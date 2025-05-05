from core.database import Base, get_db
from main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_add_location(_):
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)

    user = client.post("/auth/login", json={"username": "test_user", "password": "testpassword"})
    token = user.json()["access_token"]
    
    response = client.post("/locations?location=Moscow", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Location saved successfully"

    locations = client.get("/locations", headers={"Authorization": f"Bearer {token}"})
    assert isinstance(locations.json(), list)
    assert len(locations.json()) == 1