import { useCallback, useEffect, useMemo, useReducer, useRef } from "react";
import { useRouter } from "next/router";
import { api, ApiError } from "~/lib/api";
import type {
  AnswerPayload,
  AnswerResult,
  CompleteResult,
  Exercise,
  HeartsResponse,
  StartLessonResponse,
} from "~/lib/types";
import { useLearner } from "~/store/useLearner";
import { useSettings } from "~/store/useSettings";
import { useToast } from "~/store/useToast";
import { playCompleteSound, playCorrectSound, playWrongSound } from "~/lib/sound";
import { playAudioOrSpeak } from "~/lib/speech";

export type LessonPhase =
  | "loading"
  | "error"
  | "answering"
  | "checking"
  | "feedback"
  | "failed"
  | "completing"
  | "complete";

type State = {
  phase: LessonPhase;
  lesson: StartLessonResponse | null;
  queue: number[];
  queueIndex: number;
  solvedCount: number;
  hearts: number;
  feedback: AnswerResult | null;
  completeResult: CompleteResult | null;
  heartsModal: HeartsResponse | null;
  error: string | null;
  timeExpired: boolean;
  exitOpen: boolean;
  choiceId: number | null;
  typedAnswer: string;
  selectedWords: number[];
  matchedIds: Set<number>;
  shakeIds: Set<number>;
  selectedLeft: number | null;
  selectedRight: number | null;
  refillBusy: boolean;
};

const initialState: State = {
  phase: "loading",
  lesson: null,
  queue: [],
  queueIndex: 0,
  solvedCount: 0,
  hearts: 0,
  feedback: null,
  completeResult: null,
  heartsModal: null,
  error: null,
  timeExpired: false,
  exitOpen: false,
  choiceId: null,
  typedAnswer: "",
  selectedWords: [],
  matchedIds: new Set(),
  shakeIds: new Set(),
  selectedLeft: null,
  selectedRight: null,
  refillBusy: false,
};

type Action =
  | { type: "START"; lesson: StartLessonResponse }
  | { type: "ERROR"; message: string }
  | { type: "SET_PHASE"; phase: LessonPhase }
  | { type: "SELECT_CHOICE"; id: number }
  | { type: "SET_TYPED"; value: string }
  | { type: "TOGGLE_WORD"; id: number }
  | { type: "SELECT_LEFT"; id: number }
  | { type: "SELECT_RIGHT"; id: number }
  | { type: "CHECKING" }
  | { type: "ANSWERED"; result: AnswerResult }
  | { type: "MATCHED"; ids: [number, number] }
  | { type: "SHAKE"; ids: [number, number] }
  | { type: "CLEAR_SHAKE" }
  | { type: "CONTINUE" }
  | { type: "COMPLETE_START" }
  | { type: "COMPLETED"; result: CompleteResult }
  | { type: "FAILED"; hearts: HeartsResponse | null }
  | { type: "TIME_EXPIRED" }
  | { type: "SET_HEARTS_MODAL"; value: HeartsResponse | null }
  | { type: "SET_EXIT"; value: boolean }
  | { type: "SET_REFILL_BUSY"; value: boolean }
  | { type: "RESET_ATTEMPT"; lesson: StartLessonResponse };

