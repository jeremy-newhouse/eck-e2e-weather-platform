"""TimescaleDB ORM models: WeatherMetric hypertable."""

import sqlalchemy as sa
from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import DeclarativeBase


class TSBase(DeclarativeBase):
    """Declarative base for all TimescaleDB models."""


class WeatherMetric(TSBase):
    """Raw weather metric reading. Partitioned as a TimescaleDB hypertable on recorded_at."""

    __tablename__ = "weather_metrics"
    __table_args__ = (
        CheckConstraint(
            "metric_name IN ('temperature', 'humidity', 'wind_speed')",
            name="ck_weather_metrics_metric_name",
        ),
        # Index on (city, recorded_at DESC) for primary query pattern
        Index(
            "idx_weather_metrics_city_recorded_at",
            "city",
            sa.text("recorded_at DESC"),
        ),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String(255), nullable=False)
    metric_name = Column(String(32), nullable=False)  # "temperature" | "humidity" | "wind_speed"
    value = Column(Float, nullable=False)
    recorded_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )  # hypertable partition key

    def __repr__(self) -> str:
        return (
            f"<WeatherMetric(id={self.id}, city={self.city}, "
            f"metric_name={self.metric_name}, recorded_at={self.recorded_at})>"
        )
