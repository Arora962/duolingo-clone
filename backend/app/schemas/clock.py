"""Simulated clock request and response models."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class ClockResponse(BaseModel):
    """Current simulated clock state."""

    time_offset_days: int
    simulated_now: datetime
    simulated_today: date


class AdvanceRequest(BaseModel):
    """Number of simulated days to advance."""

    days: int = Field(default=1, ge=1)
