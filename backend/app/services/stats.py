"""Derived XP, streak, lesson and heart statistics."""
from datetime import date, datetime, time, timedelta
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.clock import now_utc, today
from app.enums import AttemptStatus, HeartEventType, SkillType
from app.models import HeartEvent, LessonAttempt, Lesson, Skill, UserSettings

MAX_HEARTS = 5
HEART_REGEN_MINUTES = 30

def _completed_non_treasure_filter():
    return LessonAttempt.status == AttemptStatus.COMPLETED, Skill.skill_type != SkillType.TREASURE

def total_xp(db, user_id):
    value = db.scalar(select(func.coalesce(func.sum(LessonAttempt.xp_earned),0)).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED,
        Skill.skill_type != SkillType.TREASURE))
    return int(value or 0)

def xp_on(db, user_id, day):
    start=datetime.combine(day,time.min); end=start+timedelta(days=1)
    value=db.scalar(select(func.coalesce(func.sum(LessonAttempt.xp_earned),0)).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED,
        Skill.skill_type != SkillType.TREASURE, LessonAttempt.finished_at>=start, LessonAttempt.finished_at<end))
    return int(value or 0)

def xp_today(db,user_id): return xp_on(db,user_id,today(db))

def xp_this_week(db,user_id):
    current=today(db); monday=current-timedelta(days=current.weekday())
    value=db.scalar(select(func.coalesce(func.sum(LessonAttempt.xp_earned),0)).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED,
        Skill.skill_type != SkillType.TREASURE, LessonAttempt.finished_at>=datetime.combine(monday,time.min),
        LessonAttempt.finished_at<datetime.combine(monday+timedelta(days=7),time.min)))
    return int(value or 0)

def active_days(db,user_id):
    rows=db.execute(select(LessonAttempt.finished_at).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED,
        Skill.skill_type != SkillType.TREASURE, LessonAttempt.finished_at.is_not(None))).scalars().all()
    return {v.date() for v in rows if v}

def current_streak(db,user_id):
    days=active_days(db,user_id); cur=today(db)
    if cur not in days: cur-=timedelta(days=1)
    n=0
    while cur in days: n+=1; cur-=timedelta(days=1)
    return n

def longest_streak(db,user_id):
    days=sorted(active_days(db,user_id))
    if not days:return 0
    best=run=1
    for a,b in zip(days,days[1:]):
        run=run+1 if b==a+timedelta(days=1) else 1
        best=max(best,run)
    return best

def streak_active_today(db,user_id): return today(db) in active_days(db,user_id)

def completed_lesson_ids(db,user_id):
    """Return every lesson with a completed attempt; path state includes treasure claims."""
    rows=db.execute(select(LessonAttempt.lesson_id).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED).distinct()).scalars().all()
    return set(rows)

def non_treasure_lessons_completed(db,user_id):
    value=db.scalar(select(func.count(func.distinct(LessonAttempt.lesson_id))).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED,
        Skill.skill_type != SkillType.TREASURE))
    return int(value or 0)

def skill_lessons_completed(db,user_id,skill_id):
    value=db.scalar(select(func.count(func.distinct(LessonAttempt.lesson_id))).join(Lesson).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED,
        Lesson.skill_id==skill_id))
    # Treasure/practice progress is still structurally valid; callers decide visibility.
    return int(value or 0)

def perfect_lessons(db,user_id):
    sub=select(LessonAttempt.id).join(Lesson).join(Skill).where(
        LessonAttempt.user_id==user_id, LessonAttempt.status==AttemptStatus.COMPLETED,
        Skill.skill_type != SkillType.TREASURE)
    attempts=db.scalars(sub).all()
    if not attempts:return 0
    from app.models import AttemptAnswer
    n=0
    for attempt_id in attempts:
        wrong=db.scalar(select(func.count()).select_from(AttemptAnswer).where(
            AttemptAnswer.attempt_id==attempt_id, AttemptAnswer.is_correct.is_(False)))
        if not wrong:n+=1
    return n

def current_hearts_status(db,user_id):
    events=db.scalars(select(HeartEvent).where(HeartEvent.user_id==user_id).order_by(HeartEvent.created_at,HeartEvent.id)).all()
    hearts=MAX_HEARTS; anchor=None
    now=now_utc(db)
    for event in events:
        if hearts<MAX_HEARTS and anchor is not None:
            gained=max(0,int((event.created_at-anchor).total_seconds()//(HEART_REGEN_MINUTES*60)))
            if gained:
                hearts=min(MAX_HEARTS,hearts+gained)
                anchor=anchor+timedelta(minutes=HEART_REGEN_MINUTES*gained)
                if hearts==MAX_HEARTS: anchor=None
        if event.event_type==HeartEventType.LOST and event.delta<0:
            if hearts==MAX_HEARTS: anchor=event.created_at
            hearts=max(0,hearts+event.delta)
            if hearts==MAX_HEARTS: anchor=None
        elif event.delta>0:
            hearts=min(MAX_HEARTS,hearts+event.delta)
            if hearts==MAX_HEARTS: anchor=None
    if hearts<MAX_HEARTS and anchor is not None:
        gained=max(0,int((now-anchor).total_seconds()//(HEART_REGEN_MINUTES*60)))
        if gained:
            hearts=min(MAX_HEARTS,hearts+gained); anchor=anchor+timedelta(minutes=HEART_REGEN_MINUTES*gained)
            if hearts==MAX_HEARTS: anchor=None
    next_seconds=None
    if hearts<MAX_HEARTS and anchor is not None:
        next_seconds=max(0,int((anchor+timedelta(minutes=HEART_REGEN_MINUTES)-now).total_seconds()))
    return {"hearts":max(0,min(MAX_HEARTS,hearts)),"max_hearts":MAX_HEARTS,"next_heart_in_seconds":next_seconds}

def current_hearts(db,user_id): return current_hearts_status(db,user_id)["hearts"]

def daily_goal(db,user_id):
    settings=db.get(UserSettings,user_id)
    goal=settings.daily_goal_xp if settings else 20
    xp=xp_today(db,user_id)
    return goal,xp,xp>=goal
