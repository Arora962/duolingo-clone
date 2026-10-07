"""Regression tests for the frontend compatibility layer."""

from sqlalchemy import select

from app import database
from app.models import HeartEvent, User


def _available_skill_id(client):
    response = client.get("/compat/api/course/path")

    assert response.status_code == 200, response.text

    skill_id = response.json()["current_skill_id"]

    assert skill_id is not None

    return skill_id


def test_compat_mistake_is_persisted_immediately(client):
    skill_id = _available_skill_id(client)

    started_response = client.get(
        f"/compat/api/lesson/{skill_id}/start"
    )

    assert started_response.status_code == 200, started_response.text

    started = started_response.json()

    before = client.get(
        "/compat/api/user/me"
    ).json()["hearts"]

    exercise_id = started["exercises"][0]["id"]

    response = client.post(
        f"/compat/api/lesson/{started['lesson_id']}/mistake",
        json={
            "exercise_id": exercise_id,
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["hearts"] == before - 1

    # The important assertion: another request sees the reduced value.
    assert (
        client.get("/compat/api/user/me")
        .json()["hearts"]
        == before - 1
    )

    with database.SessionLocal() as db:
        learner = db.scalar(
            select(User).where(
                User.username == "learner"
            )
        )

        assert learner is not None

        event = db.scalar(
            select(HeartEvent)
            .where(
                HeartEvent.user_id == learner.id,
                HeartEvent.attempt_id == started["lesson_id"],
                HeartEvent.delta == -1,
            )
            .order_by(HeartEvent.id.desc())
        )

        assert event is not None


def test_compat_complete_does_not_double_charge_recorded_mistake(client):
    skill_id = _available_skill_id(client)

    started = client.get(
        f"/compat/api/lesson/{skill_id}/start"
    ).json()

    attempt_id = started["lesson_id"]
    exercise_count = len(started["exercises"])

    mistake_response = client.post(
        f"/compat/api/lesson/{attempt_id}/mistake",
        json={
            "exercise_id": started["exercises"][0]["id"],
        },
    )

    assert mistake_response.status_code == 200

    before = client.get(
        "/compat/api/user/me"
    ).json()["hearts"]

    complete_response = client.post(
        f"/compat/api/lesson/{attempt_id}/complete",
        json={
            "correct_count": exercise_count - 1,
            "mistake_count": 1,
        },
    )

    assert complete_response.status_code == 200, (
        complete_response.text
    )

    assert (
        complete_response.json()["hearts"]
        == before
    )

    with database.SessionLocal() as db:
        learner = db.scalar(
            select(User).where(
                User.username == "learner"
            )
        )

        assert learner is not None

        events = db.scalars(
            select(HeartEvent)
            .where(
                HeartEvent.user_id == learner.id,
                HeartEvent.attempt_id == attempt_id,
                HeartEvent.delta == -1,
            )
        ).all()

        assert len(events) == 1


def test_compat_rejects_completion_that_would_reach_zero_hearts(client):
    skill_id = _available_skill_id(client)

    started = client.get(
        f"/compat/api/lesson/{skill_id}/start"
    ).json()

    attempt_id = started["lesson_id"]
    total = len(started["exercises"])

    response = client.post(
        f"/compat/api/lesson/{attempt_id}/complete",
        json={
            "correct_count": 0,
            "mistake_count": total,
        },
    )

    assert response.status_code == 409

    assert (
        response.json()["detail"]["code"]
        == "OUT_OF_HEARTS"
    )