"""Learner event history and derived gamification support records."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import AchievementMetric, AttemptStatus, HeartEventType
from app.models.mixins import TimestampMixin


class LessonAttempt(Base):
    """One run of a lesson and the XP recorded when it finishes."""

    __tablename__ = "lesson_attempts"
    __table_args__ = (
        CheckConstraint("xp_earned >= 0", name="ck_lesson_attempts_xp_earned_nonnegative"),
        CheckConstraint("(finished_at IS NULL) = (status = 'IN_PROGRESS')", name="ck_lesson_attempts_finished_matches_status"),
        # Composite index supports profile, streak, and leaderboard queries.
        Index("ix_lesson_attempts_user_status_finished", "user_id", "status", "finished_at"),
        Index("ix_lesson_attempts_lesson_id", "lesson_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="RESTRICT"), nullable=False)
    status: Mapped[AttemptStatus] = mapped_column(SAEnum(AttemptStatus, native_enum=False, create_constraint=True, length=24), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    user: Mapped["User"] = relationship(back_populates="lesson_attempts", lazy="select")
    lesson: Mapped["Lesson"] = relationship(back_populates="attempts", lazy="select")
    answers: Mapped[list["AttemptAnswer"]] = relationship(back_populates="attempt", cascade="all, delete-orphan", lazy="select")
    heart_events: Mapped[list["HeartEvent"]] = relationship(back_populates="attempt", passive_deletes=True, lazy="select")


class AttemptAnswer(Base):
    """One submitted answer, preserving correctness as recorded at answer time."""

    __tablename__ = "attempt_answers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("lesson_attempts.id", ondelete="CASCADE"), nullable=False, index=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"), nullable=False, index=True)
    submitted_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    attempt: Mapped[LessonAttempt] = relationship(back_populates="answers", lazy="select")
    exercise: Mapped["Exercise"] = relationship(back_populates="attempt_answers", lazy="select")


class HeartEvent(Base):
    """A heart ledger event; current hearts are replayed plus lazy regeneration."""

    __tablename__ = "heart_events"
    __table_args__ = (CheckConstraint("delta != 0", name="ck_heart_events_delta_nonzero"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type: Mapped[HeartEventType] = mapped_column(SAEnum(HeartEventType, native_enum=False, create_constraint=True, length=24), nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    attempt_id: Mapped[int | None] = mapped_column(ForeignKey("lesson_attempts.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    user: Mapped["User"] = relationship(back_populates="heart_events", lazy="select")
    attempt: Mapped["LessonAttempt | None"] = relationship(back_populates="heart_events", lazy="select")


class Achievement(TimestampMixin, Base):
    """A milestone definition that can be unlocked by a learner."""

    __tablename__ = "achievements"
    __table_args__ = (CheckConstraint("threshold > 0", name="ck_achievements_threshold_positive"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(String(16), nullable=False)
    metric: Mapped[AchievementMetric] = mapped_column(SAEnum(AchievementMetric, native_enum=False, create_constraint=True, length=24), nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, nullable=False)

    user_achievements: Mapped[list["UserAchievement"]] = relationship(back_populates="achievement", passive_deletes=True, lazy="select")


class UserAchievement(Base):
    """Historical link recording when a learner earned an achievement."""

    __tablename__ = "user_achievements"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id", ondelete="RESTRICT"), primary_key=True)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship(back_populates="user_achievements", lazy="select")
    achievement: Mapped[Achievement] = relationship(back_populates="user_achievements", lazy="select")


class SystemSetting(Base):
    """A small key/value store for system-level simulation settings."""

    __tablename__ = "system_settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
