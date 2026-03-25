"""Initial TimescaleDB schema: weather_metrics hypertable.

Revision ID: 001_timescale
Revises:
Create Date: 2026-03-25 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001_timescale"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # weather_metrics base table
    # ------------------------------------------------------------------
    op.create_table(
        "weather_metrics",
        sa.Column("id", sa.Integer, autoincrement=True, nullable=False),
        sa.Column("city", sa.VARCHAR(255), nullable=False),
        sa.Column("metric_name", sa.VARCHAR(32), nullable=False),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_weather_metrics"),
    )

    op.create_check_constraint(
        "ck_weather_metrics_metric_name",
        "weather_metrics",
        "metric_name IN ('temperature', 'humidity', 'wind_speed')",
    )

    # ------------------------------------------------------------------
    # Convert to TimescaleDB hypertable partitioned on recorded_at
    # chunk_time_interval = 1 day (appropriate for weather data volume)
    # if_not_exists = TRUE makes this idempotent for re-runs
    # ------------------------------------------------------------------
    op.execute(
        """
        SELECT create_hypertable(
            'weather_metrics',
            'recorded_at',
            chunk_time_interval => INTERVAL '1 day',
            if_not_exists => TRUE
        )
        """
    )

    # Composite index: primary query pattern is all metrics for a city, latest first
    op.create_index(
        "idx_weather_metrics_city_recorded_at",
        "weather_metrics",
        ["city", sa.text("recorded_at DESC")],
    )


def downgrade() -> None:
    # TimescaleDB hypertables are dropped via DROP TABLE CASCADE
    op.drop_index("idx_weather_metrics_city_recorded_at", table_name="weather_metrics")
    op.drop_table("weather_metrics")
