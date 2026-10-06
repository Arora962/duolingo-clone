"""Lesson attempt lifecycle and public exercise payload construction."""

from datetime import timedelta
import random

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.clock import now_utc
from app.constants import (
    GEMS_TREASURE_REWARD,
    HEART_REFILL_GEM_COST,
    MAX_HEARTS,
    TIMED_PRACTICE_SECONDS,
)
from app.enums import AttemptStatus, ExerciseType, HeartEventType, SkillType
from app.errors import api_error
from app.models import (
    AttemptAnswer,
    Exercise,
    HeartEvent,
    Lesson,
    LessonAttempt,
    Skill,
    User,
)
from app.services.achievements import evaluate
from app.services.answers import check_answer, solved_exercise_ids, speak_text_for
from app.services.path import build_path, skill_state
from app.services.stats import (
    current_hearts_status,
    current_streak,
    completed_lesson_ids,
    total_xp,
    xp_today,
)


def _exercise_public(exercise: Exercise) -> dict:
    """Build the frontend-safe representation of an exercise."""
    payload = {
        "id": exercise.id,
        "position": exercise.position,
        "type": exercise.type.value,
        "prompt": exercise.prompt,
        "source_text": exercise.source_text,
        "hint": exercise.hint,
        "audio_url": exercise.audio_url,
    }
    if exercise.type in (
        ExerciseType.MULTIPLE_CHOICE,
        ExerciseType.FILL_IN_BLANK,
    ):
        if exercise.options:
            payload["options"] = [
                {
                    "id": option.id,
                    "text": option.text,
                    "image_emoji": option.image_emoji,
                }
                for option in exercise.options
            ]
        else:
            payload["requires_typing"] = True
    elif exercise.type == ExerciseType.TRANSLATE_WORD_BANK:
        tiles = [
            {"id": option.id, "text": option.text}
            for option in exercise.options
        ]
        random.SystemRandom().shuffle(tiles)
        payload["tiles"] = tiles
    elif exercise.type == ExerciseType.MATCH_PAIRS:
        left = [
            {"id": option.id, "text": option.text}
            for option in exercise.options
            if option.side is not None and option.side.value == "LEFT"
        ]
        right = [
            {"id": option.id, "text": option.text}
            for option in exercise.options
            if option.side is not None and option.side.value == "RIGHT"
        ]
        random.SystemRandom().shuffle(right)
        payload["left"] = left
        payload["right"] = right
    return payload


def _expiry(attempt: LessonAttempt, lesson: Lesson, now) -> bool:
    """Return whether a timed practice attempt has expired."""
    return (
        lesson.skill.skill_type == SkillType.PRACTICE
        and now >= attempt.started_at + timedelta(seconds=TIMED_PRACTICE_SECONDS)
    )


def _lesson_query(lesson_id: int):
    """Build the eager-loading query used when starting a lesson."""
    return (
        select(Lesson)
        .where(Lesson.id == lesson_id)
        .options(
            selectinload(Lesson.skill),
            selectinload(Lesson.exercises).selectinload(Exercise.options),
            selectinload(Lesson.exercises).selectinload(
                Exercise.accepted_answers
            ),
        )
    )


def _attempt_query(attempt_id: int, user_id: int):
    """Build the eager-loading query used during an attempt."""
    return (
        select(LessonAttempt)
        .where(
            LessonAttempt.id == attempt_id,
            LessonAttempt.user_id == user_id,
        )
        .options(
            selectinload(LessonAttempt.lesson)
            .selectinload(Lesson.skill)
            .selectinload(Skill.lessons),
            selectinload(LessonAttempt.lesson)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.options),
            selectinload(LessonAttempt.lesson)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.accepted_answers),
            selectinload(LessonAttempt.answers)
            .selectinload(AttemptAnswer.exercise)
            .selectinload(Exercise.options),
            selectinload(LessonAttempt.answers)
            .selectinload(AttemptAnswer.exercise)
            .selectinload(Exercise.accepted_answers),
        )
    )


