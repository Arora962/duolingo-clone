import { useMemo } from "react";
import { Button3D } from "~/components/ui/Button3D";
import { playAudioOrSpeak } from "~/lib/speech";

const PRAISE = ["Nicely done!", "Great job!", "Excellent!", "You got it!"];

type Props = {
  correct: boolean;
  correctAnswer: string | null;
  speakText: string | null;
  speakLang: string | null;
  speechEnabled: boolean;
  onContinue: () => void;
  finalStep?: boolean;
};

export function FeedbackBar({
  correct,
  correctAnswer,
  speakText,
  speakLang,
  speechEnabled,
  onContinue,
  finalStep = false,
}: Props) {
  const praise = useMemo(
    () => PRAISE[Math.floor(Math.random() * PRAISE.length)],
    [],
  );

  return (
    <div
      className={[
        "animate-duo-slide-up fixed inset-x-0 bottom-0 z-50 border-t-2 px-4",
        "pb-[max(1rem,env(safe-area-inset-bottom))] pt-3 shadow-[0_-4px_18px_rgba(0,0,0,0.08)]",
        correct
          ? "border-[var(--color-green-text)] bg-[var(--color-green-surface)]"
          : "border-[var(--color-red-text)] bg-[var(--color-red-surface)]",
      ].join(" ")}
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <div
            className={[
              "mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xl font-black text-white",
              correct ? "bg-[var(--color-green-text)]" : "bg-[var(--color-red-text)]",
            ].join(" ")}
          >
            {correct ? "✓" : "×"}
          </div>
          <div>
            <p
              className={[
                "text-xl font-black",
                correct ? "text-[var(--color-green-text)]" : "text-[var(--color-red-text)]",
              ].join(" ")}
            >
              {correct ? praise : "Not quite"}
            </p>
            {!correct && correctAnswer && (
              <p className="mt-0.5 text-sm font-extrabold text-[var(--color-text)]">
                Correct answer: <span className="font-black">{correctAnswer}</span>
              </p>
            )}
            {correct && speakText && (
              <button
                type="button"
                onClick={() =>
                  playAudioOrSpeak(speakText, speakText, speakLang, speechEnabled)
                }
                className="mt-0.5 text-sm font-extrabold text-[var(--color-text)] underline"
              >
                🔊 Hear it again
              </button>
            )}
          </div>
        </div>

        <Button3D
          tone={correct ? "green" : "red"}
          className="min-w-[150px]"
          onClick={onContinue}
        >
          {correct ? (finalStep ? "Finish" : "Continue") : "Continue"}
        </Button3D>
      </div>
    </div>
  );
}
