"""Compatibility adapter for the supplied frontend.

The adapter deliberately reuses the existing SQLAlchemy models and services.
It translates the UI contract into the project's frozen schema; it does not
create or migrate tables.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.services.stats import daily_goal
from app.services.achievements import get_achievement_progress
from app.clock import now_utc
from app.constants import MAX_HEARTS
from app.enums import AttemptStatus, ExerciseType, HeartEventType, OptionSide, SkillType
from app.errors import api_error
from app.models import (
    AttemptAnswer,
    Course,
    Exercise,
    ExerciseOption,
    HeartEvent,
    Lesson,
    LessonAttempt,
    Skill,
    SystemSetting,
    Unit,
    User,
)
from app.services import lessons as lesson_service
from app.services.leaderboard import get_leaderboard
from app.services.path import build_path
from app.services.stats import (
    active_days,
    completed_lesson_ids,
    current_hearts_status,
    current_streak,
    total_xp,
)


LEADERBOARD_UNLOCK_LESSONS = 2
LEGENDARY_XP = 40
PRACTICE_XP = 5
LEGENDARY_MISTAKE_ALLOWANCE = 3
LEAGUE = "Bronze"
PROMOTION_RANK = 5


def _setting_key(kind: str, user_id: int, object_id: int) -> str:
    return f"compat:{kind}:{user_id}:{object_id}"


def _has_setting(db: Session, key: str) -> bool:
    return db.get(SystemSetting, key) is not None


def _set_setting(db: Session, key: str) -> None:
    existing = db.get(SystemSetting, key)
    if existing is None:
        db.add(
            SystemSetting(
                key=key,
                value="1",
                updated_at=now_utc(db),
            )
        )
    else:
        existing.value = "1"
        existing.updated_at = now_utc(db)
    db.flush()


def _skill_query(skill_id: int):
    return (
        select(Skill)
        .where(Skill.id == skill_id)
        .options(
            selectinload(Skill.unit),
            selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.options),
            selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.accepted_answers),
        )
    )


def _course_query(course_id: int):
    return (
        select(Course)
        .where(Course.id == course_id)
        .options(
            selectinload(Course.units)
            .selectinload(Unit.skills)
            .selectinload(Skill.lessons)
        )
    )


def _exercise_payload(exercise: Exercise) -> dict:
    """Translate the frozen exercise rows into the frontend's payload shape."""
    if exercise.type == ExerciseType.MULTIPLE_CHOICE:
        options = [option.text for option in exercise.options]
        correct = next(
            (option.text for option in exercise.options if option.is_correct),
            "",
        )
        return {
            "id": exercise.id,
            "type": "multiple_choice",
            "payload": {
                "question": exercise.prompt,
                "options": options,
                "correct": correct,
            },
        }

    if exercise.type == ExerciseType.TRANSLATE_WORD_BANK:
        ordered = sorted(
            (option for option in exercise.options if option.answer_order is not None),
            key=lambda option: option.answer_order,
        )
        return {
            "id": exercise.id,
            "type": "translate",
            "payload": {
                "prompt": exercise.source_text or exercise.prompt,
                "word_bank": [option.text for option in exercise.options],
                "correct_sequence": [option.text for option in ordered],
            },
        }

    if exercise.type == ExerciseType.MATCH_PAIRS:
        left = {
            option.pair_key: option.text
            for option in exercise.options
            if option.side == OptionSide.LEFT
        }
        pairs = [
            {"left": option.text, "right": right}
            for key, option in (
                (option.pair_key, option)
                for option in exercise.options
                if option.side == OptionSide.LEFT
            )
            if (right := next(
                (
                    candidate.text
                    for candidate in exercise.options
                    if candidate.side == OptionSide.RIGHT
                    and candidate.pair_key == key
                ),
                None,
            )) is not None
        ]
        # Keep the comprehension above readable to the caller and deterministic.
        if not pairs and left:
            pairs = [
                {"left": key, "right": value}
                for key, value in left.items()
            ]
        return {
            "id": exercise.id,
            "type": "match_pairs",
            "payload": {"pairs": pairs},
        }

    if exercise.type == ExerciseType.FILL_IN_BLANK:
        if exercise.options:
            correct = next(
                (option.text for option in exercise.options if option.is_correct),
                "",
            )
            options = [option.text for option in exercise.options]
        else:
            correct = next(
                (
                    answer.answer_text
                    for answer in exercise.accepted_answers
                    if answer.is_primary
                ),
                exercise.accepted_answers[0].answer_text
                if exercise.accepted_answers
                else "",
            )
            options = []
        sentence = exercise.source_text or exercise.prompt
        sentence = sentence.replace("____", "___")
        return {
            "id": exercise.id,
            "type": "fill_blank",
            "payload": {
                "sentence": sentence,
                "options": options,
                "correct": correct,
            },
        }

    primary = next(
        (
            answer.answer_text
            for answer in exercise.accepted_answers
            if answer.is_primary
        ),
        exercise.accepted_answers[0].answer_text
        if exercise.accepted_answers
        else "",
    )
    return {
        "id": exercise.id,
        "type": "type_answer",
        "payload": {
            "prompt": exercise.prompt,
            "correct": primary,
        },
    }