function resetAnswerState(state: State): State {
  return {
    ...state,
    feedback: null,
    choiceId: null,
    typedAnswer: "",
    selectedWords: [],
    matchedIds: new Set(),
    shakeIds: new Set(),
    selectedLeft: null,
    selectedRight: null,
  };
}

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "START": {
      const queue = action.lesson.exercises.map((exercise) => exercise.id);
      return {
        ...resetAnswerState(state),
        phase: "answering",
        lesson: action.lesson,
        queue,
        queueIndex: 0,
        solvedCount: 0,
        hearts: action.lesson.hearts,
        completeResult: null,
        heartsModal: null,
        error: null,
        timeExpired: false,
        exitOpen: false,
      };
    }
    case "RESET_ATTEMPT":
      return reducer(state, { type: "START", lesson: action.lesson });
    case "ERROR":
      return { ...state, phase: "error", error: action.message };
    case "SET_PHASE":
      return { ...state, phase: action.phase };
    case "SELECT_CHOICE":
      return { ...state, choiceId: action.id };
    case "SET_TYPED":
      return { ...state, typedAnswer: action.value };
    case "TOGGLE_WORD":
      return {
        ...state,
        selectedWords: state.selectedWords.includes(action.id)
          ? state.selectedWords.filter((id) => id !== action.id)
          : [...state.selectedWords, action.id],
      };
    case "SELECT_LEFT":
      return { ...state, selectedLeft: action.id };
    case "SELECT_RIGHT":
      return { ...state, selectedRight: action.id };
    case "CHECKING":
      return { ...state, phase: "checking" };
    case "ANSWERED":
      return {
        ...state,
        phase: action.result.lesson_failed ? "failed" : "feedback",
        feedback: action.result.lesson_failed ? null : action.result,
        hearts: action.result.hearts,
        solvedCount: action.result.solved_exercises,
      };
    case "MATCHED": {
      const next = new Set(state.matchedIds);
      next.add(action.ids[0]);
      next.add(action.ids[1]);
      return {
        ...state,
        phase: "answering",
        feedback: null,
        matchedIds: next,
        selectedLeft: null,
        selectedRight: null,
      };
    }
    case "SHAKE":
      return {
        ...state,
        phase: "answering",
        feedback: null,
        shakeIds: new Set(action.ids),
        selectedLeft: null,
        selectedRight: null,
      };
    case "CLEAR_SHAKE":
      return { ...state, shakeIds: new Set() };
    case "CONTINUE": {
      const feedback = state.feedback;
      if (!feedback) return state;
      if (feedback.all_exercises_solved) return state;
      const currentId = state.queue[state.queueIndex];
      const queue =
        feedback.exercise_solved || !currentId
          ? state.queue
          : [...state.queue, currentId];
      return {
        ...resetAnswerState(state),
        phase: "answering",
        queue,
        queueIndex: state.queueIndex + 1,
      };
    }
    case "COMPLETE_START":
      return { ...state, phase: "completing" };
    case "COMPLETED":
      return {
        ...state,
        phase: "complete",
        completeResult: action.result,
        feedback: null,
      };
    case "FAILED":
      return {
        ...state,
        phase: "failed",
        heartsModal: action.hearts,
        feedback: null,
      };
    case "TIME_EXPIRED":
      return { ...state, phase: "failed", timeExpired: true, feedback: null };
    case "SET_HEARTS_MODAL":
      return { ...state, heartsModal: action.value };
    case "SET_EXIT":
      return { ...state, exitOpen: action.value };
    case "SET_REFILL_BUSY":
      return { ...state, refillBusy: action.value };
    default:
      return state;
  }
}

function messageFor(error: unknown): string {
  return error instanceof Error ? error.message : "Something went wrong.";
}

