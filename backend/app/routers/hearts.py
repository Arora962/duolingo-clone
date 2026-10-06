from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.hearts import RefillRequest
from app.services.stats import current_hearts_status
from app.services.hearts import refill,HEART_REFILL_GEM_COST
router=APIRouter(tags=["hearts"])

@router.get("/hearts",summary="Get current heart status")
def hearts(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return {**current_hearts_status(db,user.id),"refill_cost_gems":HEART_REFILL_GEM_COST,"gems":user.gems}

@router.post("/hearts/refill",summary="Refill hearts with gems or practice")
def refill_hearts(payload:RefillRequest,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    hs=refill(db,user,payload.method);db.commit()
    return {**hs,"refill_cost_gems":HEART_REFILL_GEM_COST,"gems":user.gems,"method":payload.method}
