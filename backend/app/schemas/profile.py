from pydantic import BaseModel
class ProfileResponse(BaseModel): user:dict; stats:dict; course:dict; achievements:list[dict]
