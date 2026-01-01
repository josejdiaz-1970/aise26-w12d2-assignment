def test_health(client):
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_detailed(client):
    response = client.get("/v1/health/detailed")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "checks" in response.json()