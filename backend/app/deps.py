"""FastAPI dependencies. Authentication is deliberately replaceable."""

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

DEFAULT_USERNAME = "learner"


def get_current_user(db: Session = Depends(get_db)) -> User:
    """Return the seeded learner; replace this dependency when real auth is added."""
    user = db.scalar(select(User).where(User.username == DEFAULT_USERNAME))
    if user is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "Seeded learner not found.",
            },
        )
    return user
