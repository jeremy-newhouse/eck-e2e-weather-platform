"""Tests for the health router endpoints (AC-9, AC-10)."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers.health import router


def _make_session_factory(*, fail: bool = False) -> MagicMock:
    """Return a mock session factory whose context manager optionally raises."""
    mock_session = AsyncMock()
    if fail:
        mock_session.execute.side_effect = Exception("DB connection failed")

    @asynccontextmanager
    async def _factory() -> AsyncGenerator[AsyncMock, None]:
        yield mock_session

    return MagicMock(side_effect=_factory)


def _make_client(
    *,
    pg_fail: bool = False,
    ts_fail: bool = False,
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.state.pg_session_factory = _make_session_factory(fail=pg_fail)
    app.state.ts_session_factory = _make_session_factory(fail=ts_fail)
    return TestClient(app)


@pytest.fixture()
def healthy_client() -> TestClient:
    return _make_client()


@pytest.fixture()
def pg_down_client() -> TestClient:
    return _make_client(pg_fail=True)


@pytest.fixture()
def ts_down_client() -> TestClient:
    return _make_client(ts_fail=True)


@pytest.fixture()
def both_down_client() -> TestClient:
    return _make_client(pg_fail=True, ts_fail=True)


class TestHealthEndpoint:
    def test_health_returns_200_when_both_healthy(
        self, healthy_client: TestClient
    ) -> None:
        response = healthy_client.get("/health")
        assert response.status_code == 200

    def test_health_returns_ok_status_when_both_healthy(
        self, healthy_client: TestClient
    ) -> None:
        data = healthy_client.get("/health").json()
        assert data["status"] == "ok"

    def test_health_returns_service_statuses_when_both_healthy(
        self, healthy_client: TestClient
    ) -> None:
        data = healthy_client.get("/health").json()
        assert "services" in data
        assert data["services"]["postgres"] == "ok"
        assert data["services"]["timescale"] == "ok"

    def test_health_returns_degraded_when_postgres_down(
        self, pg_down_client: TestClient
    ) -> None:
        data = pg_down_client.get("/health").json()
        assert data["status"] == "degraded"
        assert data["services"]["postgres"] == "error"
        assert data["services"]["timescale"] == "ok"

    def test_health_returns_degraded_when_timescale_down(
        self, ts_down_client: TestClient
    ) -> None:
        data = ts_down_client.get("/health").json()
        assert data["status"] == "degraded"
        assert data["services"]["postgres"] == "ok"
        assert data["services"]["timescale"] == "error"

    def test_health_returns_degraded_when_both_down(
        self, both_down_client: TestClient
    ) -> None:
        data = both_down_client.get("/health").json()
        assert data["status"] == "degraded"
        assert data["services"]["postgres"] == "error"
        assert data["services"]["timescale"] == "error"

    def test_health_still_returns_200_when_degraded(
        self, pg_down_client: TestClient
    ) -> None:
        response = pg_down_client.get("/health")
        assert response.status_code == 200


class TestReadyEndpoint:
    def test_ready_returns_200_when_both_healthy(
        self, healthy_client: TestClient
    ) -> None:
        response = healthy_client.get("/ready")
        assert response.status_code == 200

    def test_ready_returns_ready_status_when_both_healthy(
        self, healthy_client: TestClient
    ) -> None:
        data = healthy_client.get("/ready").json()
        assert data["status"] == "ready"

    def test_ready_returns_503_when_postgres_down(
        self, pg_down_client: TestClient
    ) -> None:
        response = pg_down_client.get("/ready")
        assert response.status_code == 503

    def test_ready_returns_not_ready_when_postgres_down(
        self, pg_down_client: TestClient
    ) -> None:
        data = pg_down_client.get("/ready").json()
        assert data["status"] == "not ready"
        assert "error" in data

    def test_ready_returns_503_when_timescale_down(
        self, ts_down_client: TestClient
    ) -> None:
        response = ts_down_client.get("/ready")
        assert response.status_code == 503

    def test_ready_returns_not_ready_when_timescale_down(
        self, ts_down_client: TestClient
    ) -> None:
        data = ts_down_client.get("/ready").json()
        assert data["status"] == "not ready"
        assert "error" in data
