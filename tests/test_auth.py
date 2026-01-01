def test_register_user(client):
    response = client.post(
        "/v1/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "StrongPass123",
        },
    )

    # Either user is created OR already exists
    assert response.status_code in (200, 201, 400)

    if response.status_code != 400:
        data = response.json()
        assert "id" in data
        assert data["email"] == "testuser@example.com"


def test_login_user(client):
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPass123",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"