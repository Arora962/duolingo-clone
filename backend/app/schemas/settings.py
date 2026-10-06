"""Learner settings request and response models."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class SettingsResponse(BaseModel):
    """Current learner settings."""

    daily_goal_xp: int
    sound_effects_enabled: bool
    dark_mode_enabled: bool
    reminders_enabled: bool


class SettingsPatch(BaseModel):
    """Validated partial settings update."""

    model_config = ConfigDict(extra="forbid")

    daily_goal_xp: Literal[10, 20, 30, 50] | None = None
    sound_effects_enabled: bool | None = None
    dark_mode_enabled: bool | None = None
    reminders_enabled: bool | None = None
