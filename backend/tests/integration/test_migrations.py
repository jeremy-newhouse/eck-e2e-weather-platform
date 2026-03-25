"""Migration correctness tests (AC-11).

These tests verify that the Alembic migrations produce the expected schema
objects in live PostgreSQL and TimescaleDB instances.

The entire module is skipped unless ``INTEGRATION_TESTS=true`` **and** the
databases declared in ``TEST_DATABASE_URL`` / ``TEST_TIMESCALE_URL`` are
reachable.  In CI they run against the docker-compose.test.yml services.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.skipif(
    os.getenv("INTEGRATION_TESTS", "false").lower() != "true",
    reason="Integration tests require INTEGRATION_TESTS=true and live databases",
)

TEST_PG_URL: str = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5435/testdb",
)
TEST_TS_URL: str = os.getenv(
    "TEST_TIMESCALE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5434/testdb",
)


# ---------------------------------------------------------------------------
# PostgreSQL migration tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_postgres_chat_sessions_table_created() -> None:
    """chat_sessions table exists after migration (AC-11)."""
    engine = create_async_engine(TEST_PG_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'chat_sessions'"
            )
        )
        assert result.scalar() == "chat_sessions", "Table chat_sessions not found"
    await engine.dispose()


@pytest.mark.anyio
async def test_postgres_chat_messages_table_created() -> None:
    """chat_messages table exists after migration (AC-11)."""
    engine = create_async_engine(TEST_PG_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'chat_messages'"
            )
        )
        assert result.scalar() == "chat_messages", "Table chat_messages not found"
    await engine.dispose()


@pytest.mark.anyio
async def test_postgres_cities_table_created() -> None:
    """cities table exists after migration (AC-11)."""
    engine = create_async_engine(TEST_PG_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'cities'"
            )
        )
        assert result.scalar() == "cities", "Table cities not found"
    await engine.dispose()


@pytest.mark.anyio
async def test_postgres_all_required_tables_created() -> None:
    """chat_sessions, chat_messages, and cities tables all exist (AC-11)."""
    engine = create_async_engine(TEST_PG_URL)
    async with engine.connect() as conn:
        for table in ("chat_sessions", "chat_messages", "cities"):
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    f"WHERE table_schema = 'public' AND table_name = '{table}'"
                )
            )
            assert result.scalar() == table, f"Table {table} not found in PostgreSQL"
    await engine.dispose()


# ---------------------------------------------------------------------------
# TimescaleDB migration tests
# ---------------------------------------------------------------------------


@pytest.mark.anyio
async def test_timescale_weather_metrics_table_created() -> None:
    """weather_metrics table exists in TimescaleDB after migration (AC-11)."""
    engine = create_async_engine(TEST_TS_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name = 'weather_metrics'"
            )
        )
        assert result.scalar() == "weather_metrics", "Table weather_metrics not found"
    await engine.dispose()


@pytest.mark.anyio
async def test_timescale_hypertable_created() -> None:
    """weather_metrics is a TimescaleDB hypertable (AC-11)."""
    engine = create_async_engine(TEST_TS_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT hypertable_name "
                "FROM timescaledb_information.hypertables "
                "WHERE hypertable_name = 'weather_metrics'"
            )
        )
        row = result.fetchone()
        assert row is not None, "weather_metrics is not a TimescaleDB hypertable"
    await engine.dispose()


@pytest.mark.anyio
async def test_weather_metrics_city_index_exists() -> None:
    """Index on (city, recorded_at DESC) exists on weather_metrics (AC-11)."""
    engine = create_async_engine(TEST_TS_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT indexname FROM pg_indexes "
                "WHERE tablename = 'weather_metrics' AND indexname LIKE '%city%'"
            )
        )
        row = result.fetchone()
        assert row is not None, "city index on weather_metrics not found"
    await engine.dispose()


@pytest.mark.anyio
async def test_weather_metrics_columns_present() -> None:
    """weather_metrics has all required columns (AC-11)."""
    engine = create_async_engine(TEST_TS_URL)
    async with engine.connect() as conn:
        result = await conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_name = 'weather_metrics' AND table_schema = 'public'"
            )
        )
        columns = {row[0] for row in result.fetchall()}
    await engine.dispose()

    expected = {"id", "city", "metric_name", "value", "recorded_at"}
    missing = expected - columns
    assert not missing, f"Missing columns in weather_metrics: {missing}"