def _lesson_exercises(lesson: Lesson) -> list[dict]:
    return [_exercise_payload(exercise) for exercise in lesson.exercises]


def _skill_lessons_completed(
    db: Session, user_id: int, skill: Skill, completed: set[int]
) -> int:
    return sum(lesson.id in completed for lesson in skill.lessons)


def _compat_path(db: Session, user: User) -> dict:
    """Build the UI path while preserving the existing path semantics.

    Treasure/practice rows in the seed intentionally have no lessons. Their
    claim/progress state therefore lives in SystemSetting keys, which is an
    existing table rather than a schema change.
    """
    raw = build_path(db, user)
    if raw is None:
        api_error(409, "COURSE_NOT_SELECTED", "The learner has no current course.")

    output_units = []
    current_skill_id = None

    for unit in raw["units"]:
        output_skills = []
        for skill in unit["skills"]:
            kind = {
                "LESSON": "lesson",
                "TREASURE": "chest",
                "PRACTICE": "practice",
            }.get(skill["skill_type"], "lesson")
            status = skill["state"].lower()  # COMPLETED/AVAILABLE/LOCKED, same as native
            if kind == "chest":
                lessons_total = 0
                lessons_completed = 0
                progress = 1.0 if status == "completed" else 0.0
            else:
                lessons_total = skill["lessons_total"]
                lessons_completed = skill["lessons_completed"]
                progress = lessons_completed / lessons_total if lessons_total else 0.0

            if status == "available" and current_skill_id is None:
                current_skill_id = skill["id"]

            output_skills.append(
                {
                    "id": skill["id"],
                    "title": skill["title"],
                    "order_index": skill["position"] - 1,
                    "status": status,
                    "kind": kind,
                    "total_lessons": lessons_total,
                    "lessons_completed": lessons_completed,
                    "progress": progress,
                    "is_legendary": _has_setting(
                        db, _setting_key("legendary", user.id, skill["id"])
                    ),
                }
            )

        output_units.append(
            {
                "id": unit["id"],
                "title": unit["title"],
                "order_index": unit["position"] - 1,
                "skills": output_skills,
            }
        )

    return {"units": output_units, "current_skill_id": current_skill_id}


def user_me(db: Session, user: User) -> dict:
    hearts = current_hearts_status(db, user.id)
    days = active_days(db, user.id)
    last = max(days).isoformat() if days else None
    completed_count = len(completed_lesson_ids(db, user.id))
    goal, xp_today_value, goal_met = daily_goal(db, user.id)
    return {
        "id": user.id,
        "name": user.display_name,
        "xp_total": total_xp(db, user.id),
        "xp_today": xp_today_value,
        "daily_goal_xp": goal,
        "daily_goal_met": goal_met,
        "streak_count": current_streak(db, user.id),
        "hearts": hearts["hearts"],
        "max_hearts": hearts["max_hearts"],
        "gems": user.gems,
        "last_activity_date": last,
        "hearts_refill_in_seconds": hearts["next_heart_in_seconds"],
        "lessons_completed": completed_count,
        "xp_per_lesson": 10,
        "xp_per_practice": PRACTICE_XP,
        "legendary_xp": LEGENDARY_XP,
        "leaderboard_unlock_lessons": LEADERBOARD_UNLOCK_LESSONS,
        "leaderboard_unlocked": completed_count >= LEADERBOARD_UNLOCK_LESSONS,
        "achievements": get_achievement_progress(db, user.id),
    }


