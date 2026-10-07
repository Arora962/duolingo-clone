import type { FillInBlankExercise } from "~/lib/types";
import { MultipleChoice } from "~/components/lesson/MultipleChoice";
import { TypeAnswer } from "~/components/lesson/TypeAnswer";

type Props = {
  exercise: FillInBlankExercise;
  disabled: boolean;
  selectedId: number | null;
  typedAnswer: string;
  onSelect: (id: number) => void;
  onType: (value: string) => void;
};

export function FillInBlank({
  exercise,
  disabled,
  selectedId,
  typedAnswer,
  onSelect,
  onType,
}: Props) {
  if (exercise.requires_typing) {
    return (
      <TypeAnswer
        value={typedAnswer}
        disabled={disabled}
        onChange={onType}
      />
    );
  }

  if (exercise.options) {
    return (
      <MultipleChoice
        options={exercise.options}
        disabled={disabled}
        selectedId={selectedId}
        onSelect={onSelect}
      />
    );
  }

  return null;
}
