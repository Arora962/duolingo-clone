"""Weekly leaderboard across the learner and the seeded bot users."""
from datetime import datetime, time, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.clock import today
from app.enums import AttemptStatus, SkillType
from app.models import Lesson, LessonAttempt, Skill, User


def get_leaderboard(db: Session, user: User):
    """Rank every user by XP earned in the current simulated Monday-to-Monday week.

    XP is summed in a subquery and LEFT JOINed onto users, so users with 0 XP still appear.
    """
    d = today(db)
    start = datetime.combine(d - timedelta(days=d.weekday()), time.min)
    end = start + timedelta(days=7)

    weekly = (
        select(LessonAttempt.user_id.label("user_id"), func.sum(LessonAttempt.xp_earned).label("xp"))
        .join(Lesson, Lesson.id == LessonAttempt.lesson_id)
        .join(Skill, Skill.id == Lesson.skill_id)
        .where(
            LessonAttempt.status == AttemptStatus.COMPLETED,
            Skill.skill_type != SkillType.TREASURE,
            LessonAttempt.finished_at >= start,
            LessonAttempt.finished_at < end,
        )
        .group_by(LessonAttempt.user_id)
        .subquery()
    )
    weekly_xp = func.coalesce(weekly.c.xp, 0)
    rows = db.execute(
        select(User.id, User.username, User.display_name, User.avatar_url, User.is_seeded_bot,
               weekly_xp.label("weekly_xp"))
        .outerjoin(weekly, weekly.c.user_id == User.id)
        .order_by(weekly_xp.desc(), User.username)
    ).all()

    entries = [
        {"rank": rank, "user_id": r.id, "username": r.username, "display_name": r.display_name,
         "avatar_url": r.avatar_url, "weekly_xp": int(r.weekly_xp or 0),
         "is_current_user": r.id == user.id, "is_bot": bool(r.is_seeded_bot)}
        for rank, r in enumerate(rows, 1)
    ]
    current = next((e["rank"] for e in entries if e["is_current_user"]), None)
    return {
        "period_start": start, "period_end": end,
        "days_remaining": max(0, (end - datetime.combine(d, time.min)).days),
        "current_user_rank": current, "entries": entries,
    }
