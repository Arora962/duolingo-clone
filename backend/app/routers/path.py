from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.services.path import build_path
router=APIRouter(tags=["path"])
@router.get("/path",summary="Get the derived learning path")
def path(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    return build_path(db,user)
