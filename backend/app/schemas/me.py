"""Response models for learner identity and summary data."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CourseSummary(BaseModel):
    """Minimal course summary returned by learner endpoints."""

    id: int
    language_code: str
    name: str
    flag_emoji: str


class MeResponse(BaseModel):
    """Current learner summary."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    avatar_url: str | None
    gems: int
    total_xp: int
    current_streak: int
    streak_active_today: bool
    hearts: int
    max_hearts: int
    next_heart_in_seconds: int | None
    daily_goal_xp: int
    xp_today: int
    daily_goal_met: bool
    current_course: CourseSummary | None

