"""Core behavioral tests for the Duolingo clone backend."""

from datetime import timedelta

from sqlalchemy import func, select

import app.database as database
from app.clock import now_utc
from app.constants import HEART_REGEN_MINUTES, MAX_HEARTS
from app.enums import HeartEventType
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
from app.services.stats import current_hearts_status, total_xp
from app.seed import seed


def _learner(client):
    return client.get("/api/me").json()


def _start_available_lesson(client, complete_skill=False):
    path = client.get("/api/path").json()
    for unit in path["units"]:
        for skill in unit["skills"]:
            available = [
                lesson for lesson in skill["lessons"] if lesson["state"] == "AVAILABLE"
            ]
            if not available:
                continue
            if complete_skill and len(available) != 1:
                continue
            lesson = available[0]
            response = client.post(f"/api/lessons/{lesson['id']}/start")
            assert response.status_code == 200
            return response.json()
    raise AssertionError("No available lesson found")


def _answer_all_exercises(client, started):
    for exercise in started["exercises"]:
        if exercise["type"] == "MULTIPLE_CHOICE":
            payload = {
                "exercise_id": exercise["id"],
                "option_id": exercise["options"][0]["id"],
            }
            response = client.post(
                f"/api/attempts/{started['attempt_id']}/answer",
                json=payload,
            )
            assert response.status_code == 200, response.text
        elif exercise["type"] == "FILL_IN_BLANK":
            payload = {
                "exercise_id": exercise["id"],
                "option_id": exercise["options"][0]["id"],
            }
            response = client.post(
                f"/api/attempts/{started['attempt_id']}/answer",
                json=payload,
            )
            assert response.status_code == 200, response.text
        elif exercise["type"] == "TYPE_ANSWER":
            with database.SessionLocal() as db:
                answer = db.scalar(
                    select(ExerciseAcceptedAnswer)
                    .where(ExerciseAcceptedAnswer.exercise_id == exercise["id"])
                    .order_by(ExerciseAcceptedAnswer.id)
                )
            response = client.post(
                f"/api/attempts/{started['attempt_id']}/answer",
                json={"exercise_id": exercise["id"], "text": answer.answer_text},
            )
            assert response.status_code == 200, response.text
        elif exercise["type"] == "TRANSLATE_WORD_BANK":
            with database.SessionLocal() as db:
                options = db.scalars(
                    select(ExerciseOption)
                    .where(ExerciseOption.exercise_id == exercise["id"])
                    .order_by(ExerciseOption.position)
                ).all()
            option_ids = [
                option.id for option in options if option.answer_order is not None
            ]
            response = client.post(
                f"/api/attempts/{started['attempt_id']}/answer",
                json={
                    "exercise_id": exercise["id"],
                    "option_ids": option_ids,
                },
            )
            assert response.status_code == 200, response.text
        else:
            with database.SessionLocal() as db:
                options = db.scalars(
                    select(ExerciseOption)
                    .where(ExerciseOption.exercise_id == exercise["id"])
                    .order_by(ExerciseOption.position)
                ).all()
            left_options = [
                option
                for option in options
                if option.side is not None and option.side.value == "LEFT"
            ]
            right_by_pair = {
                option.pair_key: option
                for option in options
                if option.side is not None and option.side.value == "RIGHT"
            }
            for left_option in left_options:
                right_option = right_by_pair[left_option.pair_key]
                response = client.post(
                    f"/api/attempts/{started['attempt_id']}/answer",
                    json={
                        "exercise_id": exercise["id"],
                        "left_option_id": left_option.id,
                        "right_option_id": right_option.id,
                    },
                )
                assert response.status_code == 200, response.text


def test_simulated_clock_streak(client):
    seeded = _learner(client)
    assert seeded["current_streak"] == 3

    advanced = client.post("/api/dev/clock/advance", json={"days": 1})
    assert advanced.status_code == 200
    assert _learner(client)["current_streak"] == 3

    started = _start_available_lesson(client)
    _answer_all_exercises(client, started)
    completed = client.post(
        f"/api/attempts/{started['attempt_id']}/complete"
    )
    assert completed.status_code == 200
    assert completed.json()["streak_after"] == 4


