"""Derived learning-path and lesson-lock state."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Course, Exercise, Lesson, Skill, Unit, User
from app.services.stats import completed_lesson_ids


def build_path(db: Session, user: User) -> dict | None:
    """Build the learner path with the full content hierarchy eagerly loaded."""
    if user.current_course_id is None:
        return None

    course = db.scalar(
        select(Course)
        .where(Course.id == user.current_course_id)
        .options(
            selectinload(Course.units)
            .selectinload(Unit.skills)
            .selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.options),
            selectinload(Course.units)
            .selectinload(Unit.skills)
            .selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.accepted_answers),
        )
    )
    if course is None:
        return None

    done = completed_lesson_ids(db, user.id)
    skills = [skill for unit in course.units for skill in unit.skills]
    skill_done = {
        skill.id: bool(skill.lessons)
        and all(lesson.id in done for lesson in skill.lessons)
        for skill in skills
    }
    current_id = next(
        (skill.id for skill in skills if not skill_done[skill.id]),
        None,
    )

    result_units = []
    previous_completed = True
    for unit in course.units:
        unit_skills = unit.skills
        skill_output = []
        for skill in unit_skills:
            state = (
                "COMPLETED"
                if skill_done[skill.id]
                else "AVAILABLE" if previous_completed else "LOCKED"
            )
            lesson_output = []
            prior = True
            for lesson in skill.lessons:
                lesson_state = (
                    "COMPLETED"
                    if lesson.id in done
                    else "AVAILABLE" if prior and state != "LOCKED" else "LOCKED"
                )
                lesson_output.append(
                    {
                        "id": lesson.id,
                        "position": lesson.position,
                        "xp_reward": lesson.xp_reward,
                        "state": lesson_state,
                    }
                )
                prior = prior and lesson.id in done

            completed = sum(lesson.id in done for lesson in skill.lessons)
            skill_output.append(
                {
                    "id": skill.id,
                    "position": skill.position,
                    "title": skill.title,
                    "skill_type": skill.skill_type.value,
                    "icon_type": skill.icon_type.value,
                    "state": state,
                    "is_current": skill.id == current_id,
                    "lessons_total": len(skill.lessons),
                    "lessons_completed": completed,
                    "progress_ratio": (
                        completed / len(skill.lessons) if skill.lessons else 0.0
                    ),
                    "crowns": completed,
                    "crowns_max": len(skill.lessons),
                    "next_lesson_id": next(
                        (
                            lesson.id
                            for lesson in skill.lessons
                            if lesson.id not in done
                        ),
                        None,
                    ),
                    "lessons": lesson_output,
                }
            )
            previous_completed = previous_completed and skill_done[skill.id]

        result_units.append(
            {
                "id": unit.id,
                "position": unit.position,
                "title": unit.title,
                "description": unit.description,
                "color_bg": unit.color_bg,
                "color_border": unit.color_border,
                "skills_completed": sum(skill_done[skill.id] for skill in unit_skills),
                "skills_total": len(unit_skills),
                "skills": skill_output,
            }
        )

    return {
        "course": {
            "id": course.id,
            "language_code": course.language_code,
            "name": course.name,
            "flag_emoji": course.flag_emoji,
        },
        "units": result_units,
    }


def skill_state(path: dict | None, skill_id: int) -> dict | None:
    """Find a skill state inside an already-built path."""
    if path is None:
        return None
    for unit in path["units"]:
        for skill in unit["skills"]:
            if skill["id"] == skill_id:
                return skill
    return None
