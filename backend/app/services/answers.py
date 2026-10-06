"""Pure answer normalization/checking plus small DB lookup helpers."""
import re
from app.enums import ExerciseType, OptionSide
from app.errors import api_error
from app.models import ExerciseOption

_PUNCT = re.compile(r"[.,!?¿¡;:]")

def normalize(text: str) -> str:
    return " ".join(_PUNCT.sub("", text.strip().lower()).split())

def _option(exercise, option_id):
    return next((o for o in exercise.options if o.id==option_id),None)

def check_answer(exercise, payload):
    t=exercise.type
    option_id=payload.get("option_id")
    option_ids=payload.get("option_ids")
    text=payload.get("text")
    left_id=payload.get("left_option_id"); right_id=payload.get("right_option_id")
    if t in (ExerciseType.MULTIPLE_CHOICE, ExerciseType.FILL_IN_BLANK) and exercise.options:
        if option_id is None or any(v is not None for v in (option_ids,text,left_id,right_id)):
            api_error(422,"INVALID_ANSWER","This exercise requires exactly one option_id.")
        option=_option(exercise,option_id)
        if option is None: api_error(422,"INVALID_OPTION","The option does not belong to this exercise.")
        return option.is_correct, option.text, option.text if option.is_correct else next((o.text for o in exercise.options if o.is_correct),None)
    if t==ExerciseType.FILL_IN_BLANK and not exercise.options:
        if not isinstance(text,str) or any(v is not None for v in (option_id,option_ids,left_id,right_id)):
            api_error(422,"INVALID_ANSWER","This exercise requires text.")
        accepted=exercise.accepted_answers
        correct=any(normalize(text)==normalize(a.answer_text) for a in accepted)
        primary=next((a.answer_text for a in accepted if a.is_primary), accepted[0].answer_text if accepted else None)
        return correct,text,primary
    if t==ExerciseType.TYPE_ANSWER:
        if not isinstance(text,str) or any(v is not None for v in (option_id,option_ids,left_id,right_id)):
            api_error(422,"INVALID_ANSWER","This exercise requires text.")
        correct=any(normalize(text)==normalize(a.answer_text) for a in exercise.accepted_answers)
        primary=next((a.answer_text for a in exercise.accepted_answers if a.is_primary),None)
        return correct,text,primary
    if t==ExerciseType.TRANSLATE_WORD_BANK:
        if not isinstance(option_ids,list) or not option_ids or any(v is not None for v in (option_id,text,left_id,right_id)):
            api_error(422,"INVALID_ANSWER","This exercise requires an ordered option_ids array.")
        opts={o.id:o for o in exercise.options}
        if any(i not in opts for i in option_ids) or len(set(option_ids))!=len(option_ids):
            api_error(422,"INVALID_OPTION","Every tile must belong to this exercise and be unique.")
        sentence=" ".join(opts[i].text for i in option_ids)
        accepted=any(normalize(sentence)==normalize(a.answer_text) for a in exercise.accepted_answers)
        ordered=[o.id for o in sorted((o for o in exercise.options if o.answer_order is not None),key=lambda o:o.answer_order)]
        correct=accepted or option_ids==ordered
        primary=next((a.answer_text for a in exercise.accepted_answers if a.is_primary), " ".join(opts[i].text for i in ordered) if ordered else None)
        return correct,sentence,primary
    if t==ExerciseType.MATCH_PAIRS:
        if not isinstance(left_id,int) or not isinstance(right_id,int) or any(v is not None for v in (option_id,option_ids,text)):
            api_error(422,"INVALID_ANSWER","A match submission requires left_option_id and right_option_id.")
        left=_option(exercise,left_id); right=_option(exercise,right_id)
        if not left or not right or left.side!=OptionSide.LEFT or right.side!=OptionSide.RIGHT:
            api_error(422,"INVALID_OPTION","Both match options must belong to the exercise and use LEFT/RIGHT sides.")
        correct=left.pair_key==right.pair_key
        correct_right=next((o for o in exercise.options if o.side==OptionSide.RIGHT and o.pair_key==left.pair_key), None)
        feedback=(right.text if correct else (correct_right.text if correct_right else None))
        return correct,f"{left.id}:{right.id}",feedback
    api_error(422,"INVALID_ANSWER","The answer payload does not match the exercise type.")

def solved_exercise_ids(attempt):
    by_exercise={}
    for answer in attempt.answers:
        by_exercise.setdefault(answer.exercise_id,[]).append(answer)
    solved=set()
    for exercise_id,answers in by_exercise.items():
        # Match pairs require every pair key to have a correct recorded pair.
        ex=next((a.exercise for a in answers if a.exercise),None)
        if ex and ex.type==ExerciseType.MATCH_PAIRS:
            pair_keys={o.pair_key for o in ex.options if o.pair_key is not None}
            matched=set()
            for a in answers:
                if a.is_correct and ":" in a.submitted_answer:
                    try:
                        l,r=map(int,a.submitted_answer.split(":",1))
                        lo=next(o for o in ex.options if o.id==l); ro=next(o for o in ex.options if o.id==r)
                        matched.add(lo.pair_key if lo.pair_key==ro.pair_key else None)
                    except (ValueError,StopIteration): pass
            if pair_keys.issubset(matched): solved.add(exercise_id)
        elif any(a.is_correct for a in answers):
            solved.add(exercise_id)
    return solved


def speak_text_for(exercise, payload, correct_answer):
    """Text the browser should read aloud after an answer.

    For MATCH_PAIRS the Spanish word is the LEFT option, while correct_answer is the
    English (right-side) text, so speak the left option instead.
    """
    if exercise.type == ExerciseType.MATCH_PAIRS:
        left = _option(exercise, payload.get("left_option_id"))
        return left.text if left else correct_answer
    return correct_answer
