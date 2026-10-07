import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/router";
import { api, ApiError } from "~/lib/api";
import type { AnswerPayload, AnswerResult, CompleteResult, Exercise, HeartsResponse, StartLessonResponse } from "~/lib/types";
import { useLearner } from "~/store/useLearner";
import { ConfirmModal } from "~/components/layout/ConfirmModal";
import { FeedbackBar } from "~/components/lesson/FeedbackBar";
import { LessonCompleteModal } from "~/components/lesson/LessonCompleteModal";
import { LessonProgress } from "~/components/lesson/LessonProgress";
import { MatchPairs } from "~/components/lesson/MatchPairs";
import { MultipleChoice } from "~/components/lesson/MultipleChoice";
import { OutOfHeartsModal } from "~/components/lesson/OutOfHeartsModal";
import { TypeAnswer } from "~/components/lesson/TypeAnswer";
import { WordBank } from "~/components/lesson/WordBank";

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong.";
}

export function LessonPlayer({ lessonId }: { lessonId: number }) {
  const router = useRouter();
  const patchLearner = useLearner((state) => state.patch);
  const refreshMe = useLearner((state) => state.refresh);
  const [lesson, setLesson] = useState<StartLessonResponse | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [solvedCount, setSolvedCount] = useState(0);
  const [hearts, setHearts] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<AnswerResult | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [completeResult, setCompleteResult] = useState<CompleteResult | null>(null);
  const [heartsModal, setHeartsModal] = useState<HeartsResponse | null>(null);
  const [refillBusy, setRefillBusy] = useState(false);
  const [exitOpen, setExitOpen] = useState(false);
  const [choiceId, setChoiceId] = useState<number | null>(null);
  const [typedAnswer, setTypedAnswer] = useState("");
  const [selectedWords, setSelectedWords] = useState<number[]>([]);
  const [matchedIds, setMatchedIds] = useState<Set<number>>(new Set());
  const [selectedLeft, setSelectedLeft] = useState<number | null>(null);
  const [selectedRight, setSelectedRight] = useState<number | null>(null);
  const startedFor = useRef<number | null>(null);
  const completedRef = useRef(false);
  const abandonRef = useRef<number | null>(null);

  const currentExercise: Exercise | null = lesson?.exercises[currentIndex] ?? null;
  const isMatch = currentExercise?.type === "MATCH_PAIRS";

  const resetExerciseState = useCallback(() => {
    setChoiceId(null);
    setTypedAnswer("");
    setSelectedWords([]);
    setMatchedIds(new Set());
    setSelectedLeft(null);
    setSelectedRight(null);
  }, []);

  const start = useCallback(async () => {
    setLoading(true);
    setError(null);
    setHeartsModal(null);
    setCompleteResult(null);
    completedRef.current = false;
    try {
      const result = await api.startLesson(lessonId);
      setLesson(result);
      setCurrentIndex(0);
      setSolvedCount(0);
      setHearts(result.hearts);
      resetExerciseState();
      startedFor.current = lessonId;
      abandonRef.current = result.attempt_id;
      patchLearner({ hearts: result.hearts, max_hearts: result.max_hearts });
    } catch (e) {
      if (e instanceof ApiError && e.code === "OUT_OF_HEARTS") {
        const heartData = await api.hearts().catch(() => null);
        setHeartsModal(heartData);
      } else {
        setError(getErrorMessage(e));
      }
    } finally {
      setLoading(false);
    }
  }, [lessonId, patchLearner, resetExerciseState]);

  useEffect(() => {
    if (startedFor.current !== lessonId) void start();
  }, [lessonId, start]);

  useEffect(() => {
    return () => {
      const attemptId = abandonRef.current;
      if (attemptId !== null && !completedRef.current) void api.abandon(attemptId).catch(() => undefined);
    };
  }, []);

  useEffect(() => {
    resetExerciseState();
    setFeedback(null);
  }, [currentIndex, resetExerciseState]);

  const submit = useCallback(async (payload: AnswerPayload) => {
    if (!lesson || !currentExercise || submitting || feedback?.is_correct) return;
    setSubmitting(true);
    try {
      const result = await api.answer(lesson.attempt_id, payload);
      setFeedback(result);
      setHearts(result.hearts);
      setSolvedCount(result.solved_exercises);
      patchLearner({ hearts: result.hearts, next_heart_in_seconds: result.next_heart_in_seconds });
      if (result.lesson_failed) {
        const heartData = await api.hearts().catch(() => null);
        setHeartsModal(heartData);
      }
    } catch (e) {
      setError(getErrorMessage(e));
    } finally {
      setSubmitting(false);
    }
  }, [currentExercise, feedback?.is_correct, lesson, patchLearner, submitting]);

  const continueAfterFeedback = useCallback(async () => {
    if (!feedback) return;
    if (!feedback.is_correct) {
      setFeedback(null);
      if (isMatch) {
        setSelectedLeft(null);
        setSelectedRight(null);
      }
      return;
    }
    if (feedback.all_exercises_solved) {
      if (!lesson) return;
      setSubmitting(true);
      try {
        const result = await api.complete(lesson.attempt_id);
        completedRef.current = true;
        abandonRef.current = null;
        setCompleteResult(result);
        patchLearner({
          total_xp: result.total_xp,
          current_streak: result.streak_after,
          xp_today: result.xp_today,
          daily_goal_xp: result.daily_goal_xp,
          daily_goal_met: result.xp_today >= result.daily_goal_xp,
          hearts: result.hearts,
        });
        await refreshMe();
      } catch (e) {
        setError(getErrorMessage(e));
      } finally {
        setSubmitting(false);
      }
      return;
    }
    if (!feedback.exercise_solved) {
      setFeedback(null);
      return;
    }
    setCurrentIndex((index) => Math.min(index + 1, (lesson?.exercises.length ?? 1) - 1));
  }, [feedback, isMatch, lesson, patchLearner, refreshMe]);

  const submitChoice = (id: number) => {
    setChoiceId(id);
    void submit({ exercise_id: currentExercise!.id, option_id: id });
  };

  const submitWords = () => {
    if (!currentExercise || currentExercise.type !== "TRANSLATE_WORD_BANK") return;
    void submit({ exercise_id: currentExercise.id, option_ids: selectedWords });
  };

  const submitTyped = () => {
    if (!currentExercise || (currentExercise.type !== "TYPE_ANSWER" && !(currentExercise.type === "FILL_IN_BLANK" && currentExercise.requires_typing))) return;
    void submit({ exercise_id: currentExercise.id, text: typedAnswer });
  };

  const selectLeft = (id: number) => {
    if (submitting || feedback || matchedIds.has(id)) return;
    setSelectedLeft(id);
    if (selectedRight !== null && currentExercise?.type === "MATCH_PAIRS") {
      void submit({ exercise_id: currentExercise.id, left_option_id: id, right_option_id: selectedRight });
    }
  };

  const selectRight = (id: number) => {
    if (submitting || feedback || matchedIds.has(id)) return;
    setSelectedRight(id);
    if (selectedLeft !== null && currentExercise?.type === "MATCH_PAIRS") {
      void submit({ exercise_id: currentExercise.id, left_option_id: selectedLeft, right_option_id: id });
    }
  };

  useEffect(() => {
    if (!feedback || !isMatch || !feedback.is_correct || !currentExercise || currentExercise.type !== "MATCH_PAIRS") return;
    if (selectedLeft !== null && selectedRight !== null) {
      setMatchedIds((old) => {
        const next = new Set(old);
        next.add(selectedLeft);
        next.add(selectedRight);
        return next;
      });
      setSelectedLeft(null);
      setSelectedRight(null);
    }
  }, [currentExercise, feedback, isMatch, selectedLeft, selectedRight]);

  const refillAndRestart = async () => {
    setRefillBusy(true);
    try {
      const result = await api.refillHearts("GEMS");
      patchLearner({ hearts: result.hearts, gems: result.gems, next_heart_in_seconds: result.next_heart_in_seconds });
      setHearts(result.hearts);
      setHeartsModal(null);
      startedFor.current = null;
      abandonRef.current = null;
      await start();
    } catch (e) {
      setError(getErrorMessage(e));
    } finally {
      setRefillBusy(false);
    }
  };

  const abandonAndExit = async () => {
    const attemptId = abandonRef.current;
    if (attemptId !== null) await api.abandon(attemptId).catch(() => undefined);
    abandonRef.current = null;
    completedRef.current = true;
    router.push("/learn");
  };

  const heading = useMemo(() => {
    if (!currentExercise) return "";
    if (currentExercise.type === "TYPE_ANSWER") return currentExercise.prompt;
    return currentExercise.prompt;
  }, [currentExercise]);

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white px-6">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto h-16 w-16 animate-bounce rounded-full bg-feather shadow-btn-green" />
          <p className="mt-7 text-lg font-black text-wolf">Loading your lesson…</p>
        </div>
      </main>
    );
  }

  if (heartsModal) {
    return <OutOfHeartsModal hearts={heartsModal} busy={refillBusy} onRefill={refillAndRestart} onExit={() => router.push("/learn")} />;
  }

  if (error || !lesson || !currentExercise) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-white px-6">
        <div className="w-full max-w-md rounded-3xl border-2 border-swan bg-white p-7 text-center shadow-sm">
          <div className="text-5xl">🦉</div>
          <h1 className="mt-3 text-2xl font-black text-eel">We hit a snag</h1>
          <p className="mt-2 font-bold text-wolf">{error ?? "This lesson is not available right now."}</p>
          <button onClick={() => void start()} className="mt-6 w-full rounded-xl bg-macaw px-6 py-4 text-sm font-black uppercase tracking-wide text-white shadow-btn-blue active:translate-y-1 active:shadow-none">
            Try again
          </button>
          <button onClick={() => router.push("/learn")} className="mt-2 w-full rounded-xl px-6 py-3 text-sm font-black uppercase text-wolf hover:bg-polar">
            Back to path
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-white pb-40 text-eel">
      <LessonProgress
        exercises={lesson.exercises}
        currentIndex={currentIndex}
        solvedCount={solvedCount}
        hearts={hearts}
        maxHearts={lesson.max_hearts}
        onExit={() => setExitOpen(true)}
      />
      <div className="mx-auto w-full max-w-3xl px-5 pb-10 pt-10 sm:px-8 sm:pt-16">
        <div className="mb-9 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm font-black uppercase tracking-wider text-wolf">{lesson.skill.title}</p>
            <h1 className="mt-2 text-2xl font-black leading-tight sm:text-3xl">{heading}</h1>
          </div>
          {lesson.mode === "TIMED_PRACTICE" && lesson.expires_at && (
            <div className="rounded-xl bg-polar px-3 py-2 text-sm font-black text-fox">⏱ Practice</div>
          )}
        </div>

        {currentExercise.source_text && (
          <div className="mb-7 rounded-2xl bg-polar px-5 py-4 text-lg font-extrabold text-eel">
            {currentExercise.source_text}
          </div>
        )}

        <div className="flex justify-center">
          {currentExercise.type === "MULTIPLE_CHOICE" && (
            <MultipleChoice
              options={currentExercise.options}
              disabled={submitting || feedback !== null}
              selectedId={choiceId}
              onSelect={submitChoice}
            />
          )}
          {currentExercise.type === "FILL_IN_BLANK" && currentExercise.options && (
            <MultipleChoice
              options={currentExercise.options}
              disabled={submitting || feedback !== null}
              selectedId={choiceId}
              onSelect={submitChoice}
            />
          )}
          {currentExercise.type === "FILL_IN_BLANK" && currentExercise.requires_typing && (
            <TypeAnswer
              value={typedAnswer}
              disabled={submitting || feedback !== null}
              onChange={setTypedAnswer}
              onSubmit={submitTyped}
            />
          )}
          {currentExercise.type === "TYPE_ANSWER" && (
            <TypeAnswer
              value={typedAnswer}
              disabled={submitting || feedback !== null}
              onChange={setTypedAnswer}
              onSubmit={submitTyped}
            />
          )}
          {currentExercise.type === "TRANSLATE_WORD_BANK" && (
            <WordBank
              tiles={currentExercise.tiles}
              selectedIds={selectedWords}
              disabled={submitting || feedback !== null}
              onToggle={(id) => setSelectedWords((ids) => ids.includes(id) ? ids.filter((item) => item !== id) : [...ids, id])}
              onSubmit={submitWords}
            />
          )}
          {currentExercise.type === "MATCH_PAIRS" && (
            <MatchPairs
              left={currentExercise.left}
              right={currentExercise.right}
              matchedIds={matchedIds}
              selectedLeft={selectedLeft}
              selectedRight={selectedRight}
              disabled={submitting || feedback !== null}
              onSelectLeft={selectLeft}
              onSelectRight={selectRight}
            />
          )}
        </div>
      </div>

      {feedback && (
        <FeedbackBar
          correct={feedback.is_correct}
          correctAnswer={feedback.correct_answer}
          speakText={feedback.speak_text}
          onContinue={continueAfterFeedback}
          onRetry={() => {
            setFeedback(null);
            setChoiceId(null);
            if (isMatch) {
              setSelectedLeft(null);
              setSelectedRight(null);
            }
          }}
          finalStep={feedback.is_correct && feedback.all_exercises_solved}
        />
      )}

      {completeResult && (
        <LessonCompleteModal result={completeResult} onContinue={() => router.push("/learn")} />
      )}

      <ConfirmModal
        open={exitOpen}
        title="Leave this lesson?"
        description="Your current lesson attempt will be abandoned. You can start it again from the path."
        confirmLabel="Leave lesson"
        onCancel={() => setExitOpen(false)}
        onConfirm={() => void abandonAndExit()}
      />
    </main>
  );
}
