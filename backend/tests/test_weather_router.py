"""Tests for the weather router endpoint (AC-1, AC-3)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from backend.routers.weather import router
from backend.schemas.api import WeatherResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _weather_response(city: str = "London") -> WeatherResponse:
    return WeatherResponse(
        city=city,
        temperature=12.5,
        humidity=72.0,
        wind_speed=4.2,
        description="light rain",
        timestamp=datetime(2024, 3, 25, 12, 0, 0, tzinfo=timezone.utc),
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetWeatherRouter:
    """Router-level tests for GET /weather/{city}."""

    def test_returns_200_for_valid_city(self, client: TestClient) -> None:
        with patch(
            "backend.services.weather_service.get_weather",
            new=AsyncMock(return_value=_weather_response("London")),
        ):
            response = client.get("/weather/London")
        assert response.status_code == 200

    def test_response_body_matches_schema(self, client: TestClient) -> None:
        with patch(
            "backend.services.weather_service.get_weather",
            new=AsyncMock(return_value=_weather_response("Paris")),
        ):
            response = client.get("/weather/Paris")
        data = response.json()
        assert data["city"] == "Paris"
        assert data["temperature"] == 12.5
        assert data["humidity"] == 72.0
        assert data["wind_speed"] == 4.2
        assert data["description"] == "light rain"
        assert "timestamp" in data

    def test_city_passed_to_service(self, client: TestClient) -> None:
        captured: list[str] = []

        async def _capture(city: str, request: object) -> WeatherResponse:
            captured.append(city)
            return _weather_response(city)

        with patch(
            "backend.services.weather_service.get_weather", side_effect=_capture
        ):
            client.get("/weather/Berlin")
        assert captured == ["Berlin"]

    def test_404_propagated_from_service(self, client: TestClient) -> None:
        with patch(
            "backend.services.weather_service.get_weather",
            new=AsyncMock(
                side_effect=HTTPException(
                    status_code=404,
                    detail={"error": "City not found", "city": "Nowhere"},
                )
            ),
        ):
            response = client.get("/weather/Nowhere")
        assert response.status_code == 404

    def test_502_propagated_from_service(self, client: TestClient) -> None:
        with patch(
            "backend.services.weather_service.get_weather",
            new=AsyncMock(
                side_effect=HTTPException(
                    status_code=502,
                    detail={"error": "Weather API unavailable"},
                )
            ),
        ):
            response = client.get("/weather/London")
        assert response.status_code == 502
