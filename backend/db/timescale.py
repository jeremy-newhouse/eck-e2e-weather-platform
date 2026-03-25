"""TimescaleDB async engine and session factory."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_ts_engine(timescale_url: str) -> AsyncEngine:
    """Create an async SQLAlchemy engine for TimescaleDB.

    Args:
        timescale_url: asyncpg-compatible connection URL, e.g.
            ``postgresql+asyncpg://user:pass@host/tsdb``

    Returns:
        Configured :class:`AsyncEngine`.
    """
    return create_async_engine(
        timescale_url,
        echo=False,
        pool_pre_ping=True,
    )


def create_ts_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create a session factory bound to the given TimescaleDB engine.

    Args:
        engine: Async engine returned by :func:`create_ts_engine`.

    Returns:
        Callable session factory producing :class:`AsyncSession` instances.
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def get_ts_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a TimescaleDB session.

    Args:
        session_factory: Factory created via :func:`create_ts_session_factory`.

    Yields:
        An open :class:`AsyncSession` that is closed after the request.
    """
    async with session_factory() as session:
        yield session
