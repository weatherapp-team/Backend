from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_login(_):
    """
    Test the login route.

    This test registers a new user and tries to log in with valid credentials.
    """
    user_data = {"username": "a.hleborezov",
                 "email": "a.hleborezov@bread.example",
                 "password": "SuperMegaBread!"}
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201
    response = client.post("/auth/login",
                           json={"username": "a.hleborezov",
                                 "password": "SuperMegaBread!"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_empty_fields(_):
    """
    Test the login procedure with empty fields.

    User may accidentaly send request with empty fields,
    so the API should not make request to the database.
    """
    response = client.post("/auth/login",
                           json={"username": "", "password": ""})
    # TODO: currently it returns 401!
    assert response.status_code == 422


def test_login_empty_objects(_):
    """
    Test the login procedure with empty object.

    API should return error if user sends empty object.
    """
    response = client.post("/auth/login", json={})
    assert response.status_code == 422
