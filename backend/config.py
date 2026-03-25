from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/weatherdb"
    timescale_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/metricsdb"
    openweather_api_key: str = ""
    anthropic_api_key: str = ""
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
