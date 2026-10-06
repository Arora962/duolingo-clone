from datetime import datetime
from pydantic import BaseModel
class AnswerRequest(BaseModel):
    exercise_id:int; option_id:int|None=None; option_ids:list[int]|None=None; text:str|None=None; left_option_id:int|None=None; right_option_id:int|None=None
class CompleteResponse(BaseModel): pass
class RefillRequest(BaseModel): method:str
