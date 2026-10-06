"""Lesson and attempt routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.lessons import (
    AbandonResponse,
    AnswerRequest,
    AnswerResult,
    CompleteResult,
    StartLessonResponse,
    TreasureResponse,
)
from app.services import lessons

router = APIRouter(tags=["lessons"])


@router.post(
    "/lessons/{lesson_id}/start",
    response_model=StartLessonResponse,
    response_model_exclude_none=False,
    summary="Start a lesson attempt",
)
def start(
    lesson_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Start a lesson attempt."""
    result = lessons.start(db, user, lesson_id)
    db.commit()
    return result


@router.post(
    "/attempts/{attempt_id}/answer",
    response_model=AnswerResult,
    response_model_exclude_none=False,
    summary="Submit an exercise answer",
)
def answer(
    attempt_id: int,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Submit one exercise answer."""
    result = lessons.answer(db, user, attempt_id, payload.model_dump())
    db.commit()
    return result


@router.post(
    "/attempts/{attempt_id}/complete",
    response_model=CompleteResult,
    response_model_exclude_none=False,
    summary="Complete a solved lesson",
)
def complete(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Complete a solved lesson attempt."""
    result = lessons.complete(db, user, attempt_id)
    db.commit()
    return result


@router.post(
    "/attempts/{attempt_id}/abandon",
    response_model=AbandonResponse,
    response_model_exclude_none=False,
    summary="Abandon an active lesson",
)
def abandon(
    attempt_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Abandon an active lesson attempt."""
    result = lessons.abandon(db, user, attempt_id)
    db.commit()
    return result


@router.post(
    "/skills/{skill_id}/claim-treasure",
    response_model=TreasureResponse,
    response_model_exclude_none=False,
    summary="Claim a treasure skill",
)
def claim_treasure(
    skill_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Claim a treasure reward."""
    result = lessons.claim_treasure(db, user, skill_id)
    db.commit()
    return result
