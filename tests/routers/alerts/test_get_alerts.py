from core.database import get_db
from src.main import app
from fastapi.testclient import TestClient
from tests.main import override_get_db
from tests.main import test_db as _  # noqa: F401

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_get_alerts(_):  # noqa: F811:
    """
    Test getting alerts

    This test tries to test thoroughly endpoint for getting alerts.
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

    no_alerts = client.get(
        "/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(no_alerts.json(), list)
    assert len(no_alerts.json()) == 0
    client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location": "Moscow", "column_name": "humidity",
            "comparator": ">=", "number": 75,
        },
    )
    client.post(
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={"location": "Innopolis", "column_name": "temperature",
            "comparator": ">", "number": 20,
        },
    )
    have_alerts = client.get(
        "/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(have_alerts.json(), list)
    assert len(have_alerts.json()) == 2
    client.request(
        method="DELETE",
        url="/alerts",
        headers={"Authorization": f"Bearer {token}"},
        json={"id": have_alerts.json()[0]["id"]},
    )
    one_location = client.get(
        "/alerts", headers={"Authorization": f"Bearer {token}"}
    )
    assert isinstance(one_location.json(), list)
    assert len(one_location.json()) == 1
    assert one_location.json()[0]["location"] == "Innopolis"


def test_get_alerts_not_authenticated(_):  # noqa: F811:
    """
    Test getting alerts when not authenticated.

    This test tries to get alerts when
    user is not authenticated, so API should return error message.
    """
    response = client.get("/alerts")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authenticated"
