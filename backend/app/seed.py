"""Idempotent database seeding: python -m app.seed."""
from copy import deepcopy
from datetime import timedelta
from sqlalchemy import select
from app.clock import now_utc
from app.database import Base,SessionLocal,engine
from app.enums import AchievementMetric,AttemptStatus,ExerciseType,HeartEventType,OptionSide,SkillIcon,SkillType
from app.models import Achievement,AttemptAnswer,Course,Exercise,ExerciseAcceptedAnswer,ExerciseOption,HeartEvent,Lesson,LessonAttempt,Skill,SystemSetting,Unit,User,UserAchievement,UserSettings
from app.seed_data import ACHIEVEMENTS,COURSE,UNITS

def _enum(cls,value): return cls[value]
def _get_or_create(db,model,where,values):
    obj=db.scalar(select(model).filter_by(**where))
    if obj is None:
        obj=model(**where,**values);db.add(obj);db.flush()
    return obj

def _practice_exercises(unit_data):
    source=None
    for s in unit_data["skills"]:
        if s["skill_type"]==SkillType.LESSON.value and s["lessons"]:
            source=s["lessons"][0]["exercises"];break
    if not source:return []
    copied=deepcopy(source[:5])
    if len(copied)<5:return copied
    sixth=deepcopy(copied[0]); sixth["prompt"]="Practice: choose the correct Spanish greeting."; copied.append(sixth)
    return copied

def _seed_content(db):
    course=_get_or_create(db,Course,{"language_code":COURSE["language_code"]},{k:v for k,v in COURSE.items() if k!="language_code"})
    lessons_by_skill=[]
    for unit_data in UNITS:
        unit=_get_or_create(db,Unit,{"course_id":course.id,"position":unit_data["position"]},{k:v for k,v in unit_data.items() if k not in {"position","skills"}})
        for skill_data in unit_data["skills"]:
            skill=_get_or_create(db,Skill,{"unit_id":unit.id,"position":skill_data["position"]},{"title":skill_data["title"],"skill_type":_enum(SkillType,skill_data["skill_type"]),"icon_type":_enum(SkillIcon,skill_data["icon_type"])})
            lesson_specs=deepcopy(skill_data["lessons"])
            if skill.skill_type==SkillType.TREASURE and not lesson_specs:
                lesson_specs=[{"position":1,"xp_reward":0,"exercises":[]}]
            elif skill.skill_type==SkillType.PRACTICE and not lesson_specs:
                lesson_specs=[{"position":1,"xp_reward":20,"exercises":_practice_exercises(unit_data)}]
            for lesson_data in lesson_specs:
                lesson=_get_or_create(db,Lesson,{"skill_id":skill.id,"position":lesson_data["position"]},{"xp_reward":lesson_data["xp_reward"]})
                lessons_by_skill.append((skill.position,skill,lesson))
                for position,exercise_data in enumerate(lesson_data["exercises"],1):
                    exercise=_get_or_create(db,Exercise,{"lesson_id":lesson.id,"position":position},{
                        "type":_enum(ExerciseType,exercise_data["type"]),"prompt":exercise_data["prompt"],
                        "source_text":exercise_data.get("source_text"),"hint":exercise_data.get("hint"),
                        "audio_url":exercise_data.get("audio_url") or ("/static/audio/hola.mp3" if position==1 and exercise_data["type"]=="MULTIPLE_CHOICE" else None)})
                    if exercise_data["type"] in {"MULTIPLE_CHOICE","FILL_IN_BLANK"}:
                        for option_position,(text,is_correct) in enumerate(exercise_data["options"],1):
                            _get_or_create(db,ExerciseOption,{"exercise_id":exercise.id,"position":option_position},{"text":text,"is_correct":is_correct})
                    elif exercise_data["type"]=="TRANSLATE_WORD_BANK":
                        for option_position,option in enumerate(exercise_data["options"],1):
                            text,_unused,answer_order=option
                            _get_or_create(db,ExerciseOption,{"exercise_id":exercise.id,"position":option_position},{"text":text,"is_correct":False,"answer_order":answer_order})
                    elif exercise_data["type"]=="MATCH_PAIRS":
                        pos=1
                        for pair_number,(left,right) in enumerate(exercise_data["pairs"],1):
                            for text,side in ((left,OptionSide.LEFT),(right,OptionSide.RIGHT)):
                                _get_or_create(db,ExerciseOption,{"exercise_id":exercise.id,"position":pos},{"text":text,"is_correct":False,"pair_key":str(pair_number),"side":side});pos+=1
                    for answer in exercise_data.get("answers",[]):
                        _get_or_create(db,ExerciseAcceptedAnswer,{"exercise_id":exercise.id,"answer_text":answer},{"is_primary":answer==exercise_data["answers"][0]})
    return course,lessons_by_skill

def _ensure_user(db,course,username,display_name,gems=0,is_seeded_bot=False):
    user=_get_or_create(db,User,{"username":username},{"display_name":display_name,"gems":gems,"is_seeded_bot":is_seeded_bot,"current_course_id":course.id})
    if user.current_course_id is None:user.current_course_id=course.id
    if user.settings is None:
        db.add(UserSettings(user_id=user.id));db.flush()
    # The relationship is lazy-loaded; refresh the one-to-one after creation.
    user.settings = db.get(UserSettings, user.id)
    return user

