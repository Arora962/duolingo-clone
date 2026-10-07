import type { Exercise } from "~/lib/types";
import { formatCountdown } from "~/hooks/useCountdown";

type Props = {
  exercises: Exercise[];
  currentIndex: number;
  solvedCount: number;
  hearts: number;
  maxHearts: number;
  timedSeconds?: number;
  onExit: () => void;
};

function HeartIcon({ filled }: { filled: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={`h-5 w-5 ${filled ? "text-[var(--color-red-text)]" : "text-[var(--color-text-subtle)]"}`}
      fill="currentColor"
      aria-hidden
    >
      <path d="M12 21s-7.2-4.7-9.4-9C.8 8.5 2.4 5 5.8 5c2 0 3.5 1.2 4.2 2.5C10.7 6.2 12.2 5 14.2 5c3.4 0 5 3.5 3.2 7-2.2 4.3-9.4 9-9.4 9Z" />
    </svg>
  );
}

export function LessonProgress({
  exercises,
  currentIndex,
  solvedCount,
  hearts,
  maxHearts,
  timedSeconds,
  onExit,
}: Props) {
  const progress = exercises.length
    ? Math.min(100, Math.round((solvedCount / exercises.length) * 100))
    : 0;

  return (
    <header className="mx-auto flex w-full max-w-3xl items-center gap-3 px-4 py-4 sm:px-6">
      <button
        type="button"
        onClick={onExit}
        aria-label="Exit lesson"
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-2xl font-black text-[var(--color-text-muted)] hover:bg-[var(--color-surface-raised)]"
      >
        ×
      </button>
      <div className="relative h-3 flex-1 overflow-hidden rounded-full bg-[var(--color-border)]">
        <div
          className="relative h-full rounded-full bg-[var(--color-green-text)] transition-all duration-300"
          style={{ width: `${progress}%` }}
          aria-label={`Lesson progress ${progress}%`}
        >
          <span className="absolute inset-x-0 top-0 h-1/2 rounded-full bg-white/25" />
        </div>
      </div>
      {timedSeconds !== undefined && (
        <span className="shrink-0 rounded-xl bg-[var(--color-surface-raised)] px-2 py-1 text-sm font-black text-[var(--color-orange-text,#ff9600)]">
          ⏱ {formatCountdown(timedSeconds)}
        </span>
      )}
      <div className="flex shrink-0 items-center gap-0.5">
        {Array.from({ length: maxHearts }).map((_, index) => (
          <HeartIcon key={index} filled={index < hearts} />
        ))}
      </div>
      <span className="sr-only">
        Exercise {Math.min(currentIndex + 1, exercises.length)} of {exercises.length}; {solvedCount} solved
      </span>
    </header>
  );
}
