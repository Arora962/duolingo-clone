from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.lessons import AnswerRequest
from app.services import lessons
router=APIRouter(tags=["lessons"])

@router.post("/lessons/{lesson_id}/start",summary="Start a lesson attempt")
def start(lesson_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    result=lessons.start(db,user,lesson_id);db.commit();return result

@router.post("/attempts/{attempt_id}/answer",summary="Submit an exercise answer")
def answer(attempt_id:int,payload:AnswerRequest,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    result=lessons.answer(db,user,attempt_id,payload.model_dump());db.commit();return result

@router.post("/attempts/{attempt_id}/complete",summary="Complete a solved lesson")
def complete(attempt_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    result=lessons.complete(db,user,attempt_id);db.commit();return result

@router.post("/attempts/{attempt_id}/abandon",summary="Abandon an active lesson")
def abandon(attempt_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    result=lessons.abandon(db,user,attempt_id);db.commit();return result

@router.post("/skills/{skill_id}/claim-treasure",summary="Claim a treasure skill")
def claim_treasure(skill_id:int,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    result=lessons.claim_treasure(db,user,skill_id);db.commit();return result
