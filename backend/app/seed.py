"""Idempotent database seeding: python -m app.seed."""

from datetime import datetime, time, timedelta

from sqlalchemy import select

from app.clock import now_utc
from app.database import Base, SessionLocal, engine
from app.enums import AchievementMetric, AttemptStatus, ExerciseType, HeartEventType, OptionSide, SkillIcon, SkillType
from app.models import (
    Achievement,
    AttemptAnswer,
    Course,
    Exercise,
    ExerciseAcceptedAnswer,
    ExerciseOption,
    HeartEvent,
    Lesson,
    LessonAttempt,
    Skill,
    SystemSetting,
    Unit,
    User,
    UserAchievement,
    UserSettings,
)
from app.seed_data import ACHIEVEMENTS, COURSE, UNITS


def _enum(enum_cls, value):
    return enum_cls[value]


def _get_or_create(session, model, where, values):
    obj = session.scalar(select(model).filter_by(**where))
    if obj is None:
        obj = model(**where, **values)
        session.add(obj)
        session.flush()
    return obj


def _seed_content(db):
    course = _get_or_create(db, Course, {"language_code": COURSE["language_code"]}, {k: v for k, v in COURSE.items() if k != "language_code"})
    lessons_by_skill = []
    for unit_data in UNITS:
        unit = _get_or_create(db, Unit, {"course_id": course.id, "position": unit_data["position"]}, {k: v for k, v in unit_data.items() if k not in {"position", "skills"}})
        for skill_data in unit_data["skills"]:
            skill = _get_or_create(
                db, Skill, {"unit_id": unit.id, "position": skill_data["position"]},
                {"title": skill_data["title"], "skill_type": _enum(SkillType, skill_data["skill_type"]), "icon_type": _enum(SkillIcon, skill_data["icon_type"])},
            )
            for lesson_data in skill_data["lessons"]:
                lesson = _get_or_create(db, Lesson, {"skill_id": skill.id, "position": lesson_data["position"]}, {"xp_reward": lesson_data["xp_reward"]})
                lessons_by_skill.append((skill.position, skill, lesson))
                for position, exercise_data in enumerate(lesson_data["exercises"], start=1):
                    exercise = _get_or_create(
                        db, Exercise, {"lesson_id": lesson.id, "position": position},
                        {
                            "type": _enum(ExerciseType, exercise_data["type"]),
                            "prompt": exercise_data["prompt"],
                            "source_text": exercise_data.get("source_text"),
                            "hint": exercise_data.get("hint"),
                            "audio_url": exercise_data.get("audio_url"),
                        },
                    )
                    if exercise_data["type"] in {"MULTIPLE_CHOICE", "FILL_IN_BLANK"}:
                        for option_position, (text, is_correct) in enumerate(exercise_data["options"], start=1):
                            _get_or_create(db, ExerciseOption, {"exercise_id": exercise.id, "position": option_position}, {"text": text, "is_correct": is_correct})
                    elif exercise_data["type"] == "TRANSLATE_WORD_BANK":
                        for option_position, option in enumerate(exercise_data["options"], start=1):
                            text, _unused, answer_order = option
                            _get_or_create(db, ExerciseOption, {"exercise_id": exercise.id, "position": option_position}, {"text": text, "is_correct": False, "answer_order": answer_order})
                    elif exercise_data["type"] == "MATCH_PAIRS":
                        position = 1
                        for pair_number, (left, right) in enumerate(exercise_data["pairs"], start=1):
                            for text, side in ((left, OptionSide.LEFT), (right, OptionSide.RIGHT)):
                                _get_or_create(db, ExerciseOption, {"exercise_id": exercise.id, "position": position}, {"text": text, "is_correct": False, "pair_key": str(pair_number), "side": side})
                                position += 1
                    for answer in exercise_data.get("answers", []):
                        _get_or_create(db, ExerciseAcceptedAnswer, {"exercise_id": exercise.id, "answer_text": answer}, {"is_primary": answer == exercise_data["answers"][0]})
    return course, lessons_by_skill


def _ensure_user(db, course, username, display_name, gems=0, is_seeded_bot=False):
    user = _get_or_create(
        db, User, {"username": username},
        {"display_name": display_name, "gems": gems, "is_seeded_bot": is_seeded_bot, "current_course_id": course.id},
    )
    if user.current_course_id is None:
        user.current_course_id = course.id
    if user.settings is None:
        db.add(UserSettings(user_id=user.id))
        db.flush()
    return user


