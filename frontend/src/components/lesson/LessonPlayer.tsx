import { useRouter } from "next/router";
import { useEffect } from "react";
import { ConfirmModal } from "~/components/layout/ConfirmModal";
import { FeedbackBar } from "~/components/lesson/FeedbackBar";
import { FillInBlank } from "~/components/lesson/FillInBlank";
import { CheckBar } from "~/components/lesson/CheckBar";
import { LessonCompleteModal } from "~/components/lesson/LessonCompleteModal";
import { LessonProgress } from "~/components/lesson/LessonProgress";
import { MatchPairs } from "~/components/lesson/MatchPairs";
import { MultipleChoice } from "~/components/lesson/MultipleChoice";
import { OutOfHeartsModal } from "~/components/lesson/OutOfHeartsModal";
import { TimeExpiredModal } from "~/components/lesson/TimeExpiredModal";
import { TypeAnswer } from "~/components/lesson/TypeAnswer";
import { WordBank } from "~/components/lesson/WordBank";
import { useLessonPlayer } from "~/hooks/useLessonPlayer";
import { useCountdown } from "~/hooks/useCountdown";
import { useSettings } from "~/store/useSettings";
import { playAudioOrSpeak } from "~/lib/speech";

export function LessonPlayer({ lessonId }: { lessonId: number }) {
  const router = useRouter();
  const speechEnabled = useSettings(
    (state) => state.settings?.sound_effects_enabled ?? true,
  );
  const player = useLessonPlayer(lessonId);
  const timedSeconds = useCountdown(
    player.lesson?.mode === "TIMED_PRACTICE" ? player.lesson.expires_at : null,
  );

  useEffect(() => {
    if (
      player.lesson?.mode === "TIMED_PRACTICE" &&
      player.phase === "answering" &&
      timedSeconds === 0 &&
      player.lesson.expires_at
    ) {
      // The backend remains authoritative; this only makes the UI respond immediately.
      player.expire();
    }
  }, [player, timedSeconds]);

  if (player.phase === "loading") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--color-background)] px-6">
        <div className="w-full max-w-md text-center">
          <div className="mx-auto h-16 w-16 animate-duo-bounce rounded-full bg-[var(--color-green-text)] shadow-btn-green" />
          <p className="mt-7 text-lg font-black text-[var(--color-text-muted)]">Loading your lesson…</p>
        </div>
      </main>
    );
  }

  if (player.heartsModal) {
    return (
      <OutOfHeartsModal
        hearts={player.heartsModal}
        busy={player.refillBusy}
        onRefillGems={() => void player.refill("GEMS")}
        onPractice={() => void player.refill("PRACTICE")}
        onExit={() => void router.push("/learn")}
      />
    );
  }

  if (player.phase === "error" || !player.lesson || !player.currentExercise) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[var(--color-background)] px-6">
        <div className="w-full max-w-md rounded-3xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-7 text-center shadow-duo-soft">
          <div className="text-5xl">🦉</div>
          <h1 className="mt-3 text-2xl font-black text-[var(--color-text)]">We hit a snag</h1>
          <p className="mt-2 font-bold text-[var(--color-text-muted)]">
            {player.error ?? "This lesson is not available right now."}
          </p>
          <button
            type="button"
            onClick={player.retry}
            className="mt-6 w-full rounded-xl bg-[var(--color-blue-border)] px-6 py-4 text-sm font-black uppercase tracking-wide text-white shadow-btn-blue active:translate-y-1 active:shadow-none"
          >
            Try again
          </button>
          <button
            type="button"
            onClick={() => void router.push("/learn")}
            className="mt-2 w-full rounded-xl px-6 py-3 text-sm font-black uppercase text-[var(--color-text-muted)] hover:bg-[var(--color-surface-raised)]"
          >
            Back to path
          </button>
        </div>
      </main>
    );
  }

  const exercise = player.currentExercise;
  const isMatch = exercise.type === "MATCH_PAIRS";
  const showCheck =
    player.phase === "answering" &&
    !isMatch;

  return (
    <main className="min-h-screen bg-[var(--color-background)] pb-32 text-[var(--color-text)]">
      <LessonProgress
        exercises={player.lesson.exercises}
        currentIndex={player.queueIndex}
        solvedCount={player.solvedCount}
        hearts={player.hearts}
        maxHearts={player.lesson.max_hearts}
        timedSeconds={
          player.lesson.mode === "TIMED_PRACTICE" ? timedSeconds : undefined
        }
        onExit={() => player.setExitOpen(true)}
      />

      <div className="mx-auto w-full max-w-3xl px-5 pb-10 pt-6 sm:px-8 sm:pt-10">
        <div className="mb-8 flex items-start gap-4">
          <div className="hidden sm:block">
            <div className="relative">
              <div className="rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3 text-sm font-extrabold shadow-duo-soft">
                Let’s do this!
              </div>
              <span className="absolute -bottom-2 left-7 h-4 w-4 rotate-45 border-b-2 border-r-2 border-[var(--color-border)] bg-[var(--color-surface)]" />
            </div>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-black uppercase tracking-wider text-[var(--color-text-muted)]">
              {player.lesson.skill.title}
            </p>
            <h1 className="mt-2 text-2xl font-black leading-tight sm:text-3xl">
              {exercise.prompt}
            </h1>
            {(exercise.audio_url || exercise.source_text || exercise.prompt) && (
              <button
                type="button"
                aria-label="Play prompt audio"
                onClick={() =>
                  playAudioOrSpeak(
                    exercise.audio_url,
                    exercise.source_text ?? exercise.prompt,
                    "en-US",
                    speechEnabled,
                  )
                }
                className="mt-3 inline-flex h-11 w-11 items-center justify-center rounded-full border-2 border-[var(--color-blue-border)] bg-[var(--color-blue-surface)] text-xl"
              >
                🔊
              </button>
            )}
          </div>
        </div>

        {exercise.source_text && (
          <div className="mb-7 rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface-raised)] px-5 py-4 text-lg font-extrabold">
            {exercise.source_text}
          </div>
        )}

        <div className="flex justify-center">
          {exercise.type === "MULTIPLE_CHOICE" && (
            <MultipleChoice
              options={exercise.options}
              disabled={player.phase !== "answering"}
              selectedId={player.choiceId}
              onSelect={player.selectChoice}
            />
          )}

          {exercise.type === "FILL_IN_BLANK" && (
            <FillInBlank
              exercise={exercise}
              disabled={player.phase !== "answering"}
              selectedId={player.choiceId}
              typedAnswer={player.typedAnswer}
              onSelect={player.selectChoice}
              onType={player.setTypedAnswer}
            />
          )}

          {exercise.type === "TYPE_ANSWER" && (
            <TypeAnswer
              value={player.typedAnswer}
              disabled={player.phase !== "answering"}
              onChange={player.setTypedAnswer}
            />
          )}

          {exercise.type === "TRANSLATE_WORD_BANK" && (
            <WordBank
              tiles={exercise.tiles}
              selectedIds={player.selectedWords}
              disabled={player.phase !== "answering"}
              onToggle={player.toggleWord}
            />
          )}

          {exercise.type === "MATCH_PAIRS" && (
            <MatchPairs
              left={exercise.left}
              right={exercise.right}
              matchedIds={player.matchedIds}
              shakeIds={player.shakeIds}
              selectedLeft={player.selectedLeft}
              selectedRight={player.selectedRight}
              disabled={player.phase !== "answering"}
              onSelectLeft={player.selectLeft}
              onSelectRight={player.selectRight}
            />
          )}
        </div>
      </div>

      {showCheck && (
        <CheckBar
          ready={player.ready}
          checking={player.phase === "checking"}
          onCheck={player.submitCurrent}
        />
      )}

      {player.feedback && (
        <FeedbackBar
          correct={player.feedback.is_correct}
          correctAnswer={player.feedback.correct_answer}
          speakText={player.feedback.speak_text}
          speakLang={player.feedback.speak_lang}
          speechEnabled={speechEnabled}
          onContinue={() => void player.continueAfterFeedback()}
          finalStep={player.feedback.is_correct && player.feedback.all_exercises_solved}
        />
      )}

      {player.completeResult && (
        <LessonCompleteModal
          result={player.completeResult}
          onContinue={() => void router.push("/learn")}
        />
      )}

      <TimeExpiredModal
        open={player.timeExpired}
        onRetry={player.retry}
        onExit={() => void router.push("/learn")}
      />

      <ConfirmModal
        open={player.exitOpen}
        title="Are you sure you want to quit?"
        description="Your current lesson attempt will be abandoned. You can start it again from the path."
        confirmLabel="Quit"
        cancelLabel="Keep learning"
        onCancel={() => player.setExitOpen(false)}
        onConfirm={() => void player.abandonAndExit()}
      />
    </main>
  );
}
