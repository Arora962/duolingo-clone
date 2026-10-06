"""Heart refill service."""

from sqlalchemy.orm import Session

from app.clock import now_utc
from app.constants import HEART_REFILL_GEM_COST, MAX_HEARTS
from app.enums import HeartEventType
from app.errors import api_error
from app.models import HeartEvent, User
from app.services.stats import current_hearts_status


def refill(db: Session, user: User, method: str) -> dict[str, int | None]:
    """Refill hearts with gems or one practice heart."""
    status = current_hearts_status(db, user.id)
    if status["hearts"] >= MAX_HEARTS:
        api_error(409, "HEARTS_FULL", "You already have full hearts.")

    if method == "GEMS":
        if user.gems < HEART_REFILL_GEM_COST:
            api_error(
                409,
                "NOT_ENOUGH_GEMS",
                "You do not have enough gems.",
                required_gems=HEART_REFILL_GEM_COST,
            )
        delta = MAX_HEARTS - int(status["hearts"])
        user.gems -= HEART_REFILL_GEM_COST
        event_type = HeartEventType.REFILLED_GEMS
    elif method == "PRACTICE":
        delta = 1
        event_type = HeartEventType.REFILLED_PRACTICE
    else:
        api_error(
            422,
            "INVALID_REFILL_METHOD",
            "method must be GEMS or PRACTICE.",
        )

    db.add(
        HeartEvent(
            user_id=user.id,
            event_type=event_type,
            delta=delta,
            created_at=now_utc(db),
        )
    )
    db.flush()
    return current_hearts_status(db, user.id)