def course_path(db: Session, user: User) -> dict:
    return _compat_path(db, user)


def start_lesson(db: Session, user: User, skill_id: int) -> dict:
    skill = db.scalar(_skill_query(skill_id))
    if skill is None:
        api_error(404, "SKILL_NOT_FOUND", "Skill not found.")
    if skill.skill_type == SkillType.TREASURE:
        api_error(409, "TREASURE_USE_CHEST", "Open the treasure chest instead.")
    if skill.skill_type == SkillType.PRACTICE and not skill.lessons:
        api_error(
            409,
            "PRACTICE_NOT_CONFIGURED",
            "This seeded practice node has no practice lesson.",
        )

    completed = completed_lesson_ids(db, user.id)
    lesson = next(
        (item for item in skill.lessons if item.id not in completed),
        skill.lessons[0] if skill.lessons else None,
    )
    if lesson is None:
        api_error(409, "LESSON_NOT_CONFIGURED", "This skill has no lesson.")

    if skill.skill_type == SkillType.PRACTICE:
        path = _compat_path(db, user)
        state = next(
            (
                item
                for unit in path["units"]
                for item in unit["skills"]
                if item["id"] == skill_id
            ),
            None,
        )
        if state is None or state["status"] == "locked":
            api_error(403, "SKILL_LOCKED", "This practice node is locked.")
        # The native path builder intentionally locks this auxiliary node behind
        # the frozen treasure lesson. The compatibility path represents the
        # treasure claim in system_settings, so create the practice attempt here
        # after checking the same heart invariant.
        status = current_hearts_status(db, user.id)
        if status["hearts"] == 0:
            api_error(
                409,
                "OUT_OF_HEARTS",
                "You have no hearts available.",
                next_heart_in_seconds=status["next_heart_in_seconds"],
            )
        now = now_utc(db)
        for old_attempt in db.scalars(
            select(LessonAttempt).where(
                LessonAttempt.user_id == user.id,
                LessonAttempt.status == AttemptStatus.IN_PROGRESS,
            )
        ).all():
            old_attempt.status = AttemptStatus.ABANDONED
            old_attempt.finished_at = now
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
        attempt_id = attempt.id
        hearts = int(status["hearts"])
    else:
        result = lesson_service.start(db, user, lesson.id)
        attempt_id = result["attempt_id"]
        hearts = int(result["hearts"])

    return {
        "lesson_id": attempt_id,
        "skill_title": skill.title,
        "is_practice": skill.skill_type == SkillType.PRACTICE,
        "hearts": hearts,
        "exercises": _lesson_exercises(lesson),
    }


def _correct_rows(lesson: Lesson, attempt_id: int, now: datetime) -> list[AttemptAnswer]:
    rows: list[AttemptAnswer] = []
    for exercise in lesson.exercises:
        if exercise.type in (ExerciseType.MULTIPLE_CHOICE, ExerciseType.FILL_IN_BLANK):
            option = next((item for item in exercise.options if item.is_correct), None)
            submitted = option.text if option else (
                exercise.accepted_answers[0].answer_text
                if exercise.accepted_answers else ""
            )
            rows.append(
                AttemptAnswer(
                    attempt_id=attempt_id,
                    exercise_id=exercise.id,
                    submitted_answer=submitted,
                    is_correct=True,
                    answered_at=now,
                    exercise=exercise,
                )
            )
        elif exercise.type == ExerciseType.TRANSLATE_WORD_BANK:
            ordered = sorted(
                (item for item in exercise.options if item.answer_order is not None),
                key=lambda item: item.answer_order,
            )
            rows.append(
                AttemptAnswer(
                    attempt_id=attempt_id,
                    exercise_id=exercise.id,
                    submitted_answer=" ".join(item.text for item in ordered),
                    is_correct=True,
                    answered_at=now,
                    exercise=exercise,
                )
            )
        elif exercise.type == ExerciseType.MATCH_PAIRS:
            for left in (
                item for item in exercise.options if item.side == OptionSide.LEFT
            ):
                right = next(
                    (
                        item
                        for item in exercise.options
                        if item.side == OptionSide.RIGHT
                        and item.pair_key == left.pair_key
                    ),
                    None,
                )
                if right is not None:
                    rows.append(
                        AttemptAnswer(
                            attempt_id=attempt_id,
                            exercise_id=exercise.id,
                            submitted_answer=f"{left.id}:{right.id}",
                            is_correct=True,
                            answered_at=now,
                            exercise=exercise,
                        )
                    )
        else:
            submitted = next(
                (
                    answer.answer_text
                    for answer in exercise.accepted_answers
                    if answer.is_primary
                ),
                exercise.accepted_answers[0].answer_text
                if exercise.accepted_answers
                else "",
            )
            rows.append(
                AttemptAnswer(
                    attempt_id=attempt_id,
                    exercise_id=exercise.id,
                    submitted_answer=submitted,
                    is_correct=True,
                    answered_at=now,
                    exercise=exercise,
                )
            )
    return rows


