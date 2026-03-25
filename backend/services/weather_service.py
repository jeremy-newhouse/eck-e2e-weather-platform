"""Weather service — fetches current weather from OpenWeatherMap and caches results."""

from datetime import datetime, timezone

from cachetools import TTLCache
from fastapi import HTTPException, Request

from backend.config import settings
from backend.schemas.api import WeatherResponse

cache: TTLCache[str, WeatherResponse] = TTLCache(maxsize=100, ttl=300)


async def get_weather(city: str, request: Request) -> WeatherResponse:
    """Return current weather for *city*, using a 5-minute in-process cache.

    Flow:
    1. Return cached result when present.
    2. Resolve *city* to lat/lon via OWM Geocoding API.
    3. Fetch current conditions via OWM One Call 3.0.
    4. Persist raw metrics to TimescaleDB (AC-4).
    5. Cache and return a :class:`~backend.schemas.api.WeatherResponse`.

    Args:
        city: Human-readable city name (case-insensitive cache key).
        request: FastAPI request; ``request.app.state.owm_client`` is the
            shared :class:`httpx.AsyncClient` for OpenWeatherMap.

    Returns:
        Populated :class:`~backend.schemas.api.WeatherResponse`.

    Raises:
        HTTPException(404): City not recognised by OWM geocoding.
        HTTPException(502): OWM API returned a non-200 response.
    """
    key = f"weather:{city.lower()}"
    if key in cache:
        return cache[key]

    owm_client = request.app.state.owm_client

    # --- Geocoding -----------------------------------------------------------
    geo_resp = await owm_client.get(
        "/geo/1.0/direct",
        params={"q": city, "limit": 1, "appid": settings.openweather_api_key},
    )
    if geo_resp.status_code != 200:
        raise HTTPException(
            status_code=502, detail={"error": "Weather API unavailable"}
        )

    geo_data = geo_resp.json()
    if not geo_data:
        raise HTTPException(
            status_code=404, detail={"error": "City not found", "city": city}
        )

    lat: float = geo_data[0]["lat"]
    lon: float = geo_data[0]["lon"]

    # --- One Call 3.0 --------------------------------------------------------
    weather_resp = await owm_client.get(
        "/data/3.0/onecall",
        params={
            "lat": lat,
            "lon": lon,
            "units": "metric",
            "appid": settings.openweather_api_key,
            "exclude": "minutely,hourly,daily,alerts",
        },
    )
    if weather_resp.status_code != 200:
        raise HTTPException(
            status_code=502, detail={"error": "Weather API unavailable"}
        )

    weather_data = weather_resp.json()
    current = weather_data.get("current", {})

    response = WeatherResponse(
        city=city,
        temperature=current.get("temp", 0.0),
        humidity=float(current.get("humidity", 0)),
        wind_speed=current.get("wind_speed", 0.0),
        description=current.get("weather", [{}])[0].get("description", ""),
        timestamp=datetime.fromtimestamp(current.get("dt", 0), tz=timezone.utc),
    )

    # --- Persist metrics (AC-4) — imported here to avoid circular import -----
    from backend.services.metrics_service import ingest  # noqa: PLC0415

    await ingest(
        city, response.temperature, response.humidity, response.wind_speed, request
    )

    cache[key] = response
    return response
