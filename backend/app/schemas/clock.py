from datetime import date,datetime
from pydantic import BaseModel
class ClockResponse(BaseModel): time_offset_days:int; simulated_now:datetime; simulated_today:date
class AdvanceRequest(BaseModel): days:int=1
