"""Learning-path route."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas.path import PathResponse
from app.services.path import build_path

router = APIRouter(tags=["path"])


@router.get(
    "/path",
    response_model=PathResponse | None,
    response_model_exclude_none=False,
    summary="Get the derived learning path",
)
def path(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Return the learner's current course path."""
    return build_path(db, user)
