"""Learner identity, profile, and settings routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.errors import api_error
from app.models import User, UserSettings
from app.schemas.me import MeResponse
from app.schemas.profile import ProfileResponse
from app.schemas.settings import SettingsPatch, SettingsResponse
from app.services.achievements import get_achievement_progress
from app.services.stats import (
    current_hearts_status,
    current_streak,
    daily_goal,
    longest_streak,
    non_treasure_lessons_completed,
    perfect_lessons,
    streak_active_today,
    total_xp,
    xp_today,
)

router = APIRouter(tags=["me"])


@router.get(
    "/me",
    response_model=MeResponse,
    response_model_exclude_none=False,
    summary="Get the current learner",
)
def me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Return the current learner summary."""
    heart_status = current_hearts_status(db, user.id)
    goal, xp, met = daily_goal(db, user.id)
    total = total_xp(db, user.id)
    streak = current_streak(db, user.id)
    course = user.current_course
    current_course = (
        {
            "id": course.id,
            "language_code": course.language_code,
            "name": course.name,
            "flag_emoji": course.flag_emoji,
        }
        if course is not None
        else None
    )
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "gems": user.gems,
        "total_xp": total,
        "current_streak": streak,
        "streak_active_today": streak_active_today(db, user.id),
        "hearts": heart_status["hearts"],
        "max_hearts": heart_status["max_hearts"],
        "next_heart_in_seconds": heart_status["next_heart_in_seconds"],
        "daily_goal_xp": goal,
        "xp_today": xp,
        "daily_goal_met": met,
        "current_course": current_course,
        "xp": total,
        "streak": streak,
    }


@router.get(
    "/profile",
    response_model=ProfileResponse,
    response_model_exclude_none=False,
    summary="Get learner profile and achievements",
)
def profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Return profile statistics and achievement progress."""
    total = total_xp(db, user.id)
    course = user.current_course
    course_data = (
        {
            "id": course.id,
            "language_code": course.language_code,
            "name": course.name,
            "flag_emoji": course.flag_emoji,
        }
        if course is not None
        else None
    )
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "avatar_url": user.avatar_url,
            "joined_at": user.created_at,
        },
        "stats": {
            "total_xp": total,
            "current_streak": current_streak(db, user.id),
            "longest_streak": longest_streak(db, user.id),
            "lessons_completed": non_treasure_lessons_completed(db, user.id),
            "perfect_lessons": perfect_lessons(db, user.id),
            "xp_today": xp_today(db, user.id),
            "daily_goal_xp": user.settings.daily_goal_xp if user.settings else 20,
            "gems": user.gems,
        },
        "course": course_data,
        "achievements": get_achievement_progress(db, user.id),
    }


@router.get(
    "/settings",
    response_model=SettingsResponse,
    response_model_exclude_none=False,
    summary="Get learner settings",
)
def get_settings(user: User = Depends(get_current_user)) -> UserSettings:
    """Return learner settings."""
    return user.settings


@router.patch(
    "/settings",
    response_model=SettingsResponse,
    response_model_exclude_none=False,
    summary="Update learner settings",
)
def patch_settings(
    payload: SettingsPatch,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update learner settings."""
    settings = user.settings
    if settings is None:
        api_error(404, "SETTINGS_NOT_FOUND", "Learner settings not found.")

    if payload.daily_goal_xp is not None:
        settings.daily_goal_xp = payload.daily_goal_xp
    for key in (
        "sound_effects_enabled",
        "dark_mode_enabled",
        "reminders_enabled",
    ):
        value = getattr(payload, key)
        if value is not None:
            setattr(settings, key, value)
    db.commit()
    return settings
