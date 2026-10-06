"""Simulated UTC clock used by streaks and other date-sensitive features."""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SystemSetting

TIME_OFFSET_KEY = "time_offset_days"


def _offset_days(db: Session) -> int:
    """Read the simulated day offset from system settings."""
    setting = db.scalar(
        select(SystemSetting).where(SystemSetting.key == TIME_OFFSET_KEY)
    )
    if setting is None:
        return 0
    try:
        return int(setting.value)
    except ValueError:
        return 0


def now_utc(db: Session) -> datetime:
    """Return naive UTC time plus the configured simulated day offset."""
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
        days=_offset_days(db)
    )


def today(db: Session) -> date:
    """Return today's simulated UTC date."""
    return now_utc(db).date()
