"""Derived learning-path and lesson-lock state."""
from sqlalchemy import select
from app.enums import SkillType, AttemptStatus
from app.models import Course, Skill, Lesson
from app.services.stats import completed_lesson_ids

def build_path(db,user):
    course=user.current_course
    if course is None:return None
    # Content hierarchy is selectin-loaded; one additional query loads completed IDs.
    done=completed_lesson_ids(db,user.id)
    skills=sorted((s for u in course.units for s in u.skills),key=lambda s:(s.unit.position,s.position))
    skill_done={}
    for s in skills:
        skill_done[s.id]=all(l.id in done for l in s.lessons) if s.lessons else False
    current_id=next((s.id for s in skills if not skill_done[s.id]),None)
    result_units=[]
    previous_completed=True
    for unit in sorted(course.units,key=lambda u:u.position):
        unit_skills=sorted(unit.skills,key=lambda s:s.position)
        out=[]
        for s in unit_skills:
            state="COMPLETED" if skill_done[s.id] else ("AVAILABLE" if previous_completed else "LOCKED")
            lessons=sorted(s.lessons,key=lambda l:l.position)
            lesson_out=[]; prior=True
            for l in lessons:
                ls="COMPLETED" if l.id in done else ("AVAILABLE" if prior and state!="LOCKED" else "LOCKED")
                lesson_out.append({"id":l.id,"position":l.position,"xp_reward":l.xp_reward,"state":ls})
                prior=prior and l.id in done
            completed=sum(1 for l in lessons if l.id in done)
            out.append({"id":s.id,"position":s.position,"title":s.title,"skill_type":s.skill_type.value,"icon_type":s.icon_type.value,
                        "state":state,"is_current":s.id==current_id,"lessons_total":len(lessons),"lessons_completed":completed,
                        "progress_ratio":completed/len(lessons) if lessons else 0.0,"crowns":completed,"crowns_max":len(lessons),
                        "next_lesson_id":next((l.id for l in lessons if l.id not in done),None),"lessons":lesson_out})
            previous_completed=previous_completed and skill_done[s.id]
        result_units.append({"id":unit.id,"position":unit.position,"title":unit.title,"description":unit.description,"color_bg":unit.color_bg,
                             "color_border":unit.color_border,"skills_completed":sum(skill_done[s.id] for s in unit_skills),"skills_total":len(unit_skills),"skills":out})
    return {"course":{"id":course.id,"language_code":course.language_code,"name":course.name,"flag_emoji":course.flag_emoji},"units":result_units}

def skill_state(db,user,skill):
    path=build_path(db,user)
    for u in path["units"]:
        for s in u["skills"]:
            if s["id"]==skill.id:return s
    return None
