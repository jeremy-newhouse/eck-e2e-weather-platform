"""Weather router — exposes GET /api/weather/{city}."""

from fastapi import APIRouter, Request

from backend.schemas.api import WeatherResponse
from backend.services import weather_service

router = APIRouter(tags=["weather"])


@router.get("/weather/{city}", response_model=WeatherResponse)
async def get_weather(city: str, request: Request) -> WeatherResponse:
    """Return current weather conditions for the given city.

    Args:
        city: City name, e.g. ``London`` or ``New+York``.
        request: Injected FastAPI request; carries shared HTTP/DB clients on
            ``app.state``.

    Returns:
        :class:`~backend.schemas.api.WeatherResponse` with temperature,
        humidity, wind speed, and a short description.
    """
    return await weather_service.get_weather(city, request)
