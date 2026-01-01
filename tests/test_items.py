def test_items_unauthorized(client):
    response = client.get("/v1/items")
    assert response.status_code == 401


def test_items_authorized(client):
    # Login first
    login = client.post(
        "/v1/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "StrongPass123",
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/v1/items", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)