def _add_correct_answers(db,attempt,lesson,when,with_one_retry=False):
    for ex in sorted(lesson.exercises,key=lambda x:x.position):
        if ex.type in {ExerciseType.MULTIPLE_CHOICE,ExerciseType.FILL_IN_BLANK} and ex.options:
            correct=next(o for o in ex.options if o.is_correct)
            if with_one_retry and ex.position==1:
                db.add(AttemptAnswer(attempt_id=attempt.id,exercise_id=ex.id,submitted_answer="wrong answer",is_correct=False,answered_at=when-timedelta(seconds=40)))
            db.add(AttemptAnswer(attempt_id=attempt.id,exercise_id=ex.id,submitted_answer=correct.text,is_correct=True,answered_at=when-timedelta(seconds=30)))
        elif ex.type==ExerciseType.TYPE_ANSWER:
            answer=next(a for a in ex.accepted_answers if a.is_primary)
            db.add(AttemptAnswer(attempt_id=attempt.id,exercise_id=ex.id,submitted_answer=answer.answer_text,is_correct=True,answered_at=when-timedelta(seconds=30)))
        elif ex.type==ExerciseType.TRANSLATE_WORD_BANK:
            tiles=sorted((o for o in ex.options if o.answer_order is not None),key=lambda o:o.answer_order)
            db.add(AttemptAnswer(attempt_id=attempt.id,exercise_id=ex.id,submitted_answer=" ".join(o.text for o in tiles),is_correct=True,answered_at=when-timedelta(seconds=30)))
        elif ex.type==ExerciseType.MATCH_PAIRS:
            lefts={o.pair_key:o for o in ex.options if o.side==OptionSide.LEFT}
            rights={o.pair_key:o for o in ex.options if o.side==OptionSide.RIGHT}
            for key,left in lefts.items():
                right=rights[key]
                db.add(AttemptAnswer(attempt_id=attempt.id,exercise_id=ex.id,submitted_answer=f"{left.id}:{right.id}",is_correct=True,answered_at=when-timedelta(seconds=30)))

def _completed_attempt(db,user,lesson,when,with_one_retry=False):
    existing=db.scalar(select(LessonAttempt).where(LessonAttempt.user_id==user.id,LessonAttempt.lesson_id==lesson.id,LessonAttempt.finished_at==when))
    if existing:return existing
    attempt=LessonAttempt(user_id=user.id,lesson_id=lesson.id,status=AttemptStatus.COMPLETED,started_at=when-timedelta(minutes=5),finished_at=when,xp_earned=lesson.xp_reward)
    db.add(attempt);db.flush();_add_correct_answers(db,attempt,lesson,when,with_one_retry);return attempt

def _seed_learner_progress(db,learner,lesson_groups):
    if db.scalar(select(LessonAttempt.id).where(LessonAttempt.user_id==learner.id,LessonAttempt.status==AttemptStatus.COMPLETED)) is not None:return
    first=[l for _,s,l in lesson_groups if s.unit.position==1 and s.position==1]
    second=[l for _,s,l in lesson_groups if s.unit.position==1 and s.position==2]
    current=now_utc(db); today=current.replace(hour=12,minute=0,second=0,microsecond=0)
    day0=today-timedelta(days=2);day1=today-timedelta(days=1);day2=today
    _completed_attempt(db,learner,first[0],day0)
    _completed_attempt(db,learner,first[1],day0+timedelta(minutes=20))
    _completed_attempt(db,learner,second[0],day1,with_one_retry=True)
    for i in range(7):
        _completed_attempt(db,learner,first[i%2],day2-timedelta(minutes=i+1))
    _completed_attempt(db,learner,second[0],day2)
    db.add(HeartEvent(user_id=learner.id,event_type=HeartEventType.LOST,delta=-1,created_at=current-timedelta(minutes=10)))

def _seed_bots(db,course,lessons):
    for bot_index in range(1,11):
        bot=_ensure_user(db,course,f"bot{bot_index}",f"Learner Bot {bot_index}",gems=100+bot_index,is_seeded_bot=True)
        if db.scalar(select(LessonAttempt.id).where(LessonAttempt.user_id==bot.id,LessonAttempt.status==AttemptStatus.COMPLETED)) is not None:continue
        now=now_utc(db).replace(hour=14,minute=0,second=0,microsecond=0)
        for day_offset in range(0,min(4,1+bot_index%4)):
            _completed_attempt(db,bot,lessons[(bot_index+day_offset)%len(lessons)],now-timedelta(days=day_offset,hours=bot_index),with_one_retry=False)

def _seed_achievements(db,learner):
    for data in ACHIEVEMENTS:
        _get_or_create(db,Achievement,{"code":data["code"]},{"name":data["name"],"description":data["description"],"icon":data["icon"],"metric":_enum(AchievementMetric,data["metric"]),"threshold":data["threshold"]})
    from app.services.achievements import evaluate
    evaluate(db,learner.id)

def seed():
    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as db:
        setting=db.get(SystemSetting,"time_offset_days")
        if setting is None:db.add(SystemSetting(key="time_offset_days",value="0",updated_at=now_utc(db)))
        course,groups=_seed_content(db)
        learner=_ensure_user(db,course,"learner","Learner",gems=500)
        learner.settings.daily_goal_xp=20
        _seed_learner_progress(db,learner,groups)
        lessons=[lesson for _,_,lesson in groups if lesson.exercises or lesson.xp_reward>0]
        _seed_bots(db,course,lessons)
        _seed_achievements(db,learner)

if __name__=="__main__":seed()
