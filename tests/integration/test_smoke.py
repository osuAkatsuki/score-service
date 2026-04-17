from __future__ import annotations

from fastapi.testclient import TestClient


def test_status_endpoint_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert response.json() == {"server_status": 1}


def test_health_endpoint_connects_to_db_and_redis(client: TestClient) -> None:
    response = client.get("/_health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