def test_heart_regeneration(client):
    with database.SessionLocal() as db:
        learner = db.scalar(select(User).where(User.username == "learner"))
        assert learner is not None
        assert current_hearts_status(db, learner.id)["hearts"] == 4
        event = db.scalar(
            select(HeartEvent)
            .where(
                HeartEvent.user_id == learner.id,
                HeartEvent.event_type == HeartEventType.LOST,
            )
            .order_by(HeartEvent.id.desc())
        )
        assert event is not None
        event.created_at = now_utc(db) - timedelta(minutes=HEART_REGEN_MINUTES)
        db.commit()
        status = current_hearts_status(db, learner.id)
        assert status["hearts"] == MAX_HEARTS
        assert status["next_heart_in_seconds"] is None


def test_wrong_answer_costs_heart_and_records_event(client):
    started = _start_available_lesson(client)
    exercise = started["exercises"][0]
    with database.SessionLocal() as db:
        options = db.scalars(
            select(ExerciseOption)
            .where(ExerciseOption.exercise_id == exercise["id"])
            .order_by(ExerciseOption.position)
        ).all()
    wrong = next(option for option in options if not option.is_correct)
    response = client.post(
        f"/api/attempts/{started['attempt_id']}/answer",
        json={"exercise_id": exercise["id"], "option_id": wrong.id},
    )
    assert response.status_code == 200
    assert response.json()["is_correct"] is False
    assert response.json()["hearts"] == 3

    with database.SessionLocal() as db:
        learner = db.scalar(select(User).where(User.username == "learner"))
        event = db.scalar(
            select(HeartEvent)
            .where(
                HeartEvent.user_id == learner.id,
                HeartEvent.event_type == HeartEventType.LOST,
                HeartEvent.delta == -1,
            )
            .order_by(HeartEvent.id.desc())
        )
        assert event is not None


def test_complete_awards_xp_and_unlocks_next_skill(client):
    before = _learner(client)
    started = _start_available_lesson(client, complete_skill=True)
    _answer_all_exercises(client, started)
    completed = client.post(
        f"/api/attempts/{started['attempt_id']}/complete"
    )
    assert completed.status_code == 200
    result = completed.json()
    assert result["xp_earned"] == 10
    assert result["total_xp"] == before["total_xp"] + 10
    assert result["next_skill_unlocked"] is not None

    path = client.get("/api/path").json()
    next_skill = path["units"][0]["skills"][2]
    assert next_skill["state"] == "AVAILABLE"


def test_seed_idempotency(client):
    models = [
        Course,
        Unit,
        Skill,
        Lesson,
        Exercise,
        ExerciseOption,
        ExerciseAcceptedAnswer,
        User,
        UserSettings,
        LessonAttempt,
        AttemptAnswer,
        HeartEvent,
        Achievement,
        UserAchievement,
        SystemSetting,
    ]
    with database.SessionLocal() as db:
        before = {
            model.__tablename__: db.scalar(select(func.count()).select_from(model))
            for model in models
        }

    seed()

    with database.SessionLocal() as db:
        after = {
            model.__tablename__: db.scalar(select(func.count()).select_from(model))
            for model in models
        }
        learner = db.scalar(select(User).where(User.username == "learner"))
        assert before == after
        assert learner is not None
        assert total_xp(db, learner.id) == 110


def test_me_handles_null_current_course(client):
    with database.SessionLocal() as db:
        learner = db.scalar(select(User).where(User.username == "learner"))
        assert learner is not None
        learner.current_course_id = None
        db.commit()

    response = client.get("/api/me")
    assert response.status_code == 200
    assert response.json()["current_course"] is None


def test_dev_routes_disabled(dev_disabled_client):
    assert dev_disabled_client.get("/api/dev/clock").status_code == 404
    assert (
        dev_disabled_client.post("/api/dev/clock/advance", json={"days": 1}).status_code
        == 404
    )
    assert dev_disabled_client.post("/api/dev/clock/reset").status_code == 404
