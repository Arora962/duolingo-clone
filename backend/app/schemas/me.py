from pydantic import BaseModel, ConfigDict
class CourseMini(BaseModel):
    id:int; language_code:str; name:str; flag_emoji:str
class MeResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id:int; username:str; display_name:str; avatar_url:str|None=None; gems:int
    total_xp:int; current_streak:int; streak_active_today:bool; hearts:int; max_hearts:int
    next_heart_in_seconds:int|None; daily_goal_xp:int; xp_today:int; daily_goal_met:bool
    current_course:CourseMini; xp:int; streak:int
