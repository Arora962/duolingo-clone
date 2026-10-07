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
            className={`min-h-[68px] rounded-2xl border-2 px-5 py-4 text-left text-lg font-extrabold transition active:translate-y-0.5 disabled:cursor-not-allowed ${
              selected
                ? "border-macaw bg-[#eaf7ff] text-macaw shadow-[0_3px_0_#1899d6]"
                : "border-swan bg-white text-eel shadow-[0_3px_0_#e5e5e5] hover:border-hare"
            }`}
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
