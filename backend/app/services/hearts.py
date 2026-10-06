"""Heart refill service."""
from app.clock import now_utc
from app.enums import HeartEventType
from app.models import HeartEvent
from app.services.stats import MAX_HEARTS, current_hearts_status
from app.errors import api_error
MAX_HEARTS=5
HEART_REFILL_GEM_COST=100

def refill(db,user,method):
    status=current_hearts_status(db,user.id)
    if status["hearts"]>=MAX_HEARTS: api_error(409,"HEARTS_FULL","You already have full hearts.")
    if method=="GEMS":
        if user.gems<HEART_REFILL_GEM_COST: api_error(409,"NOT_ENOUGH_GEMS","You do not have enough gems.",required_gems=HEART_REFILL_GEM_COST)
        delta=MAX_HEARTS-status["hearts"]; user.gems-=HEART_REFILL_GEM_COST
        event_type=HeartEventType.REFILLED_GEMS
    elif method=="PRACTICE":
        delta=1; event_type=HeartEventType.REFILLED_PRACTICE
    else: api_error(422,"INVALID_REFILL_METHOD","method must be GEMS or PRACTICE.")
    db.add(HeartEvent(user_id=user.id,event_type=event_type,delta=delta,created_at=now_utc(db)))
    db.flush()
    return current_hearts_status(db,user.id)