def start(db: Session, user: User, lesson_id: int) -> dict:
    """Start a lesson attempt and return its public exercise payload."""
    lesson = db.scalar(_lesson_query(lesson_id))
    if lesson is None:
        api_error(404, "LESSON_NOT_FOUND", "Lesson not found.")

    path = build_path(db, user)
    state = skill_state(path, lesson.skill_id)
    if lesson.skill.skill_type == SkillType.TREASURE:
        api_error(
            409,
            "TREASURE_USE_CLAIM",
            "Treasure skills must be claimed with claim-treasure.",
        )
    if state is None or state["state"] == "LOCKED":
        api_error(403, "SKILL_LOCKED", "This skill is locked.")

    lesson_state = next(
        item["state"] for item in state["lessons"] if item["id"] == lesson.id
    )
    if lesson_state == "LOCKED":
        api_error(403, "LESSON_LOCKED", "This lesson is locked.")

    hearts_status = current_hearts_status(db, user.id)
    if hearts_status["hearts"] == 0:
        api_error(
            409,
            "OUT_OF_HEARTS",
            "You have no hearts available.",
            next_heart_in_seconds=hearts_status["next_heart_in_seconds"],
            refill_cost_gems=HEART_REFILL_GEM_COST,
        )

    now = now_utc(db)
    for old in db.scalars(
        select(LessonAttempt).where(
            LessonAttempt.user_id == user.id,
            LessonAttempt.status == AttemptStatus.IN_PROGRESS,
        )
    ).all():
        old.status = AttemptStatus.ABANDONED
        old.finished_at = now

    attempt = LessonAttempt(
        user_id=user.id,
        lesson_id=lesson.id,
        status=AttemptStatus.IN_PROGRESS,
        started_at=now,
        finished_at=None,
        xp_earned=0,
    )
    db.add(attempt)
    db.flush()

    mode = (
        "TIMED_PRACTICE"
        if lesson.skill.skill_type == SkillType.PRACTICE
        else "STANDARD"
    )
    return {
        "attempt_id": attempt.id,
        "lesson_id": lesson.id,
        "skill": {
            "id": lesson.skill.id,
            "title": lesson.skill.title,
            "skill_type": lesson.skill.skill_type.value,
        },
        "mode": mode,
        "xp_reward": lesson.xp_reward,
        "hearts": int(hearts_status["hearts"]),
        "max_hearts": MAX_HEARTS,
        "time_limit_seconds": (
            TIMED_PRACTICE_SECONDS if mode != "STANDARD" else None
        ),
        "expires_at": (
            attempt.started_at + timedelta(seconds=TIMED_PRACTICE_SECONDS)
            if mode != "STANDARD"
            else None
        ),
        "total_exercises": len(lesson.exercises),
        "exercises": [_exercise_public(exercise) for exercise in lesson.exercises],
    }


