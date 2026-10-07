import type { CompleteResult } from "~/lib/types";
import { CompleteFlow } from "~/components/lesson/CompleteFlow";

type Props = {
  result: CompleteResult;
  onContinue: () => void;
};

export function LessonCompleteModal({ result, onContinue }: Props) {
  return <CompleteFlow result={result} onContinue={onContinue} />;
}
