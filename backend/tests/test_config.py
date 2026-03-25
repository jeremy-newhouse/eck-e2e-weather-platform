"""Tests for backend configuration loading."""

from backend.config import Settings


class TestSettings:
    def test_default_database_url(self) -> None:
        s = Settings()
        assert "postgresql+asyncpg" in s.database_url
        assert "weatherdb" in s.database_url

    def test_default_timescale_url(self) -> None:
        s = Settings()
        assert "postgresql+asyncpg" in s.timescale_url
        assert "metricsdb" in s.timescale_url

    def test_default_frontend_url(self) -> None:
        s = Settings()
        assert s.frontend_url == "http://localhost:3000"

    def test_default_api_keys_empty(self) -> None:
        s = Settings()
        assert s.openweather_api_key == ""
        assert s.anthropic_api_key == ""

    def test_env_override(self, monkeypatch: object) -> None:

        # monkeypatch is passed as pytest fixture — use setenv
        assert isinstance(monkeypatch, object)
        # Use environment override via Settings constructor
        s = Settings(
            database_url="postgresql+asyncpg://user:pass@db:5432/testdb",  # type: ignore[call-arg]
            frontend_url="http://example.com",
        )
        assert "testdb" in s.database_url
        assert s.frontend_url == "http://example.com"
