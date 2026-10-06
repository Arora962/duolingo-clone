"""Achievement evaluation and progress."""
from sqlalchemy import select, func
from app.clock import now_utc
from app.enums import AchievementMetric, AttemptStatus, SkillType
from app.models import Achievement, UserAchievement, LessonAttempt, Lesson, Skill, AttemptAnswer
from app.services.stats import current_streak,total_xp

def _metric_value(db,user_id,metric):
    if metric==AchievementMetric.STREAK_DAYS:return current_streak(db,user_id)
    if metric==AchievementMetric.TOTAL_XP:return total_xp(db,user_id)
    q=select(func.count()).select_from(LessonAttempt).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id,LessonAttempt.status==AttemptStatus.COMPLETED,Skill.skill_type!=SkillType.TREASURE)
    if metric==AchievementMetric.LESSONS_COMPLETED:return int(db.scalar(q) or 0)
    attempts=db.scalars(select(LessonAttempt).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED, Skill.skill_type!=SkillType.TREASURE)).all()
    if metric==AchievementMetric.PERFECT_LESSONS:
        n=0
        for a in attempts:
            wrong=db.scalar(select(func.count()).select_from(AttemptAnswer).where(AttemptAnswer.attempt_id==a.id,AttemptAnswer.is_correct.is_(False)))
            if not wrong:n+=1
        return n
    return 0

def evaluate(db,user_id):
    now=now_utc(db); new=[]
    earned={x.achievement_id for x in db.scalars(select(UserAchievement).where(UserAchievement.user_id==user_id)).all()}
    for achievement in db.scalars(select(Achievement).order_by(Achievement.id)).all():
        if achievement.id in earned:continue
        if _metric_value(db,user_id,achievement.metric)>=achievement.threshold:
            row=UserAchievement(user_id=user_id,achievement_id=achievement.id,unlocked_at=now); db.add(row)
            new.append(achievement)
    db.flush()
    return new

def get_achievement_progress(db,user_id):
    earned={x.achievement_id:x.unlocked_at for x in db.scalars(select(UserAchievement).where(UserAchievement.user_id==user_id)).all()}
    out=[]
    for a in db.scalars(select(Achievement).order_by(Achievement.id)).all():
        out.append({"code":a.code,"name":a.name,"description":a.description,"icon":a.icon,"metric":a.metric.value,
                    "threshold":a.threshold,"current_value":_metric_value(db,user_id,a.metric),"earned":a.id in earned,"unlocked_at":earned.get(a.id)})
    return out
