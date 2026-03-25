"""Alembic environment configuration.

Supports two database targets selected via ``-x target=postgres`` or
``-x target=timescale`` on the Alembic command line.  The default target
is ``postgres``.

Usage::

    # PostgreSQL tables
    alembic -c migrations/alembic_postgres.ini -x target=postgres upgrade head

    # TimescaleDB hypertable
    alembic -c migrations/alembic_timescale.ini -x target=timescale upgrade head
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ---------------------------------------------------------------------------
# Load ORM metadata for both engines
# ---------------------------------------------------------------------------
from backend.models.postgres import PGBase
from backend.models.timescale import TSBase

# ---------------------------------------------------------------------------
# Alembic config object — provides access to alembic.ini values
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Resolve target and select the appropriate metadata
# ---------------------------------------------------------------------------
_target: str = config.get_main_option("target", "postgres") or "postgres"

if _target == "timescale":
    target_metadata = TSBase.metadata
else:
    target_metadata = PGBase.metadata


# ---------------------------------------------------------------------------
# Offline migration (generates SQL without a live connection)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL that can be applied manually without a live database
    connection.  The URL is read from the active ini file.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migration (runs against a live database connection)
# ---------------------------------------------------------------------------

def do_run_migrations(connection: Connection) -> None:
    """Execute migrations using an active synchronous connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations inside it."""
    configuration = config.get_section(config.config_ini_section, {})

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using asyncio."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
