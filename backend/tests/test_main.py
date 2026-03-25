"""Tests for FastAPI app factory in main.py."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class TestAppConstruction:
    """Verifies the app object is properly configured without starting lifespan."""

    def test_app_is_fastapi_instance(self) -> None:
        from backend.main import app

        assert isinstance(app, FastAPI)

    def test_app_title(self) -> None:
        from backend.main import app

        assert app.title == "Weather Platform API"

    def test_app_version(self) -> None:
        from backend.main import app

        assert app.version == "0.1.0"

    def test_health_routes_registered(self) -> None:
        from backend.main import app

        paths = [route.path for route in app.routes]  # type: ignore[attr-defined]
        assert "/health" in paths
        assert "/ready" in paths

    def test_cors_middleware_present(self) -> None:
        from backend.main import app

        middleware_types = [m.cls for m in app.user_middleware]
        assert CORSMiddleware in middleware_types
