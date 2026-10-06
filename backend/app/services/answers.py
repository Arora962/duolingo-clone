"""Answer normalization and checking helpers."""

import re

from app.enums import ExerciseType, OptionSide
from app.errors import api_error

_PUNCT = re.compile(r"[.,!?¿¡;:]")


def normalize(text: str) -> str:
    """Normalize answer text for comparison."""
    return " ".join(_PUNCT.sub("", text.strip().lower()).split())


def _option(exercise, option_id):
    return next(
        (option for option in exercise.options if option.id == option_id),
        None,
    )


def check_answer(exercise, payload):
    """Validate and score a submitted answer for an exercise."""
    exercise_type = exercise.type
    option_id = payload.get("option_id")
    option_ids = payload.get("option_ids")
    text = payload.get("text")
    left_id = payload.get("left_option_id")
    right_id = payload.get("right_option_id")

    if exercise_type in (
        ExerciseType.MULTIPLE_CHOICE,
        ExerciseType.FILL_IN_BLANK,
    ) and exercise.options:
        if option_id is None or any(
            value is not None for value in (option_ids, text, left_id, right_id)
        ):
            api_error(
                422,
                "INVALID_ANSWER",
                "This exercise requires exactly one option_id.",
            )
        option = _option(exercise, option_id)
        if option is None:
            api_error(
                422,
                "INVALID_OPTION",
                "The option does not belong to this exercise.",
            )
        correct_answer = next(
            (
                item.text
                for item in exercise.options
                if item.is_correct
            ),
            None,
        )
        return option.is_correct, option.text, correct_answer

    if exercise_type == ExerciseType.FILL_IN_BLANK and not exercise.options:
        if not isinstance(text, str) or any(
            value is not None for value in (option_id, option_ids, left_id, right_id)
        ):
            api_error(422, "INVALID_ANSWER", "This exercise requires text.")
        accepted = exercise.accepted_answers
        correct = any(
            normalize(text) == normalize(answer.answer_text) for answer in accepted
        )
        primary = next(
            (answer.answer_text for answer in accepted if answer.is_primary),
            accepted[0].answer_text if accepted else None,
        )
        return correct, text, primary

    if exercise_type == ExerciseType.TYPE_ANSWER:
        if not isinstance(text, str) or any(
            value is not None for value in (option_id, option_ids, left_id, right_id)
        ):
            api_error(422, "INVALID_ANSWER", "This exercise requires text.")
        correct = any(
            normalize(text) == normalize(answer.answer_text)
            for answer in exercise.accepted_answers
        )
        primary = next(
            (
                answer.answer_text
                for answer in exercise.accepted_answers
                if answer.is_primary
            ),
            None,
        )
        return correct, text, primary

    if exercise_type == ExerciseType.TRANSLATE_WORD_BANK:
        if not isinstance(option_ids, list) or not option_ids or any(
            value is not None for value in (option_id, text, left_id, right_id)
        ):
            api_error(
                422,
                "INVALID_ANSWER",
                "This exercise requires an ordered option_ids array.",
            )
        options = {option.id: option for option in exercise.options}
        if any(option_id not in options for option_id in option_ids) or len(
            set(option_ids)
        ) != len(option_ids):
            api_error(
                422,
                "INVALID_OPTION",
                "Every tile must belong to this exercise and be unique.",
            )
        sentence = " ".join(options[item].text for item in option_ids)
        accepted = any(
            normalize(sentence) == normalize(answer.answer_text)
            for answer in exercise.accepted_answers
        )
        ordered = [
            option.id
            for option in sorted(
                (
                    option
                    for option in exercise.options
                    if option.answer_order is not None
                ),
                key=lambda option: option.answer_order,
            )
        ]
        correct = accepted or option_ids == ordered
        primary = next(
            (
                answer.answer_text
                for answer in exercise.accepted_answers
                if answer.is_primary
            ),
            " ".join(options[item].text for item in ordered) if ordered else None,
        )
        return correct, sentence, primary

    if exercise_type == ExerciseType.MATCH_PAIRS:
        if not isinstance(left_id, int) or not isinstance(right_id, int) or any(
            value is not None for value in (option_id, option_ids, text)
        ):
            api_error(
                422,
                "INVALID_ANSWER",
                "A match submission requires left_option_id and right_option_id.",
            )
        left = _option(exercise, left_id)
        right = _option(exercise, right_id)
        if (
            not left
            or not right
            or left.side != OptionSide.LEFT
            or right.side != OptionSide.RIGHT
        ):
            api_error(
                422,
                "INVALID_OPTION",
                (
                    "Both match options must belong to the exercise and use "
                    "LEFT/RIGHT sides."
                ),
            )
        correct = left.pair_key == right.pair_key
        correct_right = next(
            (
                option
                for option in exercise.options
                if option.side == OptionSide.RIGHT
                and option.pair_key == left.pair_key
            ),
            None,
        )
        feedback = (
            right.text
            if correct
            else correct_right.text
            if correct_right
            else None
        )
        return correct, f"{left.id}:{right.id}", feedback

    api_error(
        422,
        "INVALID_ANSWER",
        "The answer payload does not match the exercise type.",
    )


def solved_exercise_ids(attempt) -> set[int]:
    """Return exercises fully solved by the recorded attempt answers."""
    by_exercise = {}
    for answer in attempt.answers:
        by_exercise.setdefault(answer.exercise_id, []).append(answer)

    solved = set()
    for exercise_id, answers in by_exercise.items():
        exercise = next(
            (answer.exercise for answer in answers if answer.exercise),
            None,
        )
        if exercise and exercise.type == ExerciseType.MATCH_PAIRS:
            pair_keys = {
                option.pair_key
                for option in exercise.options
                if option.pair_key is not None
            }
            matched = set()
            for answer in answers:
                if answer.is_correct and ":" in answer.submitted_answer:
                    try:
                        left_id, right_id = map(
                            int,
                            answer.submitted_answer.split(":", 1),
                        )
                        left = next(
                            option
                            for option in exercise.options
                            if option.id == left_id
                        )
                        right = next(
                            option
                            for option in exercise.options
                            if option.id == right_id
                        )
                        matched.add(
                            left.pair_key
                            if left.pair_key == right.pair_key
                            else None
                        )
                    except (ValueError, StopIteration):
                        pass
            if pair_keys.issubset(matched):
                solved.add(exercise_id)
        elif any(answer.is_correct for answer in answers):
            solved.add(exercise_id)
    return solved


def speak_text_for(exercise, payload, correct_answer):
    """Return text the browser should read aloud after an answer."""
    if exercise.type == ExerciseType.MATCH_PAIRS:
        left = _option(exercise, payload.get("left_option_id"))
        return left.text if left else correct_answer
    return correct_answer
