from core.database import get_db
from main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_locations(_):  # noqa: F811:
    """
    Test getting locations

    This test tries to test thoroughly
    endpoint for getting locations.
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

    no_locations = client.get(
        "/locations", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(no_locations.json(), list)
    assert len(no_locations.json()) == 0

    client.post(
        "/locations?location=Moscow",
        headers={"Authorization": f"Bearer {token}"},
    )
    client.post(
        "/locations?location=Innopolis",
        headers={"Authorization": f"Bearer {token}"},
    )

    have_locations = client.get(
        "/locations", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(have_locations.json(), list)
    assert len(have_locations.json()) == 2

    client.delete(
        "/locations?location=Moscow",
        headers={"Authorization": f"Bearer {token}"},
    )

    one_location = client.get(
        "/locations", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(one_location.json(), list)
    assert len(one_location.json()) == 1


def test_get_locations_not_authenticated(_):  # noqa: F811:
    """
    Test getting locations when not authenticated.

    This test tries to get locations when user is not authenticated,
    so API should return error message.
    """
    response = client.get("/locations")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"
