from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=None)
async def health_check() -> JSONResponse:
    # Will check DB connections when DB engines are available (WX-T6).
    # Returns basic health until full DB checks are wired in.
    return JSONResponse(
        content={"status": "ok", "services": {"postgres": "ok", "timescale": "ok"}}
    )


@router.get("/ready", response_model=None)
async def readiness_check() -> JSONResponse:
    return JSONResponse(content={"status": "ready"})
