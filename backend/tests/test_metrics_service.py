"""Tests for metrics_service.get_metrics (AC-5)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from backend.schemas.api import MetricBucket, MetricsResponse
from backend.services import metrics_service


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_row(bucket: datetime, metric_name: str, avg_value: float) -> Any:
    """Create a simple namespace object that mimics a SQLAlchemy Row."""
    row = MagicMock()
    row.bucket = bucket
    row.metric_name = metric_name
    row.avg_value = avg_value
    return row


def _make_request(rows: list[Any]) -> MagicMock:
    """Build a fake FastAPI Request whose app.state.ts_session_factory returns *rows*."""
    result_mock = MagicMock()
    result_mock.fetchall.return_value = rows

    session_mock = AsyncMock()
    session_mock.execute = AsyncMock(return_value=result_mock)
    session_mock.__aenter__ = AsyncMock(return_value=session_mock)
    session_mock.__aexit__ = AsyncMock(return_value=False)

    factory_mock = MagicMock(return_value=session_mock)

    request = MagicMock()
    request.app.state.ts_session_factory = factory_mock
    return request


# ---------------------------------------------------------------------------
# Range validation
# ---------------------------------------------------------------------------


class TestRangeValidation:
    @pytest.mark.asyncio
    async def test_invalid_range_raises_422(self) -> None:
        request = _make_request([])
        with pytest.raises(HTTPException) as exc_info:
            await metrics_service.get_metrics("london", "3h", request)
        assert exc_info.value.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_range_detail_contains_valid_options(self) -> None:
        request = _make_request([])
        with pytest.raises(HTTPException) as exc_info:
            await metrics_service.get_metrics("london", "invalid", request)
        detail = exc_info.value.detail
        assert "1h" in detail
        assert "6h" in detail
        assert "24h" in detail
        assert "7d" in detail

    @pytest.mark.asyncio
    async def test_empty_range_string_raises_422(self) -> None:
        request = _make_request([])
        with pytest.raises(HTTPException) as exc_info:
            await metrics_service.get_metrics("london", "", request)
        assert exc_info.value.status_code == 422


# ---------------------------------------------------------------------------
# Valid range values
# ---------------------------------------------------------------------------


class TestValidRanges:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("range_str", ["1h", "6h", "24h", "7d"])
    async def test_all_valid_ranges_return_metrics_response(
        self, range_str: str
    ) -> None:
        ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        rows = [_make_row(ts, "temperature", 22.5)]
        request = _make_request(rows)

        result = await metrics_service.get_metrics("paris", range_str, request)

        assert isinstance(result, MetricsResponse)
        assert result.city == "paris"
        assert result.range == range_str

    @pytest.mark.asyncio
    @pytest.mark.parametrize("range_str", ["1h", "6h", "24h", "7d"])
    async def test_valid_ranges_return_correct_bucket_count(
        self, range_str: str
    ) -> None:
        ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        rows = [
            _make_row(ts, "temperature", 20.0),
            _make_row(ts, "humidity", 60.0),
        ]
        request = _make_request(rows)

        result = await metrics_service.get_metrics("berlin", range_str, request)

        assert len(result.metrics) == 2


# ---------------------------------------------------------------------------
# Empty result set (AC-5)
# ---------------------------------------------------------------------------


class TestEmptyResult:
    @pytest.mark.asyncio
    async def test_empty_db_result_returns_empty_metrics_list(self) -> None:
        request = _make_request([])

        result = await metrics_service.get_metrics("cairo", "24h", request)

        assert isinstance(result, MetricsResponse)
        assert result.metrics == []

    @pytest.mark.asyncio
    async def test_empty_result_preserves_city_and_range(self) -> None:
        request = _make_request([])

        result = await metrics_service.get_metrics("tokyo", "7d", request)

        assert result.city == "tokyo"
        assert result.range == "7d"


# ---------------------------------------------------------------------------
# MetricBucket mapping
# ---------------------------------------------------------------------------


class TestMetricBucketMapping:
    @pytest.mark.asyncio
    async def test_rows_mapped_to_metric_buckets(self) -> None:
        ts = datetime(2024, 6, 15, 9, 0, 0, tzinfo=timezone.utc)
        rows = [_make_row(ts, "wind_speed", 3.7)]
        request = _make_request(rows)

        result = await metrics_service.get_metrics("oslo", "6h", request)

        assert len(result.metrics) == 1
        bucket = result.metrics[0]
        assert isinstance(bucket, MetricBucket)
        assert bucket.bucket == ts
        assert bucket.metric_name == "wind_speed"
        assert bucket.avg_value == pytest.approx(3.7)

    @pytest.mark.asyncio
    async def test_city_lowercased_in_query(self) -> None:
        request = _make_request([])

        await metrics_service.get_metrics("LONDON", "1h", request)

        # Verify the session.execute was called with city in lowercase
        factory = request.app.state.ts_session_factory
        session = factory.return_value
        call_args = session.execute.call_args
        params = call_args[0][1]  # second positional arg is the params dict
        assert params["city"] == "london"


# ---------------------------------------------------------------------------
# SQL structure
# ---------------------------------------------------------------------------


class TestSqlQueryStructure:
    @pytest.mark.asyncio
    async def test_time_bucket_appears_in_query(self) -> None:
        """Ensure the raw SQL sent to the DB contains time_bucket (AC-5)."""
        request = _make_request([])

        with patch("backend.services.metrics_service.text") as mock_text:
            mock_text.return_value = MagicMock()
            # Rebuild a minimal session mock that works with the patched text()
            result_mock = MagicMock()
            result_mock.fetchall.return_value = []
            session_mock = AsyncMock()
            session_mock.execute = AsyncMock(return_value=result_mock)
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            request.app.state.ts_session_factory = MagicMock(return_value=session_mock)

            await metrics_service.get_metrics("sydney", "24h", request)

            # The string passed to text() must contain time_bucket
            sql_arg: str = mock_text.call_args[0][0]
            assert "time_bucket" in sql_arg

    @pytest.mark.asyncio
    async def test_query_filters_by_city_and_interval(self) -> None:
        """Ensure the SQL template contains WHERE conditions for city and time."""
        request = _make_request([])

        with patch("backend.services.metrics_service.text") as mock_text:
            mock_text.return_value = MagicMock()
            result_mock = MagicMock()
            result_mock.fetchall.return_value = []
            session_mock = AsyncMock()
            session_mock.execute = AsyncMock(return_value=result_mock)
            session_mock.__aenter__ = AsyncMock(return_value=session_mock)
            session_mock.__aexit__ = AsyncMock(return_value=False)
            request.app.state.ts_session_factory = MagicMock(return_value=session_mock)

            await metrics_service.get_metrics("madrid", "7d", request)

            sql_arg: str = mock_text.call_args[0][0]
            assert ":city" in sql_arg
            assert ":interval_ago" in sql_arg
            assert ":bucket_size" in sql_arg
