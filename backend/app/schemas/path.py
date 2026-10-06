"""Response models for the derived learning path."""

from pydantic import BaseModel

from app.schemas.me import CourseSummary


class LessonPath(BaseModel):
    """Lesson progress within a skill."""

    id: int
    position: int
    xp_reward: int
    state: str


class SkillOut(BaseModel):
    """Skill state and lesson progress."""

    id: int
    position: int
    title: str
    skill_type: str
    icon_type: str
    state: str
    is_current: bool
    lessons_total: int
    lessons_completed: int
    progress_ratio: float
    crowns: int
    crowns_max: int
    next_lesson_id: int | None
    lessons: list[LessonPath]


class UnitOut(BaseModel):
    """Unit state and contained skills."""

    id: int
    position: int
    title: str
    description: str
    color_bg: str
    color_border: str
    skills_completed: int
    skills_total: int
    skills: list[SkillOut]


class PathResponse(BaseModel):
    """Complete learner path."""

    course: CourseSummary
    units: list[UnitOut]
