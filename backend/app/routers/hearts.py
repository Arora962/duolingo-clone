"""Heart status and refill routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.constants import HEART_REFILL_GEM_COST
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.hearts import HeartsResponse, RefillRequest, RefillResponse
from app.services.hearts import refill
from app.services.stats import current_hearts_status

router = APIRouter(tags=["hearts"])


@router.get(
    "/hearts",
    response_model=HeartsResponse,
    response_model_exclude_none=False,
    summary="Get current heart status",
)
def hearts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Return current hearts and refill information."""
    status = current_hearts_status(db, user.id)
    return {
        **status,
        "refill_cost_gems": HEART_REFILL_GEM_COST,
        "gems": user.gems,
    }


@router.post(
    "/hearts/refill",
    response_model=RefillResponse,
    response_model_exclude_none=False,
    summary="Refill hearts with gems or practice",
)
def refill_hearts(
    payload: RefillRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Refill hearts using the selected method."""
    status = refill(db, user, payload.method)
    db.commit()
    return {
        **status,
        "refill_cost_gems": HEART_REFILL_GEM_COST,
        "gems": user.gems,
        "method": payload.method,
    }
