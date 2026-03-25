"""Tests for Pydantic v2 schema models in backend/schemas/api.py."""

from datetime import datetime, timezone

import pytest

from backend.schemas.api import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MetricBucket,
    MetricsResponse,
    WeatherResponse,
)


class TestWeatherResponse:
    def test_valid_construction(self) -> None:
        ts = datetime(2026, 3, 25, 14, 32, 0, tzinfo=timezone.utc)
        w = WeatherResponse(
            city="London",
            temperature=12.4,
            humidity=65.0,
            wind_speed=4.2,
            description="Partly Cloudy",
            timestamp=ts,
        )
        assert w.city == "London"
        assert w.temperature == 12.4
        assert w.humidity == 65.0
        assert w.wind_speed == 4.2
        assert w.description == "Partly Cloudy"
        assert w.timestamp == ts

    def test_serialises_to_dict(self) -> None:
        ts = datetime(2026, 3, 25, 14, 32, 0, tzinfo=timezone.utc)
        w = WeatherResponse(
            city="Tokyo",
            temperature=20.0,
            humidity=70.0,
            wind_speed=3.0,
            description="Clear",
            timestamp=ts,
        )
        data = w.model_dump()
        assert data["city"] == "Tokyo"
        assert isinstance(data["timestamp"], datetime)

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(Exception):
            WeatherResponse(  # type: ignore[call-arg]
                temperature=12.4,
                humidity=65.0,
                wind_speed=4.2,
                description="Clear",
                timestamp=datetime.now(tz=timezone.utc),
            )


class TestMetricBucket:
    def test_valid_construction(self) -> None:
        ts = datetime(2026, 3, 25, 13, 0, 0, tzinfo=timezone.utc)
        mb = MetricBucket(bucket=ts, metric_name="temperature", avg_value=12.1)
        assert mb.metric_name == "temperature"
        assert mb.avg_value == 12.1

    def test_avg_value_is_float(self) -> None:
        ts = datetime(2026, 3, 25, 13, 0, 0, tzinfo=timezone.utc)
        mb = MetricBucket(bucket=ts, metric_name="humidity", avg_value=64)
        assert isinstance(mb.avg_value, float)


class TestMetricsResponse:
    def test_empty_metrics_list(self) -> None:
        mr = MetricsResponse(city="Paris", range="1h", metrics=[])
        assert mr.metrics == []
        assert mr.city == "Paris"
        assert mr.range == "1h"

    def test_with_metric_buckets(self) -> None:
        ts = datetime(2026, 3, 25, 13, 0, 0, tzinfo=timezone.utc)
        buckets = [
            MetricBucket(bucket=ts, metric_name="temperature", avg_value=12.1),
            MetricBucket(bucket=ts, metric_name="humidity", avg_value=64.5),
        ]
        mr = MetricsResponse(city="London", range="7d", metrics=buckets)
        assert len(mr.metrics) == 2
        assert mr.metrics[0].metric_name == "temperature"


class TestChatRequest:
    def test_minimal_required_fields(self) -> None:
        req = ChatRequest(message="What's the weather?")
        assert req.message == "What's the weather?"
        assert req.session_id is None
        assert req.city is None

    def test_all_fields(self) -> None:
        req = ChatRequest(
            session_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
            message="Should I bring an umbrella?",
            city="London",
        )
        assert req.session_id == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        assert req.city == "London"

    def test_missing_message_raises(self) -> None:
        with pytest.raises(Exception):
            ChatRequest(session_id=None)  # type: ignore[call-arg]


class TestChatResponse:
    def test_valid_construction(self) -> None:
        ts = datetime(2026, 3, 25, 14, 32, 15, tzinfo=timezone.utc)
        resp = ChatResponse(
            session_id="3fa85f64-5717-4562-b3fc-2c963f66afa6",
            role="assistant",
            content="It looks partly cloudy.",
            created_at=ts,
        )
        assert resp.role == "assistant"
        assert resp.session_id == "3fa85f64-5717-4562-b3fc-2c963f66afa6"


class TestHealthResponse:
    def test_ok_status(self) -> None:
        h = HealthResponse(status="ok", services={"postgres": "ok", "timescale": "ok"})
        assert h.status == "ok"
        assert h.services["postgres"] == "ok"
        assert h.services["timescale"] == "ok"

    def test_degraded_status(self) -> None:
        h = HealthResponse(
            status="degraded", services={"postgres": "ok", "timescale": "error"}
        )
        assert h.status == "degraded"
        assert h.services["timescale"] == "error"
