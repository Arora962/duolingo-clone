from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.services.leaderboard import get_leaderboard
router=APIRouter(tags=["leaderboard"])
@router.get("/leaderboard",summary="Get the simulated weekly leaderboard")
def leaderboard(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return get_leaderboard(db,user)
