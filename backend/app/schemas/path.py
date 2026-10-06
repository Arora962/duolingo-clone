from pydantic import BaseModel
class LessonPath(BaseModel): id:int; position:int; xp_reward:int; state:str
class SkillPath(BaseModel):
    id:int; position:int; title:str; skill_type:str; icon_type:str; state:str; is_current:bool
    lessons_total:int; lessons_completed:int; progress_ratio:float; crowns:int; crowns_max:int; next_lesson_id:int|None; lessons:list[LessonPath]
class UnitPath(BaseModel):
    id:int; position:int; title:str; description:str; color_bg:str; color_border:str; skills_completed:int; skills_total:int; skills:list[SkillPath]
class PathResponse(BaseModel):
    course:dict; units:list[UnitPath]
