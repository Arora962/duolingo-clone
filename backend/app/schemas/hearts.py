from typing import Literal

from pydantic import BaseModel


class HeartResponse(BaseModel):
    hearts: int
    max_hearts: int
    next_heart_in_seconds: int | None
    refill_cost_gems: int
    gems: int


class RefillRequest(BaseModel):
    method: Literal["GEMS", "PRACTICE"]
