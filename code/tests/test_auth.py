import uuid

from app import app


client = app.test_client()


def test_register_login_me():
    username = "test_" + uuid.uuid4().hex[:8]
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "123456"},
    )
    assert response.status_code == 200
    token = response.get_json()["token"]

    me_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.get_json()["username"] == username

    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "123456"},
    )
    assert login_response.status_code == 200
    assert "token" in login_response.get_json()
