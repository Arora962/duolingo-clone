type Item = { id: number; text: string };

type Props = {
  left: Item[];
  right: Item[];
  matchedIds: Set<number>;
  shakeIds: Set<number>;
  selectedLeft: number | null;
  selectedRight: number | null;
  disabled: boolean;
  onSelectLeft: (id: number) => void;
  onSelectRight: (id: number) => void;
};

function buttonClass(selected: boolean, matched: boolean, shaking: boolean): string {
  return [
    "min-h-[64px] w-full rounded-2xl border-2 px-4 py-3 text-center text-base font-extrabold",
    "transition active:translate-y-0.5",
    matched
      ? "border-[var(--color-green-text)] bg-[var(--color-green-surface)] text-[var(--color-green-text)]"
      : selected
        ? "border-[var(--color-blue-border)] bg-[var(--color-blue-surface)] text-[var(--color-blue-text)] shadow-[0_3px_0_var(--color-blue-text)]"
        : "border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] shadow-[0_3px_0_var(--color-border)] hover:border-[var(--color-text-subtle)]",
    shaking ? "animate-duo-shake border-[var(--color-red-text)] bg-[var(--color-red-surface)]" : "",
  ].join(" ");
}

export function MatchPairs({
  left,
  right,
  matchedIds,
  shakeIds,
  selectedLeft,
  selectedRight,
  disabled,
  onSelectLeft,
  onSelectRight,
}: Props) {
  return (
    <div className="grid w-full grid-cols-2 gap-3">
      <div className="space-y-3">
        {left.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={disabled || matchedIds.has(item.id)}
            onClick={() => onSelectLeft(item.id)}
            className={buttonClass(
              selectedLeft === item.id,
              matchedIds.has(item.id),
              shakeIds.has(item.id),
            )}
          >
            {item.text}
          </button>
        ))}
      </div>
      <div className="space-y-3">
        {right.map((item) => (
          <button
            key={item.id}
            type="button"
            disabled={disabled || matchedIds.has(item.id)}
            onClick={() => onSelectRight(item.id)}
            className={buttonClass(
              selectedRight === item.id,
              matchedIds.has(item.id),
              shakeIds.has(item.id),
            )}
          >
            {item.text}
          </button>
        ))}
      </div>
    </div>
  );
}
