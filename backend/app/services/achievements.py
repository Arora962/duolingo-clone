"""Achievement evaluation and progress."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clock import now_utc
from app.enums import AchievementMetric
from app.models import Achievement, UserAchievement
from app.services.stats import (
    current_streak,
    non_treasure_lessons_completed,
    perfect_lessons,
    total_xp,
)


def _metric_value(db: Session, user_id: int, metric: AchievementMetric) -> int:
    """Return the current derived value of an achievement metric."""
    if metric == AchievementMetric.STREAK_DAYS:
        return current_streak(db, user_id)
    if metric == AchievementMetric.TOTAL_XP:
        return total_xp(db, user_id)
    if metric == AchievementMetric.LESSONS_COMPLETED:
        return non_treasure_lessons_completed(db, user_id)
    if metric == AchievementMetric.PERFECT_LESSONS:
        return perfect_lessons(db, user_id)
    return 0


def evaluate(db: Session, user_id: int) -> list[Achievement]:
    """Unlock every not-yet-owned achievement whose threshold is reached."""
    now = now_utc(db)
    new = []
    earned = {
        item.achievement_id
        for item in db.scalars(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        ).all()
    }
    for achievement in db.scalars(select(Achievement).order_by(Achievement.id)).all():
        if achievement.id in earned:
            continue
        if _metric_value(db, user_id, achievement.metric) >= achievement.threshold:
            db.add(
                UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    unlocked_at=now,
                )
            )
            new.append(achievement)
    db.flush()
    return new


def get_achievement_progress(db: Session, user_id: int) -> list[dict]:
    """Return every achievement with current value and unlock state."""
    earned = {
        item.achievement_id: item.unlocked_at
        for item in db.scalars(
            select(UserAchievement).where(UserAchievement.user_id == user_id)
        ).all()
    }
    return [
        {
            "code": achievement.code,
            "name": achievement.name,
            "description": achievement.description,
            "icon": achievement.icon,
            "metric": achievement.metric.value,
            "threshold": achievement.threshold,
            "current_value": _metric_value(db, user_id, achievement.metric),
            "earned": achievement.id in earned,
            "unlocked_at": earned.get(achievement.id),
        }
        for achievement in db.scalars(
            select(Achievement).order_by(Achievement.id)
        ).all()
    ]
