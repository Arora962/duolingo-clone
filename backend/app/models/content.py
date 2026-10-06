"""Content models for the seeded, shared language course.

Exercise type mapping:
- MULTIPLE_CHOICE: exercise + 3-4 options, exactly one is_correct.
- TRANSLATE_WORD_BANK: source_text + tiles as options (answer_order set for correct
  tiles, NULL for distractors) + full valid sentences in accepted_answers.
- MATCH_PAIRS: 4-5 pairs as options sharing pair_key, one LEFT and one RIGHT each.
- FILL_IN_BLANK: source_text with "____" + options with is_correct (or
  accepted_answers if typed).
- TYPE_ANSWER: source_text + accepted_answers.
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.enums import ExerciseType, OptionSide, SkillIcon, SkillType
from app.models.mixins import TimestampMixin


def enum_column(enum_cls, length: int):
    """Build a non-native SQLAlchemy enum column for SQLite."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        create_constraint=True,
        length=length,
        nullable=False,
    )


class Course(TimestampMixin, Base):
    """A language course shared by all learners."""

    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint("language_code", name="uq_courses_language_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    ui_language_code: Mapped[str] = mapped_column(String(10), nullable=False)
    flag_emoji: Mapped[str] = mapped_column(String(16), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="1",
    )

    units: Mapped[list["Unit"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Unit.position",
    )
    users: Mapped[list["User"]] = relationship(
        back_populates="current_course",
        lazy="select",
    )


class Unit(TimestampMixin, Base):
    """An ordered course unit containing skills."""

    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("course_id", "position", name="uq_units_course_position"),
        CheckConstraint("position >= 1", name="ck_units_position_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    color_bg: Mapped[str] = mapped_column(String(20), nullable=False)
    color_border: Mapped[str] = mapped_column(String(20), nullable=False)

    course: Mapped["Course"] = relationship(
        back_populates="units",
        lazy="select",
    )
    skills: Mapped[list["Skill"]] = relationship(
        back_populates="unit",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Skill.position",
    )


class Skill(TimestampMixin, Base):
    """An ordered skill that groups lessons or special practice content."""

    __tablename__ = "skills"
    __table_args__ = (
        UniqueConstraint("unit_id", "position", name="uq_skills_unit_position"),
        CheckConstraint("position >= 1", name="ck_skills_position_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    unit_id: Mapped[int] = mapped_column(
        ForeignKey("units.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    skill_type: Mapped[SkillType] = mapped_column(enum_column(SkillType, 20))
    icon_type: Mapped[SkillIcon] = mapped_column(enum_column(SkillIcon, 20))

    unit: Mapped["Unit"] = relationship(
        back_populates="skills",
        lazy="select",
    )
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="skill",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Lesson.position",
    )


class Lesson(TimestampMixin, Base):
    """A scored lesson containing an ordered set of exercises."""

    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("skill_id", "position", name="uq_lessons_skill_position"),
        CheckConstraint("position >= 1", name="ck_lessons_position_positive"),
        CheckConstraint("xp_reward >= 0", name="ck_lessons_xp_reward_nonnegative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    xp_reward: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
        server_default="10",
    )

    skill: Mapped["Skill"] = relationship(
        back_populates="lessons",
        lazy="select",
    )
    exercises: Mapped[list["Exercise"]] = relationship(
        back_populates="lesson",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Exercise.position",
    )
    attempts: Mapped[list["LessonAttempt"]] = relationship(
        back_populates="lesson",
        passive_deletes=True,
        lazy="select",
    )


class Exercise(TimestampMixin, Base):
    """A single question presented during a lesson."""

    __tablename__ = "exercises"
    __table_args__ = (
        UniqueConstraint(
            "lesson_id",
            "position",
            name="uq_exercises_lesson_position",
        ),
        CheckConstraint("position >= 1", name="ck_exercises_position_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[ExerciseType] = mapped_column(enum_column(ExerciseType, 32))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    lesson: Mapped["Lesson"] = relationship(
        back_populates="exercises",
        lazy="select",
    )
    options: Mapped[list["ExerciseOption"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="ExerciseOption.position",
    )
    accepted_answers: Mapped[list["ExerciseAcceptedAnswer"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="ExerciseAcceptedAnswer.id",
    )
    attempt_answers: Mapped[list["AttemptAnswer"]] = relationship(
        back_populates="exercise",
        passive_deletes=True,
        lazy="select",
    )


class ExerciseOption(TimestampMixin, Base):
    """A selectable tile, choice, or matching item belonging to an exercise."""

    __tablename__ = "exercise_options"
    __table_args__ = (
        UniqueConstraint(
            "exercise_id",
            "position",
            name="uq_exercise_options_exercise_position",
        ),
        CheckConstraint(
            "position >= 1",
            name="ck_exercise_options_position_positive",
        ),
        CheckConstraint(
            "answer_order IS NULL OR answer_order >= 1",
            name="ck_exercise_options_answer_order_positive",
        ),
        CheckConstraint(
            "(pair_key IS NULL) = (side IS NULL)",
            name="ck_exercise_options_pair_side_together",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    image_emoji: Mapped[str | None] = mapped_column(String(16), nullable=True)
    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )
    answer_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pair_key: Mapped[str | None] = mapped_column(String(50), nullable=True)
    side: Mapped[OptionSide | None] = mapped_column(
        SAEnum(
            OptionSide,
            native_enum=False,
            create_constraint=True,
            length=10,
        ),
        nullable=True,
    )

    exercise: Mapped["Exercise"] = relationship(
        back_populates="options",
        lazy="select",
    )


class ExerciseAcceptedAnswer(TimestampMixin, Base):
    """A valid typed or translated answer for an exercise."""

    __tablename__ = "exercise_accepted_answers"
    __table_args__ = (
        UniqueConstraint(
            "exercise_id",
            "answer_text",
            name="uq_exercise_accepted_answers_exercise_text",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exercise_id: Mapped[int] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
    )

    exercise: Mapped["Exercise"] = relationship(
        back_populates="accepted_answers",
        lazy="select",
    )
