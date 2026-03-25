"""Tests for the health router endpoints."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from backend.routers.health import router


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert data["status"] == "ok"

    def test_health_returns_service_statuses(self, client: TestClient) -> None:
        data = client.get("/health").json()
        assert "services" in data
        assert data["services"]["postgres"] == "ok"
        assert data["services"]["timescale"] == "ok"


class TestReadyEndpoint:
    def test_ready_returns_200(self, client: TestClient) -> None:
        response = client.get("/ready")
        assert response.status_code == 200

    def test_ready_returns_ready_status(self, client: TestClient) -> None:
        data = client.get("/ready").json()
        assert data["status"] == "ready"
