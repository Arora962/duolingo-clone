type Props = {
  value: string;
  placeholder?: string;
  disabled: boolean;
  onChange: (value: string) => void;
};

export function TypeAnswer({
  value,
  placeholder = "Type your answer",
  disabled,
  onChange,
}: Props) {
  return (
    <div className="w-full">
      <label className="sr-only" htmlFor="lesson-answer">
        Your answer
      </label>
      <input
        id="lesson-answer"
        autoComplete="off"
        autoCapitalize="off"
        spellCheck={false}
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="w-full rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-4 text-xl font-extrabold text-[var(--color-text)] outline-none transition placeholder:text-[var(--color-text-subtle)] focus:border-[var(--color-blue-border)] focus:ring-4 focus:ring-[var(--color-blue-surface)] disabled:bg-[var(--color-surface-raised)]"
      />
    </div>
  );
}
