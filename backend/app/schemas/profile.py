"""Response models for learner profiles."""

from datetime import datetime

from pydantic import BaseModel

from app.schemas.me import CourseSummary


class ProfileUser(BaseModel):
    """User identity fields shown on the profile."""

    id: int
    username: str
    display_name: str
    avatar_url: str | None
    joined_at: datetime


class ProfileStats(BaseModel):
    """Derived profile statistics."""

    total_xp: int
    current_streak: int
    longest_streak: int
    lessons_completed: int
    perfect_lessons: int
    xp_today: int
    daily_goal_xp: int
    gems: int


class AchievementProgress(BaseModel):
    """Progress and unlock state for one achievement."""

    code: str
    name: str
    description: str
    icon: str
    metric: str
    threshold: int
    current_value: int
    earned: bool
    unlocked_at: datetime | None


class ProfileResponse(BaseModel):
    """Learner profile with statistics and achievement progress."""

    user: ProfileUser
    stats: ProfileStats
    course: CourseSummary | None
    achievements: list[AchievementProgress]
