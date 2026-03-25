"""Metrics service — weather_metrics TimescaleDB operations."""

from datetime import datetime, timezone

from fastapi import HTTPException, Request
from sqlalchemy import text

from backend.models.timescale import WeatherMetric
from backend.schemas.api import MetricBucket, MetricsResponse

RANGE_INTERVALS: dict[str, tuple[str, str]] = {
    "1h": ("1 hour", "1 hour"),
    "6h": ("6 hours", "1 hour"),
    "24h": ("24 hours", "1 hour"),
    "7d": ("7 days", "12 hours"),
}


async def ingest(
    city: str,
    temperature: float,
    humidity: float,
    wind_speed: float,
    request: Request,
) -> None:
    """Write 3 metric rows to TimescaleDB (AC-4).

    Args:
        city: City name; stored lower-cased.
        temperature: Current temperature in Celsius.
        humidity: Current humidity percentage.
        wind_speed: Current wind speed in m/s.
        request: FastAPI request carrying ``app.state.ts_session_factory``.
    """
    session_factory = request.app.state.ts_session_factory
    now = datetime.now(tz=timezone.utc)
    metrics = [
        WeatherMetric(
            city=city.lower(),
            metric_name="temperature",
            value=temperature,
            recorded_at=now,
        ),
        WeatherMetric(
            city=city.lower(),
            metric_name="humidity",
            value=humidity,
            recorded_at=now,
        ),
        WeatherMetric(
            city=city.lower(),
            metric_name="wind_speed",
            value=wind_speed,
            recorded_at=now,
        ),
    ]
    async with session_factory() as session:
        session.add_all(metrics)
        await session.commit()


async def get_metrics(city: str, range_str: str, request: Request) -> MetricsResponse:
    """Return time-bucket aggregated weather metrics for a city (AC-5).

    Args:
        city: City name; matched case-insensitively against stored records.
        range_str: One of ``"1h"``, ``"6h"``, ``"24h"``, ``"7d"``.
        request: FastAPI request carrying ``app.state.ts_session_factory``.

    Returns:
        :class:`MetricsResponse` containing aggregated :class:`MetricBucket` rows.

    Raises:
        HTTPException: 422 when ``range_str`` is not a recognised interval key.
    """
    if range_str not in RANGE_INTERVALS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid range: {range_str}. Must be one of: 1h, 6h, 24h, 7d",
        )

    interval_ago, bucket_size = RANGE_INTERVALS[range_str]

    query = text("""
        SELECT
            time_bucket(CAST(:bucket_size AS INTERVAL), recorded_at) AS bucket,
            metric_name,
            AVG(value) AS avg_value
        FROM weather_metrics
        WHERE city = :city
          AND recorded_at > NOW() - CAST(:interval_ago AS INTERVAL)
        GROUP BY bucket, metric_name
        ORDER BY bucket ASC
    """)

    session_factory = request.app.state.ts_session_factory
    async with session_factory() as session:
        result = await session.execute(
            query,
            {
                "city": city.lower(),
                "bucket_size": bucket_size,
                "interval_ago": interval_ago,
            },
        )
        rows = result.fetchall()

    buckets = [
        MetricBucket(
            bucket=row.bucket,
            metric_name=row.metric_name,
            avg_value=row.avg_value,
        )
        for row in rows
    ]

    return MetricsResponse(city=city, range=range_str, metrics=buckets)
