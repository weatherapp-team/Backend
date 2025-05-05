from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register(_):
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    assert response.json()["message"] == "User created successfully"


def test_register_duplicate_user(_):
    user_data = {"username": "test_user", "email": "test_user@test.example", "password": "testpassword"}
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"

def test_register_missing_fields(_):
    user_data = {"username": "test_user", "password": "testpassword"}
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 422

def test_register_empty_fields(_):
    user_data = {"username": "", "email": "", "password": ""}
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 422


def test_register_empty_object(_):
    user_data = {}
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422