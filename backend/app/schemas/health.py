"""Health endpoint response model."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Application health status."""

    status: str
