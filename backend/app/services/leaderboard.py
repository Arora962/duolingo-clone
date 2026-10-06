"""Weekly leaderboard across learner and seeded bot users."""
from datetime import datetime,timedelta,time
from sqlalchemy import select,func,case
from app.clock import today
from app.enums import AttemptStatus,SkillType
from app.models import User,LessonAttempt,Lesson,Skill

def get_leaderboard(db,user):
    d=today(db); monday=d-timedelta(days=d.weekday()); start=datetime.combine(monday,time.min); end=start+timedelta(days=7)
    rows=db.execute(select(User.id,User.username,User.display_name,User.avatar_url,User.is_seeded_bot,
        func.coalesce(func.sum(case((LessonAttempt.status==AttemptStatus.COMPLETED,LessonAttempt.xp_earned),else_=0)),0).label("weekly_xp"))
        .outerjoin(LessonAttempt,(LessonAttempt.user_id==User.id)&(LessonAttempt.finished_at>=start)&(LessonAttempt.finished_at<end))
        .outerjoin(Lesson,Lesson.id==LessonAttempt.lesson_id).outerjoin(Skill,Skill.id==Lesson.skill_id)
        .where(Skill.id.is_(None)| (Skill.skill_type!=SkillType.TREASURE))
        .group_by(User.id).order_by(func.coalesce(func.sum(case((LessonAttempt.status==AttemptStatus.COMPLETED,LessonAttempt.xp_earned),else_=0)),0).desc(),User.username)).all()
    entries=[]
    for i,r in enumerate(rows,1):
        entries.append({"rank":i,"user_id":r.id,"username":r.username,"display_name":r.display_name,"avatar_url":r.avatar_url,
                        "weekly_xp":int(r.weekly_xp or 0),"is_current_user":r.id==user.id,"is_bot":bool(r.is_seeded_bot)})
    current=next((e["rank"] for e in entries if e["is_current_user"]),None)
    return {"period_start":start,"period_end":end,"days_remaining":max(0,(end-datetime.combine(d,time.min)).days),"current_user_rank":current,"entries":entries}
