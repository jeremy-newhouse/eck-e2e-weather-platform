"""Tests for the metrics router endpoint."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers.metrics import router
from backend.schemas.api import MetricBucket, MetricsResponse


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def _metrics_response(city: str = "london", range_str: str = "1h") -> MetricsResponse:
    ts = datetime(2024, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    return MetricsResponse(
        city=city,
        range=range_str,
        metrics=[
            MetricBucket(bucket=ts, metric_name="temperature", avg_value=15.3),
        ],
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetMetricsEndpoint:
    def test_returns_200_for_valid_city_and_default_range(
        self, client: TestClient
    ) -> None:
        with patch(
            "backend.services.metrics_service.get_metrics",
            new=AsyncMock(return_value=_metrics_response()),
        ):
            response = client.get("/metrics/london")
        assert response.status_code == 200

    def test_response_body_matches_schema(self, client: TestClient) -> None:
        with patch(
            "backend.services.metrics_service.get_metrics",
            new=AsyncMock(return_value=_metrics_response("paris", "6h")),
        ):
            response = client.get("/metrics/paris?range=6h")
        data = response.json()
        assert data["city"] == "paris"
        assert data["range"] == "6h"
        assert isinstance(data["metrics"], list)

    def test_default_range_is_1h(self, client: TestClient) -> None:
        captured: list[str] = []

        async def _capture(
            city: str, range_str: str, request: object
        ) -> MetricsResponse:  # type: ignore[override]
            captured.append(range_str)
            return _metrics_response(city, range_str)

        with patch(
            "backend.services.metrics_service.get_metrics", side_effect=_capture
        ):
            client.get("/metrics/berlin")
        assert captured == ["1h"]

    def test_explicit_range_passed_to_service(self, client: TestClient) -> None:
        captured: list[str] = []

        async def _capture(
            city: str, range_str: str, request: object
        ) -> MetricsResponse:  # type: ignore[override]
            captured.append(range_str)
            return _metrics_response(city, range_str)

        with patch(
            "backend.services.metrics_service.get_metrics", side_effect=_capture
        ):
            client.get("/metrics/berlin?range=7d")
        assert captured == ["7d"]

    def test_invalid_range_returns_422(self, client: TestClient) -> None:
        response = client.get("/metrics/london?range=3h")
        assert response.status_code == 422

    def test_city_passed_to_service(self, client: TestClient) -> None:
        captured: list[str] = []

        async def _capture(
            city: str, range_str: str, request: object
        ) -> MetricsResponse:  # type: ignore[override]
            captured.append(city)
            return _metrics_response(city, range_str)

        with patch(
            "backend.services.metrics_service.get_metrics", side_effect=_capture
        ):
            client.get("/metrics/amsterdam?range=24h")
        assert captured == ["amsterdam"]
