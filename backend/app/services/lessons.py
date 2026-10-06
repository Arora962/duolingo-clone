"""Lesson attempt lifecycle and exercise payload construction."""
from datetime import timedelta
import random
from sqlalchemy import select
from app.clock import now_utc
from app.enums import AttemptStatus, SkillType, ExerciseType, HeartEventType
from app.models import Lesson,LessonAttempt,AttemptAnswer,HeartEvent,Skill
from app.services.stats import current_hearts_status,MAX_HEARTS,current_streak,xp_today,total_xp
from app.services.answers import check_answer,solved_exercise_ids
from app.services.path import skill_state,build_path
from app.services.achievements import evaluate
from app.errors import api_error
TIMED_PRACTICE_SECONDS=180

def _exercise_public(ex, course_code, start_payload=True):
    d={"id":ex.id,"position":ex.position,"type":ex.type.value,"prompt":ex.prompt,"source_text":ex.source_text,"hint":ex.hint,"audio_url":ex.audio_url}
    if ex.type in (ExerciseType.MULTIPLE_CHOICE,ExerciseType.FILL_IN_BLANK):
        if ex.options:d["options"]=[{"id":o.id,"text":o.text,"image_emoji":o.image_emoji} for o in sorted(ex.options,key=lambda x:x.position)]
        else:d["requires_typing"]=True
    elif ex.type==ExerciseType.TRANSLATE_WORD_BANK:
        tiles=[{"id":o.id,"text":o.text} for o in ex.options]; random.SystemRandom().shuffle(tiles); d["tiles"]=tiles
    elif ex.type==ExerciseType.MATCH_PAIRS:
        left=[{"id":o.id,"text":o.text} for o in ex.options if o.side.value=="LEFT"]
        right=[{"id":o.id,"text":o.text} for o in ex.options if o.side.value=="RIGHT"]
        random.SystemRandom().shuffle(right); d["left"]=left; d["right"]=right
    return d

def _expiry(attempt,lesson,now):
    return lesson.skill.skill_type==SkillType.PRACTICE and now>=attempt.started_at+timedelta(seconds=TIMED_PRACTICE_SECONDS)

def start(db,user,lesson_id):
    lesson=db.get(Lesson,lesson_id)
    if not lesson:api_error(404,"LESSON_NOT_FOUND","Lesson not found.")
    state=skill_state(db,user,lesson.skill)
    if lesson.skill.skill_type==SkillType.TREASURE:api_error(409,"TREASURE_USE_CLAIM","Treasure skills must be claimed with claim-treasure.")
    if state is None or state["state"]=="LOCKED":api_error(403,"SKILL_LOCKED","This skill is locked.")
    lesson_state=next(x["state"] for x in state["lessons"] if x["id"]==lesson.id)
    if lesson_state=="LOCKED":api_error(403,"LESSON_LOCKED","This lesson is locked.")
    hs=current_hearts_status(db,user.id)
    if hs["hearts"]==0:api_error(409,"OUT_OF_HEARTS","You have no hearts available.",next_heart_in_seconds=hs["next_heart_in_seconds"],refill_cost_gems=100)
    now=now_utc(db)
    for old in db.scalars(select(LessonAttempt).where(LessonAttempt.user_id==user.id,LessonAttempt.status==AttemptStatus.IN_PROGRESS)).all():
        old.status=AttemptStatus.ABANDONED;old.finished_at=now
    attempt=LessonAttempt(user_id=user.id,lesson_id=lesson.id,status=AttemptStatus.IN_PROGRESS,started_at=now,finished_at=None,xp_earned=0)
    db.add(attempt);db.flush()
    mode="TIMED_PRACTICE" if lesson.skill.skill_type==SkillType.PRACTICE else "STANDARD"
    return {"attempt_id":attempt.id,"lesson_id":lesson.id,"skill":{"id":lesson.skill.id,"title":lesson.skill.title,"skill_type":lesson.skill.skill_type.value},
            "mode":mode,"xp_reward":lesson.xp_reward,"hearts":hs["hearts"],"max_hearts":MAX_HEARTS,
            "time_limit_seconds":TIMED_PRACTICE_SECONDS if mode!="STANDARD" else None,
            "expires_at":attempt.started_at+timedelta(seconds=TIMED_PRACTICE_SECONDS) if mode!="STANDARD" else None,
            "total_exercises":len(lesson.exercises),"exercises":[_exercise_public(e,user.current_course.language_code) for e in sorted(lesson.exercises,key=lambda x:x.position)]}

def answer(db,user,attempt_id,payload):
    attempt=db.scalar(select(LessonAttempt).where(LessonAttempt.id==attempt_id,LessonAttempt.user_id==user.id))
    if not attempt:api_error(404,"ATTEMPT_NOT_FOUND","Attempt not found.")
    if attempt.status!=AttemptStatus.IN_PROGRESS:api_error(409,"ATTEMPT_NOT_ACTIVE","This lesson attempt is no longer active.")
    lesson=attempt.lesson; now=now_utc(db)
    if _expiry(attempt,lesson,now):
        attempt.status=AttemptStatus.ABANDONED;attempt.finished_at=now;db.flush();api_error(409,"TIME_EXPIRED","The timed practice has expired.")
    exercise=db.get(__import__("app.models",fromlist=["Exercise"]).Exercise,payload.get("exercise_id"))
    if not exercise or exercise.lesson_id!=lesson.id:api_error(404,"EXERCISE_NOT_FOUND","Exercise does not belong to this attempt's lesson.")
    correct,submitted,correct_answer=check_answer(exercise,payload)
    db.add(AttemptAnswer(attempt_id=attempt.id,exercise_id=exercise.id,submitted_answer=submitted,is_correct=correct,answered_at=now));db.flush()
    if not correct:
        db.add(HeartEvent(user_id=user.id,event_type=HeartEventType.LOST,delta=-1,attempt_id=attempt.id,created_at=now));db.flush()
    hs=current_hearts_status(db,user.id)
    solved=solved_exercise_ids(attempt)
    failed=hs["hearts"]==0 and not correct
    if failed:
        attempt.status=AttemptStatus.FAILED_NO_HEARTS;attempt.finished_at=now;db.flush()
    return {"is_correct":correct,"correct_answer":correct_answer,"speak_text":correct_answer,
            "speak_lang":user.current_course.language_code if user.current_course else None,"audio_url":exercise.audio_url,
            "exercise_solved":exercise.id in solved,"solved_exercises":len(solved),"total_exercises":len(lesson.exercises),
            "progress_percent":round(len(solved)/len(lesson.exercises)*100) if lesson.exercises else 100,
            "all_exercises_solved":len(solved)==len(lesson.exercises),"hearts":hs["hearts"],"next_heart_in_seconds":hs["next_heart_in_seconds"],
            "lesson_failed":failed,"failure_reason":"OUT_OF_HEARTS" if failed else None}