def _wrong_submission(exercise: Exercise) -> str:
    if exercise.type == ExerciseType.MATCH_PAIRS:
        left = next(
            (item for item in exercise.options if item.side == OptionSide.LEFT),
            None,
        )
        right = next(
            (
                item
                for item in exercise.options
                if item.side == OptionSide.RIGHT
                and (left is None or item.pair_key != left.pair_key)
            ),
            None,
        )
        if left is not None and right is not None:
            return f"{left.id}:{right.id}"
    if exercise.type == ExerciseType.TRANSLATE_WORD_BANK:
        ordered = sorted(
            (item for item in exercise.options if item.answer_order is not None),
            key=lambda item: item.answer_order,
        )
        if len(ordered) > 1:
            return " ".join(item.text for item in reversed(ordered))
    if exercise.options:
        wrong = next((item for item in exercise.options if not item.is_correct), None)
        if wrong is not None:
            return wrong.text
    return "__incorrect__"


def _record_adapter_attempt(
    db: Session, user: User, attempt_id: int, correct_count: int, mistake_count: int
) -> LessonAttempt:
    attempt = db.scalar(
        select(LessonAttempt)
        .where(
            LessonAttempt.id == attempt_id,
            LessonAttempt.user_id == user.id,
        )
        .options(
            selectinload(LessonAttempt.lesson)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.options),
            selectinload(LessonAttempt.lesson)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.accepted_answers),
            selectinload(LessonAttempt.answers),
        )
    )

    if attempt is None:
        api_error(
            404,
            "ATTEMPT_NOT_FOUND",
            "Attempt not found.",
        )

    if attempt.status != AttemptStatus.IN_PROGRESS:
        api_error(
            409,
            "ATTEMPT_NOT_ACTIVE",
            "This lesson attempt is no longer active.",
        )

    lesson = attempt.lesson
    total = len(lesson.exercises)

    if (
        correct_count < 0
        or mistake_count < 0
        or correct_count + mistake_count != total
    ):
        api_error(
            422,
            "INVALID_LESSON_RESULT",
            "correct_count + mistake_count must equal the lesson exercise count.",
        )

    if total == 0:
        api_error(
            409,
            "LESSON_NOT_CONFIGURED",
            "This lesson has no exercises.",
        )

    existing_answers = list(attempt.answers)

    # A wrong answer may already have been persisted immediately by the
    # compatibility endpoint used by the frontend.
    existing_wrong = sum(
        not answer.is_correct
        for answer in existing_answers
    )

    if existing_wrong > mistake_count:
        api_error(
            422,
            "INVALID_LESSON_RESULT",
            "The reported mistake count is lower than the mistakes already recorded.",
        )

    answered_ids = {
        answer.exercise_id
        for answer in existing_answers
    }

    existing_correct_ids = {
        answer.exercise_id
        for answer in existing_answers
        if answer.is_correct
    }

    unanswered = [
        exercise
        for exercise in lesson.exercises
        if exercise.id not in answered_ids
    ]

    missing_mistakes = mistake_count - existing_wrong

    if missing_mistakes > len(unanswered):
        api_error(
            422,
            "INVALID_LESSON_RESULT",
            "The reported mistakes cannot be reconciled with this lesson.",
        )

    # Never allow a direct API caller to finish a lesson by spending the last
    # available heart. The browser UI also stops at zero hearts.
    heart_status = current_hearts_status(db, user.id)

    if (
        missing_mistakes > 0
        and missing_mistakes >= int(heart_status["hearts"])
    ):
        api_error(
            409,
            "OUT_OF_HEARTS",
            "You do not have enough hearts to finish this lesson.",
            next_heart_in_seconds=heart_status["next_heart_in_seconds"],
        )

    now = now_utc(db)

    if lesson.skill.skill_type == SkillType.PRACTICE:
        attempt.started_at = now

    # If the frontend already persisted one or more mistakes, only create the
    # missing mistake rows here. This prevents a heart being charged twice.
    mistake_targets = unanswered[:missing_mistakes]

    for exercise in mistake_targets:
        db.add(
            AttemptAnswer(
                attempt_id=attempt.id,
                exercise_id=exercise.id,
                submitted_answer=_wrong_submission(exercise),
                is_correct=False,
                answered_at=now,
                exercise=exercise,
            )
        )

        db.add(
            HeartEvent(
                user_id=user.id,
                event_type=HeartEventType.LOST,
                delta=-1,
                attempt_id=attempt.id,
                created_at=now,
            )
        )

    # The adapter grades the answer counts sent by the browser. The native
    # lesson service still needs a solved/correct row for every exercise, so
    # add those rows where a correct row does not already exist.
    correct_rows = _correct_rows(
        lesson,
        attempt.id,
        now,
    )

    db.add_all(
        row
        for row in correct_rows
        if row.exercise_id not in existing_correct_ids
    )

    db.flush()

    # Force the relationship to be reloaded by lesson_service.complete().
    db.expire(attempt, ["answers"])

    return attempt

