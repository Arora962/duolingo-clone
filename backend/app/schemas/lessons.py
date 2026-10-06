"""Request and response models for lesson attempts."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AnswerRequest(BaseModel):
    """Accepted answer payload for every exercise type."""

    model_config = ConfigDict(extra="forbid")

    exercise_id: int
    option_id: int | None = None
    option_ids: list[int] | None = None
    text: str | None = None
    left_option_id: int | None = None
    right_option_id: int | None = None


class ExerciseOptionOut(BaseModel):
    """Safe multiple-choice option payload."""

    id: int
    text: str
    image_emoji: str | None


class ExerciseBase(BaseModel):
    """Fields shared by all lesson exercises."""

    model_config = ConfigDict(extra="forbid")

    id: int
    position: int
    prompt: str
    source_text: str | None
    hint: str | None
    audio_url: str | None


class MultipleChoiceExercise(ExerciseBase):
    """Multiple-choice exercise payload."""

    type: Literal["MULTIPLE_CHOICE"]
    options: list[ExerciseOptionOut]


class FillInBlankOptionsExercise(ExerciseBase):
    """Fill-in-the-blank exercise with selectable options."""

    type: Literal["FILL_IN_BLANK"]
    options: list[ExerciseOptionOut]


class FillInBlankTypingExercise(ExerciseBase):
    """Fill-in-the-blank exercise requiring typed input."""

    type: Literal["FILL_IN_BLANK"]
    requires_typing: Literal[True]


class WordBankTile(BaseModel):
    """One visible word-bank tile."""

    id: int
    text: str


class TranslateWordBankExercise(ExerciseBase):
    """Word-bank translation exercise."""

    type: Literal["TRANSLATE_WORD_BANK"]
    tiles: list[WordBankTile]


class MatchPairItem(BaseModel):
    """One visible side of a matching pair."""

    id: int
    text: str


class MatchPairsExercise(ExerciseBase):
    """Matching exercise payload."""

    type: Literal["MATCH_PAIRS"]
    left: list[MatchPairItem]
    right: list[MatchPairItem]


class TypeAnswerExercise(ExerciseBase):
    """Typed-answer exercise payload."""

    type: Literal["TYPE_ANSWER"]


ExerciseOut = (
    MultipleChoiceExercise
    | FillInBlankOptionsExercise
    | FillInBlankTypingExercise
    | TranslateWordBankExercise
    | MatchPairsExercise
    | TypeAnswerExercise
)


class LessonSkillSummary(BaseModel):
    """Skill identity returned when a lesson starts."""

    id: int
    title: str
    skill_type: str


class StartLessonResponse(BaseModel):
    """Lesson attempt start response."""

    attempt_id: int
    lesson_id: int
    skill: LessonSkillSummary
    mode: str
    xp_reward: int
    hearts: int
    max_hearts: int
    time_limit_seconds: int | None
    expires_at: datetime | None
    total_exercises: int
    exercises: list[ExerciseOut]


class AnswerResult(BaseModel):
    """Answer evaluation response."""

    is_correct: bool
    correct_answer: str | None
    speak_text: str | None
    speak_lang: str | None
    audio_url: str | None
    exercise_solved: bool
    solved_exercises: int
    total_exercises: int
    progress_percent: int
    all_exercises_solved: bool
    hearts: int
    next_heart_in_seconds: int | None
    lesson_failed: bool
    failure_reason: str | None


class CompleteSkill(BaseModel):
    """Updated skill state after completion."""

    id: int
    state: str
    lessons_completed: int
    lessons_total: int
    crowns: int


class NextSkillUnlocked(BaseModel):
    """Identity of a newly available skill."""

    id: int
    title: str


class NewlyUnlockedAchievement(BaseModel):
    """Achievement newly awarded by a completion."""

    code: str
    name: str
    description: str
    icon: str


class CompleteResult(BaseModel):
    """Lesson completion response."""

    xp_earned: int
    total_xp: int
    accuracy_percent: float
    time_spent_seconds: int
    streak_before: int
    streak_after: int
    streak_extended: bool
    xp_today: int
    daily_goal_xp: int
    goal_just_met: bool
    hearts: int
    skill: CompleteSkill
    skill_just_completed: bool
    next_skill_unlocked: NextSkillUnlocked | None
    newly_unlocked_achievements: list[NewlyUnlockedAchievement]


class AbandonResponse(BaseModel):
    """Lesson abandonment response."""

    status: Literal["ABANDONED"]


class TreasureResponse(BaseModel):
    """Treasure reward response."""

    gems_awarded: int
    gems: int
