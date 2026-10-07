"""API models for the frontend compatibility layer.

These models intentionally describe the contract consumed by the supplied
frontend. They do not alter the project's frozen database schema.
"""

from pydantic import BaseModel


class UserMe(BaseModel):
    id: int
    name: str
    xp_total: int
    streak_count: int
    hearts: int
    max_hearts: int
    gems: int
    last_activity_date: str | None
    hearts_refill_in_seconds: int | None
    lessons_completed: int
    xp_per_lesson: int
    xp_per_practice: int
    legendary_xp: int
    leaderboard_unlock_lessons: int
    leaderboard_unlocked: bool


class SkillNode(BaseModel):
    id: int
    title: str
    order_index: int
    status: str
    kind: str
    total_lessons: int
    lessons_completed: int
    progress: float
    is_legendary: bool


class UnitNode(BaseModel):
    id: int
    title: str
    order_index: int
    skills: list[SkillNode]


class CoursePath(BaseModel):
    units: list[UnitNode]
    current_skill_id: int | None


class Exercise(BaseModel):
    id: int
    type: str
    payload: dict


class LessonStart(BaseModel):
    lesson_id: int
    skill_title: str
    is_practice: bool
    hearts: int
    exercises: list[Exercise]


class LessonCompleteBody(BaseModel):
    correct_count: int
    mistake_count: int


class LessonResult(BaseModel):
    xp_earned: int
    xp_total: int
    hearts: int
    hearts_lost: int
    streak_count: int
    accuracy: float
    is_perfect: bool
    skill_completed: bool
    unlocked_skill_title: str | None


class LegendaryStart(BaseModel):
    skill_title: str
    hearts: int
    mistake_allowance: int
    exercises: list[Exercise]


class LegendaryResult(BaseModel):
    xp_earned: int
    xp_total: int
    hearts: int
    hearts_lost: int
    streak_count: int
    accuracy: float
    is_perfect: bool
    legendary_earned: bool
    was_already_legendary: bool
    mistake_allowance: int


class ChestOpenResult(BaseModel):
    claimed: bool
    unlocked_skill_title: str | None


class HeartsState(BaseModel):
    hearts: int
    max_hearts: int


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: int
    name: str
    xp_total: int
    is_current_user: bool


class Leaderboard(BaseModel):
    league: str
    promotion_rank: int
    days_remaining: int
    entries: list[LeaderboardEntry]


class Guidebook(BaseModel):
    unit_number: int
    topic: str
    key_phrases: list[str]


class Explanation(BaseModel):
    explanation: str
