from pydantic import BaseModel, ConfigDict, Field
class SettingsResponse(BaseModel):
    daily_goal_xp:int; sound_effects_enabled:bool; dark_mode_enabled:bool; reminders_enabled:bool
class SettingsPatch(BaseModel):
    daily_goal_xp:int|None=Field(default=None); sound_effects_enabled:bool|None=None; dark_mode_enabled:bool|None=None; reminders_enabled:bool|None=None
    model_config=ConfigDict(extra="forbid")