def answer(db: Session, user: User, attempt_id: int, payload: dict) -> dict:
    """Record an answer, apply heart loss, and return answer feedback."""
    attempt = db.scalar(_attempt_query(attempt_id, user.id))
    if attempt is None:
        api_error(404, "ATTEMPT_NOT_FOUND", "Attempt not found.")
    if attempt.status != AttemptStatus.IN_PROGRESS:
        api_error(
            409,
            "ATTEMPT_NOT_ACTIVE",
            "This lesson attempt is no longer active.",
        )

    lesson = attempt.lesson
    now = now_utc(db)
    if _expiry(attempt, lesson, now):
        attempt.status = AttemptStatus.ABANDONED
        attempt.finished_at = now
        db.commit()
        api_error(409, "TIME_EXPIRED", "The timed practice has expired.")

    exercise = next(
        (
            item
            for item in lesson.exercises
            if item.id == payload.get("exercise_id")
        ),
        None,
    )
    if exercise is None:
        api_error(
            404,
            "EXERCISE_NOT_FOUND",
            "Exercise does not belong to this attempt's lesson.",
        )

    correct, submitted, correct_answer = check_answer(exercise, payload)
    answer_record = AttemptAnswer(
        attempt_id=attempt.id,
        exercise_id=exercise.id,
        submitted_answer=submitted,
        is_correct=correct,
        answered_at=now,
        exercise=exercise,
    )
    attempt.answers.append(answer_record)
    db.flush()

    if not correct:
        db.add(
            HeartEvent(
                user_id=user.id,
                event_type=HeartEventType.LOST,
                delta=-1,
                attempt_id=attempt.id,
                created_at=now,
            )
        )
        db.flush()

    hearts_status = current_hearts_status(db, user.id)
    solved = solved_exercise_ids(attempt)
    failed = hearts_status["hearts"] == 0 and not correct
    if failed:
        attempt.status = AttemptStatus.FAILED_NO_HEARTS
        attempt.finished_at = now
        db.flush()

    return {
        "is_correct": correct,
        "correct_answer": correct_answer,
        "speak_text": speak_text_for(exercise, payload, correct_answer),
        "speak_lang": (
            user.current_course.language_code
            if user.current_course is not None
            else None
        ),
        "audio_url": exercise.audio_url,
        "exercise_solved": exercise.id in solved,
        "solved_exercises": len(solved),
        "total_exercises": len(lesson.exercises),
        "progress_percent": (
            round(len(solved) / len(lesson.exercises) * 100)
            if lesson.exercises
            else 100
        ),
        "all_exercises_solved": len(solved) == len(lesson.exercises),
        "hearts": hearts_status["hearts"],
        "next_heart_in_seconds": hearts_status["next_heart_in_seconds"],
        "lesson_failed": failed,
        "failure_reason": "OUT_OF_HEARTS" if failed else None,
    }


def complete(db: Session, user: User, attempt_id: int) -> dict:
    """Complete a solved lesson and return updated learner progress."""
    attempt = db.scalar(_attempt_query(attempt_id, user.id))
    if attempt is None:
        api_error(404, "ATTEMPT_NOT_FOUND", "Attempt not found.")
    if attempt.status != AttemptStatus.IN_PROGRESS:
        api_error(
            409,
            "ATTEMPT_NOT_ACTIVE",
            "This lesson attempt is no longer active.",
        )

    lesson = attempt.lesson
    now = now_utc(db)
    if _expiry(attempt, lesson, now):
        attempt.status = AttemptStatus.ABANDONED
        attempt.finished_at = now
        db.commit()
        api_error(409, "TIME_EXPIRED", "The timed practice has expired.")

    solved = solved_exercise_ids(attempt)
    if len(solved) != len(lesson.exercises):
        api_error(
            409,
            "NOT_ALL_EXERCISES_SOLVED",
            "Every exercise must be solved before completion.",
            solved_exercises=len(solved),
            total_exercises=len(lesson.exercises),
        )

    completed_ids = completed_lesson_ids(db, user.id)
    skill_was_completed = bool(lesson.exercises) and all(
        item.id in completed_ids for item in lesson.skill.lessons
    )
    before_streak = current_streak(db, user.id)
    before_today = xp_today(db, user.id)

    attempt.status = AttemptStatus.COMPLETED
    attempt.finished_at = now
    attempt.xp_earned = lesson.xp_reward
    db.flush()

    after_streak = current_streak(db, user.id)
    after_today = xp_today(db, user.id)
    total = total_xp(db, user.id)
    answers = attempt.answers
    accuracy = (
        round(sum(answer.is_correct for answer in answers) / len(answers) * 100, 2)
        if answers
        else 100.0
    )
    new_achievements = evaluate(db, user.id)

    path = build_path(db, user)
    state = skill_state(path, lesson.skill_id)
    skill_just = (
        not skill_was_completed
        and state is not None
        and state["state"] == "COMPLETED"
    )
    if path is None or state is None:
        api_error(409, "COURSE_NOT_SELECTED", "The learner has no current course.")

    skills = [skill for unit in path["units"] for skill in unit["skills"]]
    index = next(
        (index for index, skill in enumerate(skills) if skill["id"] == lesson.skill_id),
        -1,
    )
    next_unlocked = None
    if (
        skill_just
        and index >= 0
        and index + 1 < len(skills)
        and skills[index + 1]["state"] == "AVAILABLE"
    ):
        next_unlocked = {
            "id": skills[index + 1]["id"],
            "title": skills[index + 1]["title"],
        }

    goal = user.settings.daily_goal_xp if user.settings else 20
    return {
        "xp_earned": attempt.xp_earned,
        "total_xp": total,
        "accuracy_percent": accuracy,
        "time_spent_seconds": int((now - attempt.started_at).total_seconds()),
        "streak_before": before_streak,
        "streak_after": after_streak,
        "streak_extended": after_streak > before_streak,
        "xp_today": after_today,
        "daily_goal_xp": goal,
        "goal_just_met": before_today < goal <= after_today,
        "hearts": current_hearts_status(db, user.id)["hearts"],
        "skill": {
            "id": state["id"],
            "state": state["state"],
            "lessons_completed": state["lessons_completed"],
            "lessons_total": state["lessons_total"],
            "crowns": state["crowns"],
        },
        "skill_just_completed": skill_just,
        "next_skill_unlocked": next_unlocked,
        "newly_unlocked_achievements": [
            {
                "code": achievement.code,
                "name": achievement.name,
                "description": achievement.description,
                "icon": achievement.icon,
            }
            for achievement in new_achievements
        ],
    }


