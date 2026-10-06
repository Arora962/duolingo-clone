"""Development-only simulated-clock routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.clock import TIME_OFFSET_KEY, now_utc, today
from app.database import get_db
from app.errors import api_error
from app.models import SystemSetting
from app.schemas.clock import AdvanceRequest, ClockResponse

router = APIRouter(prefix="/dev", tags=["dev"])


def _response(db: Session) -> dict:
    """Build the simulated clock response."""
    setting = db.get(SystemSetting, "time_offset_days")
    return {
        "time_offset_days": int(setting.value) if setting else 0,
        "simulated_now": now_utc(db),
        "simulated_today": today(db),
    }


@router.get(
    "/clock",
    response_model=ClockResponse,
    response_model_exclude_none=False,
    summary="Read the simulated clock",
)
def get_clock(db: Session = Depends(get_db)) -> dict:
    """Read the current simulated clock."""
    return _response(db)


@router.post(
    "/clock/advance",
    response_model=ClockResponse,
    response_model_exclude_none=False,
    summary="Advance the simulated clock by days",
)
def advance_clock(
    payload: AdvanceRequest,
    db: Session = Depends(get_db),
) -> dict:
    """Advance the simulated clock."""
    if payload.days < 1:
        api_error(422, "INVALID_DAYS", "days must be at least 1.")

    setting = db.get(SystemSetting, "time_offset_days")
    if setting is None:
        setting = SystemSetting(
            key="time_offset_days",
            value="0",
            updated_at=now_utc(db),
        )
        db.add(setting)
        db.flush()
    setting.value = str(int(setting.value) + payload.days)
    setting.updated_at = now_utc(db)
    db.commit()
    return _response(db)


@router.post(
    "/clock/reset",
    response_model=ClockResponse,
    response_model_exclude_none=False,
    summary="Reset the simulated clock",
)
def reset_clock(db: Session = Depends(get_db)) -> dict:
    """Reset the simulated clock to the real UTC day."""
    setting = db.get(SystemSetting, "time_offset_days")
    if setting is None:
        setting = SystemSetting(
            key="time_offset_days",
            value="0",
            updated_at=now_utc(db),
        )
        db.add(setting)
    setting.value = "0"
    setting.updated_at = now_utc(db)
    db.commit()
    return _response(db)
