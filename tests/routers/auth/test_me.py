from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_me(_):  # noqa: F811
    """
    Test the profile route.

    This test tries to get the profile of current user.
    """
    user_data = {
        "username": "a.hleborezov",
        "email": "a.hleborezov@bread.example",
        "password": "SuperMegaBread!",
        "full_name": "Alexander Hleborezov",
    }
    register_response = client.post("/auth/register", json=user_data)
    assert register_response.status_code == 201
    user = client.post(
        "/auth/login",
        json={"username": "a.hleborezov", "password": "SuperMegaBread!"},
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer " f"{user.json()['access_token']}"},
    )
    res_json = response.json()

    assert response.status_code == 200
    assert res_json["username"] == user_data["username"]
    assert res_json["email"] == user_data["email"]
    assert res_json["full_name"] == user_data["full_name"]
    assert res_json["disabled"] is False
    assert "password" not in res_json


def test_me_not_authenticated(_):  # noqa: F811
    """
    Test the profile route when not authenticated.

    This test tries to get the profile when user is not authenticated.
    API should return error message.
    """
    response = client.get("/auth/me")
    res_json = response.json()

    assert response.status_code == 403
    assert res_json["detail"] == "Not authenticated"
