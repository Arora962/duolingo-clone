type Item = { id: number; text: string };

type Props = {
  left: Item[];
  right: Item[];
  matchedIds: Set<number>;
  selectedLeft: number | null;
  selectedRight: number | null;
  disabled: boolean;
  onSelectLeft: (id: number) => void;
  onSelectRight: (id: number) => void;
};

const buttonClass = (selected: boolean, matched: boolean) =>
  `min-h-[64px] rounded-2xl border-2 px-4 py-3 text-center text-base font-extrabold transition active:translate-y-0.5 ${
    matched
      ? "border-feather bg-[#efffe7] text-feather"
      : selected
        ? "border-macaw bg-[#eaf7ff] text-macaw shadow-[0_3px_0_#1899d6]"
        : "border-swan bg-white text-eel shadow-[0_3px_0_#e5e5e5] hover:border-hare"
  }`;

export function MatchPairs({
  left,
  right,
  matchedIds,
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
            className={`w-full ${buttonClass(selectedLeft === item.id, matchedIds.has(item.id))}`}
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
            className={`w-full ${buttonClass(selectedRight === item.id, matchedIds.has(item.id))}`}
          >
            {item.text}
          </button>
        ))}
      </div>
    </div>
  );
}
