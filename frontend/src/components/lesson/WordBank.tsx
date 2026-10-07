type Tile = { id: number; text: string };

type Props = {
  tiles: Tile[];
  selectedIds: number[];
  disabled: boolean;
  onToggle: (id: number) => void;
  onSubmit: () => void;
};

export function WordBank({ tiles, selectedIds, disabled, onToggle, onSubmit }: Props) {
  const selected = selectedIds.map((id) => tiles.find((tile) => tile.id === id)).filter(Boolean) as Tile[];

  return (
    <div className="w-full">
      <div className="mb-6 flex min-h-[92px] flex-wrap content-start gap-2 border-b-2 border-swan pb-4">
        {selected.length ? selected.map((tile) => (
          <button
            key={`selected-${tile.id}`}
            type="button"
            disabled={disabled}
            onClick={() => onToggle(tile.id)}
            className="rounded-xl border-2 border-macaw bg-white px-3 py-2 text-base font-extrabold text-eel shadow-[0_3px_0_#1899d6] active:translate-y-0.5"
          >
            {tile.text}
          </button>
        )) : (
          <span className="pt-2 text-sm font-extrabold text-hare">Tap the words to build your answer.</span>
        )}
      </div>
      <div className="flex flex-wrap justify-center gap-2">
        {tiles.map((tile) => {
          const selected = selectedIds.includes(tile.id);
          return (
            <button
              key={tile.id}
              type="button"
              disabled={disabled || selected}
              onClick={() => onToggle(tile.id)}
              className={`rounded-xl border-2 px-3 py-2 text-base font-extrabold transition active:translate-y-0.5 ${
                selected
                  ? "border-transparent bg-polar text-hare shadow-none"
                  : "border-swan bg-white text-eel shadow-[0_3px_0_#e5e5e5] hover:border-hare"
              }`}
            >
              {tile.text}
            </button>
          );
        })}
      </div>
      <button
        type="button"
        disabled={disabled || selectedIds.length === 0}
        onClick={onSubmit}
        className="mt-6 w-full rounded-xl bg-feather px-6 py-4 text-sm font-black uppercase tracking-wide text-white shadow-btn-green transition active:translate-y-1 active:shadow-none disabled:cursor-not-allowed disabled:opacity-50"
      >
        Check
      </button>
    </div>
  );
}
