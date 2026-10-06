from fastapi import APIRouter,Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.clock import now_utc,today
from app.database import get_db
from app.models import SystemSetting
from app.schemas.clock import AdvanceRequest
router=APIRouter(prefix="/dev",tags=["dev"])

def _response(db):
    setting=db.get(SystemSetting,"time_offset_days"); return {"time_offset_days":int(setting.value) if setting else 0,"simulated_now":now_utc(db),"simulated_today":today(db)}

@router.get("/clock",summary="Read the simulated clock")
def get_clock(db:Session=Depends(get_db)): return _response(db)

@router.post("/clock/advance",summary="Advance the simulated clock by days")
def advance_clock(payload:AdvanceRequest,db:Session=Depends(get_db)):
    if payload.days<1: from app.errors import api_error; api_error(422,"INVALID_DAYS","days must be at least 1.")
    setting=db.get(SystemSetting,"time_offset_days")
    if setting is None: setting=SystemSetting(key="time_offset_days",value="0",updated_at=now_utc(db));db.add(setting);db.flush()
    setting.value=str(int(setting.value)+payload.days);setting.updated_at=now_utc(db);db.commit();return _response(db)

@router.post("/clock/reset",summary="Reset the simulated clock")
def reset_clock(db:Session=Depends(get_db)):
    setting=db.get(SystemSetting,"time_offset_days")
    if setting is None: setting=SystemSetting(key="time_offset_days",value="0",updated_at=now_utc(db));db.add(setting)
    setting.value="0";setting.updated_at=now_utc(db);db.commit();return _response(db)
