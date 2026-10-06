"""Derived XP, streak, lesson, and heart statistics."""

from datetime import date, datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.clock import now_utc, today
from app.constants import DEFAULT_DAILY_GOAL_XP, HEART_REGEN_MINUTES, MAX_HEARTS
from app.enums import AttemptStatus, HeartEventType, SkillType
from app.models import (
    AttemptAnswer,
    HeartEvent,
    Lesson,
    LessonAttempt,
    Skill,
    UserSettings,
)


def total_xp(db: Session, user_id: int) -> int:
    """Return completed non-treasure XP for a learner."""
    value = db.scalar(
        select(func.coalesce(func.sum(LessonAttempt.xp_earned), 0))
        .join(Lesson)
        .join(Skill)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Skill.skill_type != SkillType.TREASURE,
        )
    )
    return int(value or 0)


def xp_on(db: Session, user_id: int, day: date) -> int:
    """Return completed non-treasure XP earned on a date."""
    start = datetime.combine(day, time.min)
    end = start + timedelta(days=1)
    value = db.scalar(
        select(func.coalesce(func.sum(LessonAttempt.xp_earned), 0))
        .join(Lesson)
        .join(Skill)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Skill.skill_type != SkillType.TREASURE,
            LessonAttempt.finished_at >= start,
            LessonAttempt.finished_at < end,
        )
    )
    return int(value or 0)


def xp_today(db: Session, user_id: int) -> int:
    """Return completed XP earned today."""
    return xp_on(db, user_id, today(db))


def xp_this_week(db: Session, user_id: int) -> int:
    """Return completed XP earned during the simulated week."""
    current = today(db)
    monday = current - timedelta(days=current.weekday())
    value = db.scalar(
        select(func.coalesce(func.sum(LessonAttempt.xp_earned), 0))
        .join(Lesson)
        .join(Skill)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Skill.skill_type != SkillType.TREASURE,
            LessonAttempt.finished_at >= datetime.combine(monday, time.min),
            LessonAttempt.finished_at
            < datetime.combine(monday + timedelta(days=7), time.min),
        )
    )
    return int(value or 0)


def active_days(db: Session, user_id: int) -> set[date]:
    """Return dates on which the learner completed a non-treasure lesson."""
    rows = db.execute(
        select(LessonAttempt.finished_at)
        .join(Lesson)
        .join(Skill)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Skill.skill_type != SkillType.TREASURE,
            LessonAttempt.finished_at.is_not(None),
        )
    ).scalars()
    return {value.date() for value in rows if value}


def current_streak(db: Session, user_id: int) -> int:
    """Return the learner's current consecutive-day streak."""
    days = active_days(db, user_id)
    current = today(db)
    if current not in days:
        current -= timedelta(days=1)
    streak = 0
    while current in days:
        streak += 1
        current -= timedelta(days=1)
    return streak


def longest_streak(db: Session, user_id: int) -> int:
    """Return the learner's longest consecutive-day streak."""
    days = sorted(active_days(db, user_id))
    if not days:
        return 0
    best = run = 1
    for previous, current in zip(days, days[1:]):
        run = run + 1 if current == previous + timedelta(days=1) else 1
        best = max(best, run)
    return best


def streak_active_today(db: Session, user_id: int) -> bool:
    """Return whether the learner has completed a lesson today."""
    return today(db) in active_days(db, user_id)


def completed_lesson_ids(db: Session, user_id: int) -> set[int]:
    """Return every lesson with at least one completed attempt."""
    rows = db.execute(
        select(LessonAttempt.lesson_id)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
        )
        .distinct()
    ).scalars()
    return set(rows)


def non_treasure_lessons_completed(db: Session, user_id: int) -> int:
    """Count completed non-treasure attempts, including replays."""
    value = db.scalar(
        select(func.count(LessonAttempt.id))
        .join(Lesson)
        .join(Skill)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Skill.skill_type != SkillType.TREASURE,
        )
    )
    return int(value or 0)


def skill_lessons_completed(db: Session, user_id: int, skill_id: int) -> int:
    """Count distinct completed lessons belonging to a skill."""
    value = db.scalar(
        select(func.count(func.distinct(LessonAttempt.lesson_id)))
        .join(Lesson)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Lesson.skill_id == skill_id,
        )
    )
    return int(value or 0)


def perfect_lessons(db: Session, user_id: int) -> int:
    """Count completed non-treasure attempts with no wrong answer."""
    has_wrong = (
        select(AttemptAnswer.id)
        .where(
            AttemptAnswer.attempt_id == LessonAttempt.id,
            AttemptAnswer.is_correct.is_(False),
        )
        .exists()
    )
    value = db.scalar(
        select(func.count(LessonAttempt.id))
        .join(Lesson)
        .join(Skill)
        .where(
            LessonAttempt.user_id == user_id,
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Skill.skill_type != SkillType.TREASURE,
            ~has_wrong,
        )
    )
    return int(value or 0)


def current_hearts_status(db: Session, user_id: int) -> dict[str, int | None]:
    """Replay heart events and apply lazy regeneration."""
    events = db.scalars(
        select(HeartEvent)
        .where(HeartEvent.user_id == user_id)
        .order_by(HeartEvent.created_at, HeartEvent.id)
    ).all()
    hearts = MAX_HEARTS
    anchor = None
    now = now_utc(db)

    for event in events:
        if hearts < MAX_HEARTS and anchor is not None:
            gained = max(
                0,
                int(
                    (event.created_at - anchor).total_seconds()
                    // (HEART_REGEN_MINUTES * 60)
                ),
            )
            if gained:
                hearts = min(MAX_HEARTS, hearts + gained)
                anchor = anchor + timedelta(minutes=HEART_REGEN_MINUTES * gained)
                if hearts == MAX_HEARTS:
                    anchor = None

        if event.event_type == HeartEventType.LOST and event.delta < 0:
            if hearts == MAX_HEARTS:
                anchor = event.created_at
            hearts = max(0, hearts + event.delta)
            if hearts == MAX_HEARTS:
                anchor = None
        elif event.delta > 0:
            hearts = min(MAX_HEARTS, hearts + event.delta)
            if hearts == MAX_HEARTS:
                anchor = None

    if hearts < MAX_HEARTS and anchor is not None:
        gained = max(
            0,
            int(
                (now - anchor).total_seconds() // (HEART_REGEN_MINUTES * 60)
            ),
        )
        if gained:
            hearts = min(MAX_HEARTS, hearts + gained)
            anchor = anchor + timedelta(minutes=HEART_REGEN_MINUTES * gained)
            if hearts == MAX_HEARTS:
                anchor = None

    next_seconds = None
    if hearts < MAX_HEARTS and anchor is not None:
        next_seconds = max(
            0,
            int(
                (
                    anchor + timedelta(minutes=HEART_REGEN_MINUTES) - now
                ).total_seconds()
            ),
        )

    return {
        "hearts": max(0, min(MAX_HEARTS, hearts)),
        "max_hearts": MAX_HEARTS,
        "next_heart_in_seconds": next_seconds,
    }


def current_hearts(db: Session, user_id: int) -> int:
    """Return the current heart count."""
    return int(current_hearts_status(db, user_id)["hearts"])


def daily_goal(db: Session, user_id: int) -> tuple[int, int, bool]:
    """Return daily goal, today's XP, and whether the goal is met."""
    settings = db.get(UserSettings, user_id)
    goal = settings.daily_goal_xp if settings else DEFAULT_DAILY_GOAL_XP
    xp = xp_today(db, user_id)
    return goal, xp, xp >= goal