def _completed_attempt(db, user, lesson, when, perfect=True):
    existing = db.scalar(select(LessonAttempt).where(LessonAttempt.user_id == user.id, LessonAttempt.lesson_id == lesson.id, LessonAttempt.finished_at == when))
    if existing is not None:
        return existing
    attempt = LessonAttempt(user_id=user.id, lesson_id=lesson.id, status=AttemptStatus.COMPLETED, started_at=when - timedelta(minutes=5), finished_at=when, xp_earned=lesson.xp_reward)
    db.add(attempt)
    db.flush()
    for exercise in lesson.exercises:
        answer_text = "correct" if perfect else "answer"
        db.add(AttemptAnswer(attempt_id=attempt.id, exercise_id=exercise.id, submitted_answer=answer_text, is_correct=perfect, answered_at=when - timedelta(seconds=30)))
    return attempt


def _seed_learner_progress(db, learner, lesson_groups):
    # First skill: both lessons completed. Second skill: only its first lesson completed.
    first_skill_lessons = [lesson for _, skill, lesson in lesson_groups if skill.unit.position == 1 and skill.position == 1]
    second_skill_lessons = [lesson for _, skill, lesson in lesson_groups if skill.unit.position == 1 and skill.position == 2]
    current = now_utc(db)
    today_start = datetime.combine(current.date(), time(hour=12))
    days = [today_start - timedelta(days=2), today_start - timedelta(days=1), today_start]
    _completed_attempt(db, learner, first_skill_lessons[0], days[0], perfect=True)
    _completed_attempt(db, learner, first_skill_lessons[1], days[0] + timedelta(minutes=20), perfect=True)
    _completed_attempt(db, learner, second_skill_lessons[0], days[1], perfect=False)
    # Repeated completed attempts provide enough recorded XP for the seeded achievement data.
    for index in range(7):
        _completed_attempt(db, learner, first_skill_lessons[index % 2], days[2] - timedelta(minutes=index + 1), perfect=True)
    # A same-day completed attempt also keeps the three-day streak ending today.
    _completed_attempt(db, learner, second_skill_lessons[0], days[2], perfect=True)

    lost_time = current - timedelta(minutes=10)
    if db.scalar(select(HeartEvent).where(HeartEvent.user_id == learner.id, HeartEvent.event_type == HeartEventType.LOST)) is None:
        db.add(HeartEvent(user_id=learner.id, event_type=HeartEventType.LOST, delta=-1, attempt_id=None, created_at=lost_time))


def _seed_bots(db, course, lessons):
    now = now_utc(db)
    today_start = datetime.combine(now.date(), time(hour=14))
    for bot_index in range(1, 11):
        bot = _ensure_user(db, course, f"bot{bot_index}", f"Learner Bot {bot_index}", gems=100 + bot_index, is_seeded_bot=True)
        for day_offset in range(0, min(4, 1 + bot_index % 4)):
            lesson = lessons[(bot_index + day_offset) % len(lessons)]
            when = today_start - timedelta(days=day_offset, hours=bot_index)
            _completed_attempt(db, bot, lesson, when, perfect=(bot_index % 2 == 0))


def _seed_achievements(db, learner):
    achievement_map = {}
    for data in ACHIEVEMENTS:
        achievement = _get_or_create(
            db, Achievement, {"code": data["code"]},
            {"name": data["name"], "description": data["description"], "icon": data["icon"], "metric": _enum(AchievementMetric, data["metric"]), "threshold": data["threshold"]},
        )
        achievement_map[achievement.code] = achievement
    from app.services.stats import current_streak, completed_lesson_ids, total_xp
    metrics = {"STREAK_3": current_streak(db, learner.id), "FIRST_LESSON": len(completed_lesson_ids(db, learner.id)), "XP_100": total_xp(db, learner.id), "XP_500": total_xp(db, learner.id)}
    unlock_codes = ["STREAK_3", "FIRST_LESSON", "PERFECT_LESSON"]
    if metrics["XP_100"] >= 100:
        unlock_codes.append("XP_100")
    for code in unlock_codes:
        achievement = achievement_map[code]
        if db.get(UserAchievement, {"user_id": learner.id, "achievement_id": achievement.id}) is None:
            db.add(UserAchievement(user_id=learner.id, achievement_id=achievement.id, unlocked_at=now_utc(db)))


def seed() -> None:
    """Create all missing course, learner, bot, event, and achievement seed rows in one transaction."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as db:
        setting = db.get(SystemSetting, "time_offset_days")
        if setting is None:
            db.add(SystemSetting(key="time_offset_days", value="0", updated_at=now_utc(db)))
        course, lesson_groups = _seed_content(db)
        learner = _ensure_user(db, course, "learner", "Learner", gems=500)
        if learner.settings is not None:
            learner.settings.daily_goal_xp = 20
        _seed_learner_progress(db, learner, lesson_groups)
        lesson_list = [lesson for _, _, lesson in lesson_groups]
        _seed_bots(db, course, lesson_list)
        _seed_achievements(db, learner)


if __name__ == "__main__":
    seed()
