from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class WeatherResponse(BaseModel):
    city: str
    temperature: float
    humidity: float
    wind_speed: float
    description: str
    timestamp: datetime


class MetricBucket(BaseModel):
    bucket: datetime
    metric_name: str
    avg_value: float


class MetricsResponse(BaseModel):
    city: str
    range: str
    metrics: list[MetricBucket]


class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    city: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    role: str
    content: str
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    services: dict[str, str]
