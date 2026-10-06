"""Import and re-export every model so SQLAlchemy metadata is complete."""

from app.models.content import (
    Course,
    Exercise,
    ExerciseAcceptedAnswer,
    ExerciseOption,
    Lesson,
    Skill,
    Unit,
)
from app.models.gamification import (
    Achievement,
    AttemptAnswer,
    HeartEvent,
    LessonAttempt,
    SystemSetting,
    UserAchievement,
)
from app.models.learner import User, UserSettings

__all__ = [
    "Achievement",
    "AttemptAnswer",
    "Course",
    "Exercise",
    "ExerciseAcceptedAnswer",
    "ExerciseOption",
    "HeartEvent",
    "Lesson",
    "LessonAttempt",
    "Skill",
    "SystemSetting",
    "Unit",
    "User",
    "UserAchievement",
    "UserSettings",
]
