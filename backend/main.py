import os
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from anthropic import AsyncAnthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.postgres import create_pg_engine, create_pg_session_factory
from backend.db.timescale import create_ts_engine, create_ts_session_factory
from backend.routers import chat, health, metrics, weather


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Run Alembic migrations on both engines at startup
    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    subprocess.run(
        [
            "alembic",
            "-c",
            os.path.join(migrations_dir, "alembic_postgres.ini"),
            "upgrade",
            "head",
        ],
        check=True,
        cwd=os.path.dirname(__file__),
    )
    subprocess.run(
        [
            "alembic",
            "-c",
            os.path.join(migrations_dir, "alembic_timescale.ini"),
            "upgrade",
            "head",
        ],
        check=True,
        cwd=os.path.dirname(__file__),
    )

    # Initialize DB engines and session factories
    app.state.pg_engine = create_pg_engine(settings.database_url)
    app.state.pg_session_factory = create_pg_session_factory(app.state.pg_engine)
    app.state.ts_engine = create_ts_engine(settings.timescale_url)
    app.state.ts_session_factory = create_ts_session_factory(app.state.ts_engine)

    # Initialize shared clients
    app.state.owm_client = httpx.AsyncClient(
        base_url="https://api.openweathermap.org",
        timeout=10.0,
    )
    app.state.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    yield

    await app.state.owm_client.aclose()
    await app.state.ts_engine.dispose()
    await app.state.pg_engine.dispose()


app = FastAPI(title="Weather Platform API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(weather.router, prefix="/api")
app.include_router(metrics.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
