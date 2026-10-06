"""Heart endpoint request and response models."""

from typing import Literal

from pydantic import BaseModel


class HeartsResponse(BaseModel):
    """Current heart balance and refill information."""

    hearts: int
    max_hearts: int
    next_heart_in_seconds: int | None
    refill_cost_gems: int
    gems: int


class RefillResponse(BaseModel):
    """Heart balance after a refill."""

    hearts: int
    max_hearts: int
    next_heart_in_seconds: int | None
    refill_cost_gems: int
    gems: int
    method: str


class RefillRequest(BaseModel):
    """Requested heart refill method."""

    method: Literal["GEMS", "PRACTICE"]
