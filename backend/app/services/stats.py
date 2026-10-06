"""Small query services for values intentionally derived from recorded events."""

from collections import defaultdict
from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.clock import now_utc, today
from app.enums import AttemptStatus, HeartEventType
from app.models import HeartEvent, LessonAttempt

MAX_HEARTS = 5
HEART_REGEN_MINUTES = 30


def total_xp(db: Session, user_id: int) -> int:
    """Return XP earned by completed lesson attempts."""
    value = db.scalar(
        select(func.coalesce(func.sum(LessonAttempt.xp_earned), 0)).where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
        )
    )
    return int(value or 0)


def xp_on(db: Session, user_id: int, day: date) -> int:
    """Return completed-attempt XP grouped by the UTC date of finished_at."""
    start = datetime.combine(day, time.min)
    end = start + timedelta(days=1)
    value = db.scalar(
        select(func.coalesce(func.sum(LessonAttempt.xp_earned), 0)).where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            LessonAttempt.finished_at >= start,
            LessonAttempt.finished_at < end,
        )
    )
    return int(value or 0)


def xp_this_week(db: Session, user_id: int) -> int:
    """Return completed-attempt XP from the simulated Monday-through-today week."""
    current = today(db)
    monday = current - timedelta(days=current.weekday())
    return sum(xp_on(db, user_id, monday + timedelta(days=i)) for i in range((current - monday).days + 1))


def current_streak(db: Session, user_id: int) -> int:
    """Count consecutive completed-lesson days ending today or, if absent, yesterday."""
    rows = db.scalars(
        select(LessonAttempt.finished_at)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            LessonAttempt.finished_at.is_not(None),
        )
    ).all()
    completed_days = {value.date() for value in rows if value is not None}
    current = today(db)
    if current not in completed_days:
        current -= timedelta(days=1)
    streak = 0
    while current in completed_days:
        streak += 1
        current -= timedelta(days=1)
    return streak


def current_hearts(db: Session, user_id: int) -> int:
    """Replay the heart ledger and apply one lazy regeneration per elapsed 30 minutes, capped at five."""
    events = db.scalars(
        select(HeartEvent)
        .where(HeartEvent.user_id == user_id)
        .order_by(HeartEvent.created_at, HeartEvent.id)
    ).all()
    if not events:
        return MAX_HEARTS

    hearts = MAX_HEARTS
    cursor = events[0].created_at
    for event in events:
        elapsed = event.created_at - cursor
        hearts = min(MAX_HEARTS, hearts + max(0, int(elapsed.total_seconds() // 60) // HEART_REGEN_MINUTES))
        hearts = max(0, min(MAX_HEARTS, hearts + event.delta))
        cursor = event.created_at

    elapsed = now_utc(db) - cursor
    hearts = min(MAX_HEARTS, hearts + max(0, int(elapsed.total_seconds() // 60) // HEART_REGEN_MINUTES))
    return max(0, min(MAX_HEARTS, hearts))


def completed_lesson_ids(db: Session, user_id: int) -> set[int]:
    """Return lesson IDs for which the learner has at least one completed attempt."""
    rows = db.scalars(
        select(LessonAttempt.lesson_id).where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
        ).distinct()
    )
    return set(rows)


def skill_lessons_completed(db: Session, user_id: int, skill_id: int) -> int:
    """Return how many lessons in a skill have at least one completed attempt."""
    from app.models import Lesson

    value = db.scalar(
        select(func.count(func.distinct(LessonAttempt.lesson_id)))
        .join(Lesson, Lesson.id == LessonAttempt.lesson_id)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Lesson.skill_id == skill_id,
        )
    )
    return int(value or 0)
