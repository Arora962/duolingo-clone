type Props = {
  correct: boolean;
  correctAnswer: string | null;
  speakText: string | null;
  onContinue: () => void;
  onRetry?: () => void;
  finalStep?: boolean;
};

export function FeedbackBar({
  correct,
  correctAnswer,
  speakText,
  onContinue,
  onRetry,
  finalStep = false,
}: Props) {
  const speak = () => {
    if (typeof window === "undefined" || !speakText || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(new SpeechSynthesisUtterance(speakText));
  };

  return (
    <div
      className={`fixed inset-x-0 bottom-0 z-50 border-t-2 px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-4 shadow-[0_-4px_18px_rgba(0,0,0,0.08)] ${
        correct ? "border-[#a6df7a] bg-correct-bg" : "border-[#f0a8ad] bg-wrong-bg"
      }`}
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <div
            className={`mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xl font-black text-white ${
              correct ? "bg-feather" : "bg-cardinal"
            }`}
          >
            {correct ? "✓" : "!"}
          </div>
          <div>
            <p className={`text-xl font-black ${correct ? "text-feather-dark" : "text-cardinal-dark"}`}>
              {correct ? "Nicely done!" : "Not quite"}
            </p>
            {!correct && correctAnswer && (
              <p className="mt-0.5 text-sm font-extrabold text-eel">
                Correct answer: <span className="font-black">{correctAnswer}</span>
              </p>
            )}
            {correct && speakText && (
              <button type="button" onClick={speak} className="mt-0.5 text-sm font-extrabold text-eel underline">
                🔊 Hear it again
              </button>
            )}
          </div>
        </div>
        {correct ? (
          <button
            type="button"
            onClick={onContinue}
            className="min-w-[150px] rounded-xl bg-feather px-6 py-3 text-sm font-black uppercase tracking-wide text-white shadow-btn-green transition active:translate-y-1 active:shadow-none"
          >
            {finalStep ? "Finish" : "Continue"}
          </button>
        ) : (
          <button
            type="button"
            onClick={onRetry ?? onContinue}
            className="min-w-[150px] rounded-xl bg-cardinal px-6 py-3 text-sm font-black uppercase tracking-wide text-white shadow-btn-red transition active:translate-y-1 active:shadow-none"
          >
            Try again
          </button>
        )}
      </div>
    </div>
  );
}
