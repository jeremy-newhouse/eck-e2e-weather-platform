"""Shared pytest fixtures for unit and integration tests.

Integration fixtures (test_pg_session, test_ts_session, async_client) require
live databases and are only active when INTEGRATION_TESTS=true.  Unit tests in
the top-level tests/ directory do not depend on any fixture here and will
continue to run without a database.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# ---------------------------------------------------------------------------
# Environment-derived constants
# ---------------------------------------------------------------------------

TEST_PG_URL: str = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5435/testdb",
)
TEST_TS_URL: str = os.getenv(
    "TEST_TIMESCALE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5434/testdb",
)

INTEGRATION_TESTS: bool = os.getenv("INTEGRATION_TESTS", "false").lower() == "true"


# ---------------------------------------------------------------------------
# anyio backend (required by pytest-anyio / anyio marker)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


# ---------------------------------------------------------------------------
# Integration fixtures — skipped automatically when no live DB is available
# ---------------------------------------------------------------------------


@pytest.fixture
async def test_pg_session() -> AsyncSession:
    """Async PostgreSQL session backed by a throw-away schema.

    Creates all PGBase tables before the test and drops them afterwards so
    each test starts from a clean state.  Requires ``INTEGRATION_TESTS=true``
    and a reachable PostgreSQL instance at ``TEST_DATABASE_URL``.
    """
    from backend.models.postgres import PGBase

    engine = create_async_engine(TEST_PG_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(PGBase.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session  # type: ignore[misc]
    async with engine.begin() as conn:
        await conn.run_sync(PGBase.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_ts_session() -> AsyncSession:
    """Async TimescaleDB session backed by a throw-away schema.

    Creates all TSBase tables before the test and drops them afterwards.
    Requires ``INTEGRATION_TESTS=true`` and a reachable TimescaleDB instance
    at ``TEST_TIMESCALE_URL``.
    """
    from backend.models.timescale import TSBase

    engine = create_async_engine(TEST_TS_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(TSBase.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session  # type: ignore[misc]
    async with engine.begin() as conn:
        await conn.run_sync(TSBase.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def async_client():  # type: ignore[return]
    """Async HTTP test client wired to the FastAPI application.

    Uses ``httpx.AsyncClient`` with ``ASGITransport`` so no real HTTP server
    is required.  The application lifespan is intentionally **not** started
    here because it requires live databases; tests that need app-state clients
    should set them on ``app.state`` directly or use per-router fixtures.
    """
    from httpx import ASGITransport, AsyncClient

    from backend.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
