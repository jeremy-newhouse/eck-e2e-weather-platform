"""Health and readiness endpoints (AC-9, AC-10)."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

router = APIRouter(tags=["health"])


@router.get("/health", response_model=None)
async def health_check(request: Request) -> dict[str, object]:
    """Returns health status with individual service checks (AC-9)."""
    services: dict[str, str] = {}
    overall = "ok"

    # Check PostgreSQL
    try:
        pg_session_factory = request.app.state.pg_session_factory
        async with pg_session_factory() as session:
            await session.execute(text("SELECT 1"))
        services["postgres"] = "ok"
    except Exception:
        services["postgres"] = "error"
        overall = "degraded"

    # Check TimescaleDB
    try:
        ts_session_factory = request.app.state.ts_session_factory
        async with ts_session_factory() as session:
            await session.execute(text("SELECT 1"))
        services["timescale"] = "ok"
    except Exception:
        services["timescale"] = "error"
        overall = "degraded"

    return {"status": overall, "services": services}


@router.get("/ready", response_model=None)
async def readiness_check(request: Request) -> dict[str, str] | JSONResponse:
    """Returns 200 when all DBs healthy, 503 otherwise (AC-10)."""
    try:
        pg_session_factory = request.app.state.pg_session_factory
        ts_session_factory = request.app.state.ts_session_factory

        async with pg_session_factory() as session:
            await session.execute(text("SELECT 1"))
        async with ts_session_factory() as session:
            await session.execute(text("SELECT 1"))

        return {"status": "ready"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "error": str(e)},
        )
