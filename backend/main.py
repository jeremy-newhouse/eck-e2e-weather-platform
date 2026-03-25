import os
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
from anthropic import AsyncAnthropic
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.routers import health


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

    # Initialize shared clients
    app.state.owm_client = httpx.AsyncClient(
        base_url="https://api.openweathermap.org",
        timeout=10.0,
    )
    app.state.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    yield

    await app.state.owm_client.aclose()


app = FastAPI(title="Weather Platform API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)

# Remaining routers wired in subsequent tasks (WX-T3, WX-T4, WX-T5):
# from backend.routers import weather, metrics, chat
# app.include_router(weather.router, prefix="/api")
# app.include_router(metrics.router, prefix="/api")
# app.include_router(chat.router, prefix="/api")
