from datetime import datetime
from pydantic import BaseModel
class LeaderboardEntry(BaseModel):
    rank:int; user_id:int; username:str; display_name:str; avatar_url:str|None; weekly_xp:int; is_current_user:bool; is_bot:bool
class LeaderboardResponse(BaseModel):
    period_start:datetime; period_end:datetime; days_remaining:int; current_user_rank:int|None; entries:list[LeaderboardEntry]
