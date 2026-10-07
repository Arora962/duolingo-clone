type Tile = { id: number; text: string };

type Props = {
  tiles: Tile[];
  selectedIds: number[];
  disabled: boolean;
  onToggle: (id: number) => void;
};

export function WordBank({ tiles, selectedIds, disabled, onToggle }: Props) {
  const selected = selectedIds
    .map((id) => tiles.find((tile) => tile.id === id))
    .filter(Boolean) as Tile[];

  return (
    <div className="w-full">
      <div className="mb-6 flex min-h-[92px] flex-wrap content-start gap-2 border-b-2 border-[var(--color-border)] pb-4">
        {selected.length ? (
          selected.map((tile) => (
            <button
              key={`selected-${tile.id}`}
              type="button"
              disabled={disabled}
              onClick={() => onToggle(tile.id)}
              className="rounded-xl border-2 border-[var(--color-blue-border)] bg-[var(--color-surface)] px-3 py-2 text-base font-extrabold text-[var(--color-text)] shadow-[0_3px_0_var(--color-blue-border)] active:translate-y-0.5"
            >
              {tile.text}
            </button>
          ))
        ) : (
          <span className="pt-2 text-sm font-extrabold text-[var(--color-text-subtle)]">
            Tap the words to build your answer.
          </span>
        )}
      </div>

      <div className="flex flex-wrap justify-center gap-2">
        {tiles.map((tile) => {
          const selectedTile = selectedIds.includes(tile.id);
          return (
            <button
              key={tile.id}
              type="button"
              disabled={disabled || selectedTile}
              onClick={() => onToggle(tile.id)}
              aria-hidden={selectedTile}
              className={[
                "min-h-[42px] rounded-xl border-2 px-3 py-2 text-base font-extrabold transition",
                selectedTile
                  ? "border-transparent bg-[var(--color-surface-raised)] text-transparent shadow-none"
                  : "border-[var(--color-border)] bg-[var(--color-surface)] text-[var(--color-text)] shadow-[0_3px_0_var(--color-border)] hover:border-[var(--color-text-subtle)]",
              ].join(" ")}
            >
              {selectedTile ? <span className="invisible">{tile.text}</span> : tile.text}
            </button>
          );
        })}
      </div>
    </div>
  );
}
