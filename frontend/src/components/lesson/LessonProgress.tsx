import type { Exercise } from "~/lib/types";

type Props = {
  exercises: Exercise[];
  currentIndex: number;
  solvedCount: number;
  hearts: number;
  maxHearts: number;
  onExit: () => void;
};

export function LessonProgress({
  exercises,
  currentIndex,
  solvedCount,
  hearts,
  maxHearts,
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
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-2xl font-black text-wolf transition hover:bg-polar active:translate-y-0.5"
      >
        ×
      </button>
      <div className="h-3 flex-1 overflow-hidden rounded-full bg-swan">
        <div
          className="h-full rounded-full bg-feather transition-all duration-300"
          style={{ width: `${progress}%` }}
          aria-label={`Lesson progress ${progress}%`}
        />
      </div>
      <div className="flex shrink-0 items-center gap-1.5 text-sm font-extrabold text-cardinal">
        {Array.from({ length: maxHearts }).map((_, index) => (
          <span key={index} className={index < hearts ? "" : "opacity-25 grayscale"}>
            ❤️
          </span>
        ))}
      </div>
      <span className="sr-only">
        Exercise {Math.min(currentIndex + 1, exercises.length)} of {exercises.length}; {solvedCount} solved
      </span>
    </header>
  );
}