export function useLessonPlayer(lessonId: number) {
  const router = useRouter();
  const [state, dispatch] = useReducer(reducer, initialState);
  const startedFor = useRef<number | null>(null);
  const abandonRef = useRef<number | null>(null);
  const completedRef = useRef(false);
  const shakeTimer = useRef<number | null>(null);

  const patchLearner = useLearner((item) => item.patch);
  const refreshMe = useLearner((item) => item.refresh);
  const soundEnabled = useSettings((item) => item.settings?.sound_effects_enabled ?? true);
  const speechEnabled = soundEnabled;
  const pushToast = useToast((item) => item.push);

  const currentExercise = useMemo<Exercise | null>(() => {
    if (!state.lesson || state.queue.length === 0) return null;
    const id = state.queue[state.queueIndex];
    return state.lesson.exercises.find((exercise) => exercise.id === id) ?? null;
  }, [state.lesson, state.queue, state.queueIndex]);

  const start = useCallback(async () => {
    startedFor.current = lessonId;
    completedRef.current = false;
    dispatch({ type: "SET_PHASE", phase: "loading" });
    try {
      const lesson = await api.startLesson(lessonId);
      abandonRef.current = lesson.attempt_id;
      dispatch({ type: "START", lesson });
      patchLearner({ hearts: lesson.hearts, max_hearts: lesson.max_hearts });
    } catch (error) {
      startedFor.current = null;
      if (error instanceof ApiError && error.code === "OUT_OF_HEARTS") {
        const hearts = await api.hearts().catch(() => null);
        dispatch({ type: "FAILED", hearts });
      } else {
        dispatch({ type: "ERROR", message: messageFor(error) });
      }
    }
  }, [lessonId, patchLearner]);

  useEffect(() => {
    if (startedFor.current !== lessonId) void start();
  }, [lessonId, start]);

  useEffect(() => {
    return () => {
      const attemptId = abandonRef.current;
      if (attemptId !== null && !completedRef.current) {
        void api.abandon(attemptId).catch(() => undefined);
      }
      if (shakeTimer.current !== null) window.clearTimeout(shakeTimer.current);
    };
  }, []);

  const handleAnswerError = useCallback(
    (error: unknown) => {
      if (error instanceof ApiError && error.code === "TIME_EXPIRED") {
        dispatch({ type: "TIME_EXPIRED" });
        return;
      }
      if (error instanceof ApiError && error.code === "ATTEMPT_NOT_ACTIVE") {
        pushToast("This lesson attempt is no longer active.", "warning");
        router.push("/learn");
        return;
      }
      if (error instanceof ApiError && error.code === "NETWORK_ERROR") {
        dispatch({ type: "SET_PHASE", phase: "answering" });
        pushToast("Connection problem. Check your connection and try again.", "error");
        return;
      }
      dispatch({ type: "ERROR", message: messageFor(error) });
    },
    [pushToast, router],
  );

  const submit = useCallback(
    async (payload: AnswerPayload) => {
      if (!state.lesson || !currentExercise || state.phase !== "answering") return;
      dispatch({ type: "CHECKING" });
      try {
        const result = await api.answer(state.lesson.attempt_id, payload);
        patchLearner({
          hearts: result.hearts,
          next_heart_in_seconds: result.next_heart_in_seconds,
        });
        if (result.lesson_failed) {
          const hearts = await api.hearts().catch(() => null);
          dispatch({ type: "FAILED", hearts });
          return;
        }
        dispatch({ type: "ANSWERED", result });
        if (result.is_correct) {
          playCorrectSound(soundEnabled);
          playAudioOrSpeak(result.audio_url, result.speak_text, result.speak_lang, speechEnabled);
        } else {
          playWrongSound(soundEnabled);
        }
      } catch (error) {
        handleAnswerError(error);
      }
    },
    [currentExercise, handleAnswerError, patchLearner, soundEnabled, speechEnabled, state.lesson, state.phase],
  );

  const submitCurrent = useCallback(() => {
    if (!currentExercise) return;

    if (currentExercise.type === "MULTIPLE_CHOICE" || (
      currentExercise.type === "FILL_IN_BLANK" && currentExercise.options
    )) {
      if (state.choiceId === null) return;
      void submit({ exercise_id: currentExercise.id, option_id: state.choiceId });
      return;
    }

    if (
      currentExercise.type === "TYPE_ANSWER" ||
      (currentExercise.type === "FILL_IN_BLANK" && currentExercise.requires_typing)
    ) {
      if (!state.typedAnswer.trim()) return;
      void submit({ exercise_id: currentExercise.id, text: state.typedAnswer.trim() });
      return;
    }

    if (currentExercise.type === "TRANSLATE_WORD_BANK") {
      if (!state.selectedWords.length) return;
      void submit({ exercise_id: currentExercise.id, option_ids: state.selectedWords });
    }
  }, [currentExercise, state.choiceId, state.selectedWords, state.typedAnswer, submit]);

  const selectLeft = useCallback(
    (id: number) => {
      if (state.phase !== "answering" || currentExercise?.type !== "MATCH_PAIRS" || state.matchedIds.has(id)) return;
      const other = state.selectedRight;
      dispatch({ type: "SELECT_LEFT", id });
      if (other !== null) {
        void submit({ exercise_id: currentExercise.id, left_option_id: id, right_option_id: other }).then(() => undefined);
      }
    },
    [currentExercise, state.matchedIds, state.phase, state.selectedRight, submit],
  );

  const selectRight = useCallback(
    (id: number) => {
      if (state.phase !== "answering" || currentExercise?.type !== "MATCH_PAIRS" || state.matchedIds.has(id)) return;
      const other = state.selectedLeft;
      dispatch({ type: "SELECT_RIGHT", id });
      if (other !== null) {
        void submit({ exercise_id: currentExercise.id, left_option_id: other, right_option_id: id });
      }
    },
    [currentExercise, state.matchedIds, state.phase, state.selectedLeft, submit],
  );

  // Match-pair responses need different UI semantics than normal answer feedback.
  useEffect(() => {
    if (
      !state.feedback ||
      currentExercise?.type !== "MATCH_PAIRS" ||
      state.phase !== "feedback"
    ) return;

    const feedback = state.feedback;
    const left = state.selectedLeft;
    const right = state.selectedRight;
    if (feedback.is_correct && left !== null && right !== null) {
      if (feedback.exercise_solved) {
        return;
      }
      dispatch({ type: "MATCHED", ids: [left, right] });
      return;
    }

    if (!feedback.is_correct && left !== null && right !== null) {
      dispatch({ type: "SHAKE", ids: [left, right] });
      shakeTimer.current = window.setTimeout(() => dispatch({ type: "CLEAR_SHAKE" }), 360);
    }
  }, [currentExercise, state.feedback, state.phase, state.selectedLeft, state.selectedRight]);

  const continueAfterFeedback = useCallback(async () => {
    if (!state.feedback) return;

    if (state.feedback.all_exercises_solved) {
      if (!state.lesson) return;
      dispatch({ type: "COMPLETE_START" });
      try {
        const result = await api.complete(state.lesson.attempt_id);
        completedRef.current = true;
        abandonRef.current = null;
        patchLearner({
          total_xp: result.total_xp,
          current_streak: result.streak_after,
          xp_today: result.xp_today,
          daily_goal_xp: result.daily_goal_xp,
          daily_goal_met: result.xp_today >= result.daily_goal_xp,
          hearts: result.hearts,
        });
        await refreshMe();
        playCompleteSound(soundEnabled);
        dispatch({ type: "COMPLETED", result });
      } catch (error) {
        if (error instanceof ApiError && error.code === "TIME_EXPIRED") {
          dispatch({ type: "TIME_EXPIRED" });
        } else if (error instanceof ApiError && error.code === "ATTEMPT_NOT_ACTIVE") {
          pushToast("This lesson attempt is no longer active.", "warning");
          router.push("/learn");
        } else if (error instanceof ApiError && error.code === "NETWORK_ERROR") {
          dispatch({ type: "SET_PHASE", phase: "feedback" });
          pushToast("Connection problem. Try completing the lesson again.", "error");
        } else {
          dispatch({ type: "ERROR", message: messageFor(error) });
        }
      }
      return;
    }

    dispatch({ type: "CONTINUE" });
  }, [patchLearner, pushToast, refreshMe, router, soundEnabled, state.feedback, state.lesson]);

  const refill = useCallback(
    async (method: "GEMS" | "PRACTICE") => {
      dispatch({ type: "SET_REFILL_BUSY", value: true });
      try {
        const result = await api.refillHearts(method);
        patchLearner({
          hearts: result.hearts,
          gems: result.gems,
          next_heart_in_seconds: result.next_heart_in_seconds,
        });
        dispatch({ type: "SET_HEARTS_MODAL", value: null });
        startedFor.current = null;
        abandonRef.current = null;
        await start();
      } catch (error) {
        pushToast(messageFor(error), "error");
      } finally {
        dispatch({ type: "SET_REFILL_BUSY", value: false });
      }
    },
    [patchLearner, pushToast, start],
  );

  const abandonAndExit = useCallback(async () => {
    const attemptId = abandonRef.current;
    if (attemptId !== null) await api.abandon(attemptId).catch(() => undefined);
    abandonRef.current = null;
    completedRef.current = true;
    await router.push("/learn");
  }, [router]);

  const retry = useCallback(() => {
    const oldAttempt = abandonRef.current;
    abandonRef.current = null;
    completedRef.current = true;
    dispatch({ type: "SET_HEARTS_MODAL", value: null });
    startedFor.current = null;
    void (async () => {
      if (oldAttempt !== null) {
        await api.abandon(oldAttempt).catch(() => undefined);
      }
      completedRef.current = false;
      await start();
    })();
  }, [start]);

  const retryCurrent = useCallback(() => {
    dispatch({ type: "SET_PHASE", phase: "answering" });
  }, []);

  const expire = useCallback(() => {
    if (state.phase === "answering" || state.phase === "checking") {
      dispatch({ type: "TIME_EXPIRED" });
    }
  }, [state.phase]);

  const setExitOpen = useCallback((open: boolean) => {
    dispatch({ type: "SET_EXIT", value: open });
  }, []);

  const ready =
    currentExercise?.type === "MULTIPLE_CHOICE"
      ? state.choiceId !== null
      : currentExercise?.type === "FILL_IN_BLANK"
        ? currentExercise.requires_typing
          ? Boolean(state.typedAnswer.trim())
          : state.choiceId !== null
        : currentExercise?.type === "TYPE_ANSWER"
          ? Boolean(state.typedAnswer.trim())
          : currentExercise?.type === "TRANSLATE_WORD_BANK"
            ? state.selectedWords.length > 0
            : false;

  return {
    ...state,
    currentExercise,
    ready,
    submitCurrent,
    continueAfterFeedback,
    selectLeft,
    selectRight,
    refill,
    retry,
    retryCurrent,
    expire,
    abandonAndExit,
    setExitOpen,
    selectChoice: (id: number) => dispatch({ type: "SELECT_CHOICE", id }),
    setTypedAnswer: (value: string) => dispatch({ type: "SET_TYPED", value }),
    toggleWord: (id: number) => dispatch({ type: "TOGGLE_WORD", id }),
  };
}
