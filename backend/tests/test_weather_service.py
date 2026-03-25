"""Unit tests for backend.services.weather_service.

All OWM HTTP calls and metrics ingestion are mocked so tests run without
network access or a real database.
"""

from datetime import datetime
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import FastAPI

from backend.schemas.api import WeatherResponse
from backend.services import weather_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GEO_RESPONSE: list[dict[str, Any]] = [
    {"lat": 51.5074, "lon": -0.1278, "name": "London"}
]

ONECALL_RESPONSE: dict[str, Any] = {
    "current": {
        "dt": 1711368000,
        "temp": 12.5,
        "humidity": 72,
        "wind_speed": 4.2,
        "weather": [{"description": "light rain"}],
    }
}


def _make_httpx_response(status_code: int, json_data: Any) -> httpx.Response:
    """Build a minimal httpx.Response for mocking."""
    return httpx.Response(status_code, json=json_data)


def _make_request(owm_client: Any) -> MagicMock:
    """Return a fake FastAPI Request with the given OWM client on app.state."""
    app = FastAPI()
    app.state.owm_client = owm_client
    request = MagicMock()
    request.app = app
    return request


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_cache() -> None:
    """Wipe the TTL cache before every test to prevent cross-test pollution."""
    weather_service.cache.clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetWeatherSuccess:
    """AC-1: Successful weather fetch returns a correctly shaped WeatherResponse."""

    @pytest.mark.asyncio
    async def test_returns_weather_response_shape(self) -> None:
        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            side_effect=[
                _make_httpx_response(200, GEO_RESPONSE),
                _make_httpx_response(200, ONECALL_RESPONSE),
            ]
        )
        request = _make_request(owm_client)

        with patch("backend.services.metrics_service.ingest", new=AsyncMock()):
            result = await weather_service.get_weather("London", request)

        assert isinstance(result, WeatherResponse)
        assert result.city == "London"
        assert result.temperature == 12.5
        assert result.humidity == 72.0
        assert result.wind_speed == 4.2
        assert result.description == "light rain"
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_returns_weather_response_with_correct_city(self) -> None:
        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            side_effect=[
                _make_httpx_response(200, GEO_RESPONSE),
                _make_httpx_response(200, ONECALL_RESPONSE),
            ]
        )
        request = _make_request(owm_client)

        with patch("backend.services.metrics_service.ingest", new=AsyncMock()):
            result = await weather_service.get_weather("London", request)

        assert result.city == "London"


class TestGetWeatherCache:
    """AC-2: Second call with the same city must not issue new OWM requests."""

    @pytest.mark.asyncio
    async def test_cache_hit_skips_owm_call(self) -> None:
        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            side_effect=[
                _make_httpx_response(200, GEO_RESPONSE),
                _make_httpx_response(200, ONECALL_RESPONSE),
            ]
        )
        request = _make_request(owm_client)

        with patch("backend.services.metrics_service.ingest", new=AsyncMock()):
            first = await weather_service.get_weather("London", request)
            second = await weather_service.get_weather("London", request)

        # OWM should have been called exactly twice (geo + onecall) on first request
        assert owm_client.get.call_count == 2
        assert first is second

    @pytest.mark.asyncio
    async def test_cache_key_is_case_insensitive(self) -> None:
        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            side_effect=[
                _make_httpx_response(200, GEO_RESPONSE),
                _make_httpx_response(200, ONECALL_RESPONSE),
            ]
        )
        request = _make_request(owm_client)

        with patch("backend.services.metrics_service.ingest", new=AsyncMock()):
            await weather_service.get_weather("London", request)
            await weather_service.get_weather("london", request)

        # Second call (different case) should still hit the cache
        assert owm_client.get.call_count == 2


class TestGetWeatherCityNotFound:
    """AC-3: Empty geocoding response raises HTTP 404."""

    @pytest.mark.asyncio
    async def test_empty_geo_response_raises_404(self) -> None:
        from fastapi import HTTPException

        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            return_value=_make_httpx_response(200, [])  # empty list = city not found
        )
        request = _make_request(owm_client)

        with pytest.raises(HTTPException) as exc_info:
            await weather_service.get_weather("UnknownCity", request)

        assert exc_info.value.status_code == 404
        detail = cast(dict[str, str], exc_info.value.detail)
        assert detail["error"] == "City not found"
        assert detail["city"] == "UnknownCity"


class TestGetWeatherOwmError:
    """Upstream OWM error raises HTTP 502."""

    @pytest.mark.asyncio
    async def test_geo_api_error_raises_502(self) -> None:
        from fastapi import HTTPException

        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            return_value=_make_httpx_response(500, {"message": "internal error"})
        )
        request = _make_request(owm_client)

        with pytest.raises(HTTPException) as exc_info:
            await weather_service.get_weather("London", request)

        assert exc_info.value.status_code == 502
        detail = cast(dict[str, str], exc_info.value.detail)
        assert detail["error"] == "Weather API unavailable"

    @pytest.mark.asyncio
    async def test_onecall_api_error_raises_502(self) -> None:
        from fastapi import HTTPException

        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            side_effect=[
                _make_httpx_response(200, GEO_RESPONSE),
                _make_httpx_response(401, {"message": "unauthorized"}),
            ]
        )
        request = _make_request(owm_client)

        with pytest.raises(HTTPException) as exc_info:
            await weather_service.get_weather("London", request)

        assert exc_info.value.status_code == 502
        detail = cast(dict[str, str], exc_info.value.detail)
        assert detail["error"] == "Weather API unavailable"


class TestGetWeatherIngestsMetrics:
    """AC-4: Metrics ingest is called once per successful cache-miss fetch."""

    @pytest.mark.asyncio
    async def test_ingest_called_on_cache_miss(self) -> None:
        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            side_effect=[
                _make_httpx_response(200, GEO_RESPONSE),
                _make_httpx_response(200, ONECALL_RESPONSE),
            ]
        )
        request = _make_request(owm_client)

        mock_ingest = AsyncMock()

        # Patch ingest on the metrics_service module so the lazy import picks it up
        with patch("backend.services.metrics_service.ingest", mock_ingest):
            result = await weather_service.get_weather("London", request)

        mock_ingest.assert_awaited_once()
        call_args = mock_ingest.call_args
        assert call_args.args[0] == "London"  # city
        assert call_args.args[1] == result.temperature
        assert call_args.args[2] == result.humidity
        assert call_args.args[3] == result.wind_speed

    @pytest.mark.asyncio
    async def test_ingest_not_called_on_cache_hit(self) -> None:
        owm_client = AsyncMock()
        owm_client.get = AsyncMock(
            side_effect=[
                _make_httpx_response(200, GEO_RESPONSE),
                _make_httpx_response(200, ONECALL_RESPONSE),
            ]
        )
        request = _make_request(owm_client)

        mock_ingest = AsyncMock()

        with patch("backend.services.metrics_service.ingest", mock_ingest):
            await weather_service.get_weather("London", request)
            await weather_service.get_weather("London", request)  # cache hit

        # ingest called only once (on the first miss)
        mock_ingest.assert_awaited_once()