def abandon(db: Session, user: User, attempt_id: int) -> dict[str, str]:
    """Abandon an active lesson attempt."""
    attempt = db.scalar(
        select(LessonAttempt).where(
            LessonAttempt.id == attempt_id,
            LessonAttempt.user_id == user.id,
        )
    )
    if attempt is None:
        api_error(404, "ATTEMPT_NOT_FOUND", "Attempt not found.")
    if attempt.status != AttemptStatus.IN_PROGRESS:
        api_error(
            409,
            "ATTEMPT_NOT_ACTIVE",
            "This lesson attempt is no longer active.",
        )
    attempt.status = AttemptStatus.ABANDONED
    attempt.finished_at = now_utc(db)
    return {"status": "ABANDONED"}


def claim_treasure(db: Session, user: User, skill_id: int) -> dict[str, int]:
    """Claim a treasure skill and award its gem reward."""
    skill = db.scalar(
        select(Skill)
        .where(Skill.id == skill_id)
        .options(
            selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.options),
            selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.accepted_answers),
        )
    )
    if skill is None:
        api_error(404, "SKILL_NOT_FOUND", "Skill not found.")
    if skill.skill_type != SkillType.TREASURE:
        api_error(409, "NOT_TREASURE", "This skill is not a treasure.")

    path = build_path(db, user)
    state = skill_state(path, skill.id)
    if state is None or state["state"] == "LOCKED":
        api_error(403, "SKILL_LOCKED", "This skill is locked.")
    if state["state"] == "COMPLETED":
        api_error(409, "ALREADY_CLAIMED", "This treasure has already been claimed.")
    if not skill.lessons:
        api_error(409, "TREASURE_NOT_CONFIGURED", "This treasure has no reward lesson.")

    lesson = skill.lessons[0]
    now = now_utc(db)
    db.add(
        LessonAttempt(
            user_id=user.id,
            lesson_id=lesson.id,
            status=AttemptStatus.COMPLETED,
            started_at=now,
            finished_at=now,
            xp_earned=0,
        )
    )
    user.gems += GEMS_TREASURE_REWARD
    db.flush()
    return {"gems_awarded": GEMS_TREASURE_REWARD, "gems": user.gems}