def record_mistake(
    db: Session,
    user: User,
    attempt_id: int,
    exercise_id: int,
) -> dict:
    """Persist one incorrect answer immediately so heart loss survives refreshes."""
    attempt = db.scalar(
        select(LessonAttempt)
        .where(
            LessonAttempt.id == attempt_id,
            LessonAttempt.user_id == user.id,
        )
        .options(
            selectinload(LessonAttempt.lesson)
            .selectinload(Lesson.exercises),
            selectinload(LessonAttempt.answers),
        )
    )

    if attempt is None:
        api_error(
            404,
            "ATTEMPT_NOT_FOUND",
            "Attempt not found.",
        )

    if attempt.status != AttemptStatus.IN_PROGRESS:
        api_error(
            409,
            "ATTEMPT_NOT_ACTIVE",
            "This lesson attempt is no longer active.",
        )

    exercise = next(
        (
            item
            for item in attempt.lesson.exercises
            if item.id == exercise_id
        ),
        None,
    )

    if exercise is None:
        api_error(
            422,
            "INVALID_EXERCISE",
            "The exercise does not belong to this lesson.",
        )

    if any(
        answer.exercise_id == exercise_id
        for answer in attempt.answers
    ):
        api_error(
            409,
            "EXERCISE_ALREADY_ANSWERED",
            "This exercise has already been answered.",
        )

    status = current_hearts_status(
        db,
        user.id,
    )

    if status["hearts"] <= 0:
        api_error(
            409,
            "OUT_OF_HEARTS",
            "You have no hearts available.",
            next_heart_in_seconds=status["next_heart_in_seconds"],
        )

    now = now_utc(db)

    db.add(
        AttemptAnswer(
            attempt_id=attempt.id,
            exercise_id=exercise.id,
            submitted_answer=_wrong_submission(exercise),
            is_correct=False,
            answered_at=now,
            exercise=exercise,
        )
    )

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

    updated = current_hearts_status(
        db,
        user.id,
    )

    return {
        "hearts": int(updated["hearts"]),
        "max_hearts": int(updated["max_hearts"]),
    }

