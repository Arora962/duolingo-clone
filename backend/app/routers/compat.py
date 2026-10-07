"""Frontend compatibility routes.

Mounted at /compat so the project's existing /api contract remains untouched.
The frontend keeps its existing /api/... path strings; its base URL points at
http://localhost:8000/compat, producing /compat/api/... requests.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Lesson, LessonAttempt, Skill, User
from app.schemas.compat import (
    ChestOpenResult,
    CoursePath,
    Explanation,
    Guidebook,
    HeartsState,
    Leaderboard,
    LeaderboardEntry,
    LegendaryResult,
    LegendaryStart,
    LessonCompleteBody,
    LessonResult,
    LessonStart,
    UserMe,
)
from app.services import compat


router = APIRouter(tags=["frontend-compat"])


@router.get("/api/user/me", response_model=UserMe)
def user_me(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return compat.user_me(db, user)


@router.get("/api/course/path", response_model=CoursePath)
def course_path(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return compat.course_path(db, user)


@router.post("/api/course/units/{unit_id}/jump", response_model=CoursePath)
def jump_to_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # Jump is intentionally a harmless no-op in the first compatibility cut.
    # The UI can render its existing "Jump here?" affordance without mutating
    # the frozen progression records.
    _ = unit_id
    return compat.course_path(db, user)


@router.post("/api/course/chest/{skill_id}/open", response_model=ChestOpenResult)
def open_chest(
    skill_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = compat.open_chest(db, user, skill_id)
    db.commit()
    return result


@router.get("/api/course/units/{unit_id}/guidebook", response_model=Guidebook)
def guidebook(
    unit_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return compat.guidebook(db, user, unit_id)


@router.get("/api/lesson/{skill_id}/start", response_model=LessonStart)
def start_lesson(
    skill_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = compat.start_lesson(db, user, skill_id)
    db.commit()
    return result


@router.post("/api/lesson/{attempt_id}/complete", response_model=LessonResult)
def complete_lesson(
    attempt_id: int,
    body: LessonCompleteBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = compat.complete_lesson(db, user, attempt_id, body.model_dump())
    db.commit()
    return result


@router.get("/api/lesson/{skill_id}/legendary", response_model=LegendaryStart)
def start_legendary(
    skill_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = compat.start_legendary(db, user, skill_id)
    db.commit()
    return result


@router.post("/api/lesson/{skill_id}/legendary/complete", response_model=LegendaryResult)
def complete_legendary(
    skill_id: int,
    body: LessonCompleteBody,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    attempt = db.scalar(
        select(LessonAttempt)
        .join(Lesson, Lesson.id == LessonAttempt.lesson_id)
        .join(Skill, Skill.id == Lesson.skill_id)
        .where(
            LessonAttempt.user_id == user.id,
            LessonAttempt.status == "IN_PROGRESS",
            Skill.id == skill_id,
        )
        .order_by(LessonAttempt.id.desc())
    )
    if attempt is None:
        from app.errors import api_error

        api_error(404, "LEGENDARY_ATTEMPT_NOT_FOUND", "No active Legendary attempt found.")

    result = compat.complete_legendary(
        db,
        user,
        attempt.id,
        body.model_dump(),
        skill_id,
    )
    db.commit()
    return result


@router.post("/api/hearts/refill", response_model=HeartsState)
def refill_hearts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = compat.refill_hearts(db, user)
    db.commit()
    return result


@router.get("/api/leaderboard", response_model=Leaderboard)
def leaderboard(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return compat.leaderboard(db, user)


@router.post("/api/exercise/explain", response_model=Explanation)
def explain(
    body: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ = db, user
    return compat.explain(
        str(body.get("question", "")),
        str(body.get("correct_answer", "")),
    )