def complete(db,user,attempt_id):
    attempt=db.scalar(select(LessonAttempt).where(LessonAttempt.id==attempt_id,LessonAttempt.user_id==user.id))
    if not attempt:api_error(404,"ATTEMPT_NOT_FOUND","Attempt not found.")
    if attempt.status!=AttemptStatus.IN_PROGRESS:api_error(409,"ATTEMPT_NOT_ACTIVE","This lesson attempt is no longer active.")
    now=now_utc(db)
    if _expiry(attempt,attempt.lesson,now):
        attempt.status=AttemptStatus.ABANDONED;attempt.finished_at=now;db.flush();api_error(409,"TIME_EXPIRED","The timed practice has expired.")
    solved=solved_exercise_ids(attempt)
    if len(solved)!=len(attempt.lesson.exercises):api_error(409,"NOT_ALL_EXERCISES_SOLVED","Every exercise must be solved before completion.",solved_exercises=len(solved),total_exercises=len(attempt.lesson.exercises))
    before_streak=current_streak(db,user.id); before_today=xp_today(db,user.id)
    attempt.status=AttemptStatus.COMPLETED;attempt.finished_at=now;attempt.xp_earned=attempt.lesson.xp_reward;db.flush()
    after_streak=current_streak(db,user.id); after_today=xp_today(db,user.id)
    total=total_xp(db,user.id)
    answers=attempt.answers; accuracy=round(sum(a.is_correct for a in answers)/len(answers)*100,2) if answers else 100.0
    new_achievements=evaluate(db,user.id)
    state=skill_state(db,user,attempt.lesson.skill)
    skill_just=state["state"]=="COMPLETED"
    path=build_path(db,user); skills=[s for u in path["units"] for s in u["skills"]]; idx=next((i for i,s in enumerate(skills) if s["id"]==attempt.lesson.skill_id),-1)
    next_unlocked=None
    if idx>=0 and idx+1<len(skills) and skills[idx+1]["state"]=="AVAILABLE":next_unlocked={"id":skills[idx+1]["id"],"title":skills[idx+1]["title"]}
    return {"xp_earned":attempt.xp_earned,"total_xp":total,"accuracy_percent":accuracy,"time_spent_seconds":int((now-attempt.started_at).total_seconds()),
            "streak_before":before_streak,"streak_after":after_streak,"streak_extended":after_streak>before_streak,
            "xp_today":after_today,"daily_goal_xp":user.settings.daily_goal_xp if user.settings else 20,"goal_just_met":before_today<(user.settings.daily_goal_xp if user.settings else 20)<=after_today,
            "hearts":current_hearts_status(db,user.id)["hearts"],"skill":{"id":state["id"],"state":state["state"],"lessons_completed":state["lessons_completed"],
            "lessons_total":state["lessons_total"],"crowns":state["crowns"]},"skill_just_completed":skill_just,
            "next_skill_unlocked":next_unlocked,"newly_unlocked_achievements":[{"code":a.code,"name":a.name,"description":a.description,"icon":a.icon} for a in new_achievements]}

def abandon(db,user,attempt_id):
    attempt=db.scalar(select(LessonAttempt).where(LessonAttempt.id==attempt_id,LessonAttempt.user_id==user.id))
    if not attempt:api_error(404,"ATTEMPT_NOT_FOUND","Attempt not found.")
    if attempt.status!=AttemptStatus.IN_PROGRESS:api_error(409,"ATTEMPT_NOT_ACTIVE","This lesson attempt is no longer active.")
    attempt.status=AttemptStatus.ABANDONED;attempt.finished_at=now_utc(db)
    return {"status":"ABANDONED"}

def claim_treasure(db,user,skill_id):
    skill=db.get(Skill,skill_id)
    if not skill:api_error(404,"SKILL_NOT_FOUND","Skill not found.")
    if skill.skill_type!=SkillType.TREASURE:api_error(409,"NOT_TREASURE","This skill is not a treasure.")
    state=skill_state(db,user,skill)
    if state["state"]=="LOCKED":api_error(403,"SKILL_LOCKED","This skill is locked.")
    if state["state"]=="COMPLETED":api_error(409,"ALREADY_CLAIMED","This treasure has already been claimed.")
    lesson=skill.lessons[0]
    now=now_utc(db)
    db.add(LessonAttempt(user_id=user.id,lesson_id=lesson.id,status=AttemptStatus.COMPLETED,started_at=now,finished_at=now,xp_earned=0))
    user.gems+=30;db.flush()
    return {"gems_awarded":30,"gems":user.gems}