def complete_lesson(
    db: Session,
    user: User,
    attempt_id: int,
    body: dict,
) -> dict:
    attempt = _record_adapter_attempt(
        db,
        user,
        attempt_id,
        int(body["correct_count"]),
        int(body["mistake_count"]),
    )
    total = len(attempt.lesson.exercises)
    correct_count = int(body["correct_count"])
    mistake_count = int(body["mistake_count"])

    result = lesson_service.complete(db, user, attempt.id)

    if attempt.lesson.skill.skill_type == SkillType.PRACTICE:
        # The UI advertises the compatibility practice reward separately from
        # the seeded practice lesson's native XP value.
        attempt.xp_earned = PRACTICE_XP
        db.flush()

    # The UI contract reports exercise-level accuracy; the underlying row ledger
    # additionally contains one solution row per match pair. Keep that detail
    # out of the UI's percentage.
    result["accuracy"] = round(correct_count / total * 100, 2)
    result["is_perfect"] = mistake_count == 0
    result["hearts_lost"] = mistake_count
    result["skill_completed"] = bool(result["skill_just_completed"])
    result["unlocked_skill_title"] = (
        result["next_skill_unlocked"]["title"]
        if result["next_skill_unlocked"]
        else None
    )
    return {
        "xp_earned": int(attempt.xp_earned),
        "xp_total": total_xp(db, user.id),
        "hearts": int(result["hearts"]),
        "hearts_lost": int(result["hearts_lost"]),
        "streak_count": int(result["streak_after"]),
        "accuracy": result["accuracy"],
        "is_perfect": result["is_perfect"],
        "skill_completed": result["skill_completed"],
        "unlocked_skill_title": result["unlocked_skill_title"],
    }


def start_legendary(db: Session, user: User, skill_id: int) -> dict:
    skill = db.scalar(_skill_query(skill_id))
    if skill is None:
        api_error(404, "SKILL_NOT_FOUND", "Skill not found.")
    completed = completed_lesson_ids(db, user.id)
    if not skill.lessons or not all(item.id in completed for item in skill.lessons):
        api_error(423, "SKILL_NOT_COMPLETED", "Complete this skill before Legendary.")

    # Use the first lesson as the replay source. The attempt is deliberately
    # against an existing lesson so no new database structure is required.
    lesson = skill.lessons[0]
    result = lesson_service.start(db, user, lesson.id)
    return {
        "attempt_id": result["attempt_id"],
        "skill_title": skill.title,
        "hearts": result["hearts"],
        "mistake_allowance": LEGENDARY_MISTAKE_ALLOWANCE,
        "exercises": _lesson_exercises(lesson),
    }


def complete_legendary(
    db: Session,
    user: User,
    attempt_id: int,
    body: dict,
    skill_id: int,
) -> dict:
    attempt = _record_adapter_attempt(
        db,
        user,
        attempt_id,
        int(body["correct_count"]),
        int(body["mistake_count"]),
    )
    skill = attempt.lesson.skill
    if skill.id != skill_id:
        api_error(409, "LEGENDARY_SKILL_MISMATCH", "This attempt belongs to another skill.")

    mistake_count = int(body["mistake_count"])
    already = _has_setting(db, _setting_key("legendary", user.id, skill.id))

    result = lesson_service.complete(db, user, attempt.id)

    # Existing complete() records the normal lesson reward. Upgrade this replay
    # to the compatibility layer's Legendary reward without adding a column.
    attempt.xp_earned = LEGENDARY_XP
    db.flush()
    _set_setting(db, _setting_key("legendary", user.id, skill.id))

    result["xp_earned"] = LEGENDARY_XP
    result["accuracy"] = round(
        int(body["correct_count"]) / len(attempt.lesson.exercises) * 100, 2
    )
    result["is_perfect"] = mistake_count == 0
    result["hearts_lost"] = mistake_count

    return {
        "xp_earned": LEGENDARY_XP,
        "xp_total": total_xp(db, user.id),
        "hearts": int(current_hearts_status(db, user.id)["hearts"]),
        "hearts_lost": mistake_count,
        "streak_count": current_streak(db, user.id),
        "accuracy": result["accuracy"],
        "is_perfect": result["is_perfect"],
        "legendary_earned": mistake_count <= LEGENDARY_MISTAKE_ALLOWANCE,
        "was_already_legendary": already,
        "mistake_allowance": LEGENDARY_MISTAKE_ALLOWANCE,
    }


