"""Application enum values persisted by the frozen schema."""

from enum import Enum


class SkillType(str, Enum):
    """Skill category."""

    LESSON = "LESSON"
    TREASURE = "TREASURE"
    PRACTICE = "PRACTICE"


class SkillIcon(str, Enum):
    """Skill icon identifier."""

    STAR = "STAR"
    BOOK = "BOOK"
    DUMBBELL = "DUMBBELL"
    TROPHY = "TROPHY"
    TREASURE = "TREASURE"
    FAST_FORWARD = "FAST_FORWARD"


class ExerciseType(str, Enum):
    """Exercise interaction type."""

    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TRANSLATE_WORD_BANK = "TRANSLATE_WORD_BANK"
    MATCH_PAIRS = "MATCH_PAIRS"
    FILL_IN_BLANK = "FILL_IN_BLANK"
    TYPE_ANSWER = "TYPE_ANSWER"


class OptionSide(str, Enum):
    """Side of a matching-pair option."""

    LEFT = "LEFT"
    RIGHT = "RIGHT"


class AttemptStatus(str, Enum):
    """Lesson attempt lifecycle state."""

    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED_NO_HEARTS = "FAILED_NO_HEARTS"
    ABANDONED = "ABANDONED"


class HeartEventType(str, Enum):
    """Heart ledger event type."""

    LOST = "LOST"
    REFILLED_PRACTICE = "REFILLED_PRACTICE"
    REFILLED_GEMS = "REFILLED_GEMS"


class AchievementMetric(str, Enum):
    """Achievement progress metric."""

    STREAK_DAYS = "STREAK_DAYS"
    TOTAL_XP = "TOTAL_XP"
    LESSONS_COMPLETED = "LESSONS_COMPLETED"
    PERFECT_LESSONS = "PERFECT_LESSONS"
