def test_valid_login_returns_token(client):
    response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "admin1234"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["role"] == "admin"
    assert "access_token" in payload


def test_invalid_password_is_rejected(client):
    response = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "unauthorized"


def test_inactive_user_cannot_login(client):
    response = client.post(
        "/auth/login",
        json={"email": "inactive@example.com", "password": "inactive1234"},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["message"] == "Only active users can authenticate."


def test_protected_route_requires_token(client):
    response = client.get("/users")

    assert response.status_code == 401
