import type { ExerciseOption } from "~/lib/types";

type Props = {
  options: ExerciseOption[];
  disabled: boolean;
  selectedId: number | null;
  onSelect: (id: number) => void;
};

export function MultipleChoice({ options, disabled, selectedId, onSelect }: Props) {
  return (
    <div className="grid w-full gap-3 sm:grid-cols-2">
      {options.map((option, index) => {
        const selected = selectedId === option.id;
        return (
          <button
            key={option.id}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(option.id)}
            className={[
              "min-h-[68px] rounded-2xl border-2 px-5 py-4 text-left text-lg font-extrabold transition",
              "active:translate-y-0.5 disabled:cursor-not-allowed",
              selected
                ? "border-[var(--color-blue-border)] bg-[var(--color-blue-surface)] text-[var(--color-blue-text)] shadow-[0_3px_0_var(--color-blue-text)]"
                : "border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] shadow-[0_3px_0_var(--color-border)] hover:border-[var(--color-text-subtle)]",
            ].join(" ")}
          >
            <span className="mr-3 inline-flex h-7 w-7 items-center justify-center rounded-lg border-2 border-current text-sm opacity-70">
              {String.fromCharCode(65 + index)}
            </span>
            {option.image_emoji ? `${option.image_emoji} ` : ""}
            {option.text}
          </button>
        );
      })}
    </div>
  );
}