def open_chest(db: Session, user: User, skill_id: int) -> dict:
    skill = db.scalar(select(Skill).where(Skill.id == skill_id))
    if skill is None:
        api_error(404, "SKILL_NOT_FOUND", "Skill not found.")
    if skill.skill_type != SkillType.TREASURE:
        api_error(409, "NOT_TREASURE", "This skill is not a treasure.")

    path = _compat_path(db, user)
    state = next(
        (
            skill_data
            for unit in path["units"]
            for skill_data in unit["skills"]
            if skill_data["id"] == skill_id
        ),
        None,
    )
    if state is None or state["status"] == "locked":
        api_error(403, "SKILL_LOCKED", "This treasure is locked.")

    try:
        lesson_service.claim_treasure(db, user, skill_id)
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        if detail.get("code") == "ALREADY_CLAIMED":
            return {"claimed": False, "unlocked_skill_title": None}
        raise

    # Find the next visual lesson skill, if one exists, for the reward toast.
    units = path["units"]
    flat = [item for unit in units for item in unit["skills"]]
    index = next((i for i, item in enumerate(flat) if item["id"] == skill_id), -1)
    unlocked = next(
        (
            item["title"]
            for item in flat[index + 1 :]
            if item["kind"] == "lesson"
        ),
        None,
    )
    return {"claimed": True, "unlocked_skill_title": unlocked}


def refill_hearts(db: Session, user: User) -> dict:
    status = current_hearts_status(db, user.id)
    if status["hearts"] >= MAX_HEARTS:
        # The supplied UI treats refill as a mock action; returning the current
        # state keeps the button harmless instead of surfacing a 409.
        return {"hearts": status["hearts"], "max_hearts": status["max_hearts"]}

    # Use the project's existing GEMS ledger. If there are not enough gems,
    # fall back to the mocked practice refill so the UI can always recover.
    try:
        from app.services.hearts import refill as refill_service

        return refill_service(db, user, "GEMS")
    except Exception as exc:
        # Only recover from the expected domain error; other exceptions should
        # still surface during development.
        if getattr(exc, "status_code", None) != 409:
            raise

    from app.services.hearts import refill as refill_service

    return refill_service(db, user, "PRACTICE")


def leaderboard(db: Session, user: User) -> dict:
    completed_count = len(completed_lesson_ids(db, user.id))
    if completed_count < LEADERBOARD_UNLOCK_LESSONS:
        api_error(
            423,
            "LEADERBOARD_LOCKED",
            f"Complete {LEADERBOARD_UNLOCK_LESSONS - completed_count} more "
            f"{'lesson' if LEADERBOARD_UNLOCK_LESSONS - completed_count == 1 else 'lessons'} "
            "to unlock the leaderboard.",
        )

    raw = get_leaderboard(db, user)
    return {
        "league": LEAGUE,
        "promotion_rank": PROMOTION_RANK,
        "days_remaining": raw["days_remaining"],
        "entries": [
            {
                "rank": entry["rank"],
                "user_id": entry["user_id"],
                "name": entry["display_name"],
                "xp_total": entry["weekly_xp"],
                "is_current_user": entry["is_current_user"],
            }
            for entry in raw["entries"]
        ],
    }


def guidebook(db: Session, user: User, unit_id: int) -> dict:
    unit = db.scalar(
        select(Unit)
        .where(Unit.id == unit_id)
        .options(
            selectinload(Unit.skills)
            .selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.options),
            selectinload(Unit.skills)
            .selectinload(Skill.lessons)
            .selectinload(Lesson.exercises)
            .selectinload(Exercise.accepted_answers),
        )
    )
    if unit is None:
        api_error(404, "UNIT_NOT_FOUND", "Unit not found.")

    phrases: list[str] = []
    seen: set[str] = set()
    for skill in unit.skills:
        for lesson in skill.lessons:
            for exercise in lesson.exercises:
                candidates = []
                if exercise.source_text:
                    candidates.append(exercise.source_text)
                candidates.extend(
                    answer.answer_text
                    for answer in exercise.accepted_answers
                    if answer.is_primary
                )
                candidates.extend(
                    option.text for option in exercise.options if option.is_correct
                )
                for value in candidates:
                    if value and value not in seen:
                        seen.add(value)
                        phrases.append(value)
                    if len(phrases) >= 8:
                        return {
                            "unit_number": unit.position,
                            "topic": unit.title,
                            "key_phrases": phrases,
                        }

    return {
        "unit_number": unit.position,
        "topic": unit.title,
        "key_phrases": phrases,
    }


def explain(question: str, correct_answer: str) -> dict:
    return {
        "explanation": (
            f"Look for the key clue in the question and compare it with "
            f"“{correct_answer}”. The correct answer fits the meaning and "
            "grammar of the sentence."
        )
    }
