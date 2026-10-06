from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class User(TimestampMixin, Base):
    """A learner account; XP, streak, hearts, and progress are derived elsewhere."""

    __tablename__ = "users"
    __table_args__ = (CheckConstraint("gems >= 0", name="ck_users_gems_nonnegative"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, unique=True)
    current_course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"), nullable=True, index=True)
    gems: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    is_seeded_bot: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")

    current_course: Mapped["Course | None"] = relationship(back_populates="users", lazy="select")
    settings: Mapped["UserSettings | None"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False, lazy="select")
    lesson_attempts: Mapped[list["LessonAttempt"]] = relationship(back_populates="user", cascade="all, delete-orphan", lazy="select")
    heart_events: Mapped[list["HeartEvent"]] = relationship(back_populates="user", cascade="all, delete-orphan", lazy="select")
    user_achievements: Mapped[list["UserAchievement"]] = relationship(back_populates="user", cascade="all, delete-orphan", lazy="select")


class UserSettings(TimestampMixin, Base):
    """One-to-one learner preferences and daily XP goal."""

    __tablename__ = "user_settings"
    __table_args__ = (CheckConstraint("daily_goal_xp IN (10, 20, 30, 50)", name="ck_user_settings_daily_goal_xp"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    daily_goal_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=20, server_default="20")
    sound_effects_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")
    dark_mode_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")

    user: Mapped[User] = relationship(back_populates="settings", lazy="select")
