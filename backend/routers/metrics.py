"""Metrics router: GET /api/metrics/{city}."""

from typing import Annotated, Literal

from fastapi import APIRouter, Query, Request

from backend.schemas.api import MetricsResponse
from backend.services import metrics_service

router = APIRouter(tags=["metrics"])


@router.get("/metrics/{city}", response_model=MetricsResponse)
async def get_metrics(
    city: str,
    range: Annotated[Literal["1h", "6h", "24h", "7d"], Query()] = "1h",
    request: Request = None,  # type: ignore[assignment]
) -> MetricsResponse:
    """Return time-bucket aggregated weather metrics for a city.

    Args:
        city: City name (path parameter).
        range: Time window — one of ``1h``, ``6h``, ``24h``, ``7d``. Defaults to ``1h``.
        request: Injected by FastAPI; provides access to ``app.state``.

    Returns:
        :class:`MetricsResponse` with aggregated metric buckets.
    """
    return await metrics_service.get_metrics(city, range, request)
