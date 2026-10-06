from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import get_current_user
from app.models import User
from app.services.stats import total_xp,current_streak,streak_active_today,current_hearts_status,xp_today,daily_goal
from app.services.achievements import get_achievement_progress
from app.schemas.settings import SettingsPatch,SettingsResponse
from app.errors import api_error
router=APIRouter(tags=["me"])

@router.get("/me",summary="Get the current learner")
def me(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    hs=current_hearts_status(db,user.id); goal,xp,met=daily_goal(db,user.id); total=total_xp(db,user.id); streak=current_streak(db,user.id)
    return {"id":user.id,"username":user.username,"display_name":user.display_name,"avatar_url":user.avatar_url,"gems":user.gems,
            "total_xp":total,"current_streak":streak,"streak_active_today":streak_active_today(db,user.id),"hearts":hs["hearts"],"max_hearts":hs["max_hearts"],
            "next_heart_in_seconds":hs["next_heart_in_seconds"],"daily_goal_xp":goal,"xp_today":xp,"daily_goal_met":met,
            "current_course":{"id":user.current_course.id,"language_code":user.current_course.language_code,"name":user.current_course.name,"flag_emoji":user.current_course.flag_emoji},
            "xp":total,"streak":streak}

@router.get("/profile",summary="Get learner profile and achievements")
def profile(db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    total=total_xp(db,user.id)
    from app.services.stats import longest_streak,perfect_lessons
    return {"user":{"id":user.id,"username":user.username,"display_name":user.display_name,"avatar_url":user.avatar_url,"joined_at":user.created_at},
            "stats":{"total_xp":total,"current_streak":current_streak(db,user.id),"longest_streak":longest_streak(db,user.id),
                     "lessons_completed":__import__("app.services.stats",fromlist=["non_treasure_lessons_completed"]).non_treasure_lessons_completed(db,user.id),
                     "perfect_lessons":perfect_lessons(db,user.id),"xp_today":xp_today(db,user.id),"daily_goal_xp":user.settings.daily_goal_xp if user.settings else 20,"gems":user.gems},
            "course":{"id":user.current_course.id,"language_code":user.current_course.language_code,"name":user.current_course.name,"flag_emoji":user.current_course.flag_emoji},
            "achievements":get_achievement_progress(db,user.id)}

@router.get("/settings",response_model=SettingsResponse,summary="Get learner settings")
def get_settings(user:User=Depends(get_current_user)):
    s=user.settings
    return {"daily_goal_xp":s.daily_goal_xp,"sound_effects_enabled":s.sound_effects_enabled,"dark_mode_enabled":s.dark_mode_enabled,"reminders_enabled":s.reminders_enabled}

@router.patch("/settings",response_model=SettingsResponse,summary="Update learner settings")
def patch_settings(payload:SettingsPatch,db:Session=Depends(get_db),user:User=Depends(get_current_user)):
    s=user.settings
    if payload.daily_goal_xp is not None:
        if payload.daily_goal_xp not in {10,20,30,50}: api_error(422,"INVALID_DAILY_GOAL","daily_goal_xp must be one of 10, 20, 30, 50.")
        s.daily_goal_xp=payload.daily_goal_xp
    for key in ("sound_effects_enabled","dark_mode_enabled","reminders_enabled"):
        value=getattr(payload,key)
        if value is not None:setattr(s,key,value)
    db.flush()
    return s
