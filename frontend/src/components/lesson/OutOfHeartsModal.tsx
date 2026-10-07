import type { HeartsResponse } from "~/lib/types";

type Props = {
  hearts: HeartsResponse | null;
  busy: boolean;
  onRefill: () => void;
  onExit: () => void;
};

export function OutOfHeartsModal({ hearts, busy, onRefill, onExit }: Props) {
  const cost = hearts?.refill_cost_gems ?? 350;
  const gems = hearts?.gems ?? 0;
  const canRefill = gems >= cost;

  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/45 px-4 py-8">
      <div className="w-full max-w-md rounded-3xl bg-white p-7 text-center shadow-2xl">
        <div className="text-6xl">💔</div>
        <h1 className="mt-3 text-3xl font-black text-eel">Out of hearts</h1>
        <p className="mt-2 font-bold text-wolf">No worries. Refill your hearts and give the lesson another try.</p>
        <div className="mt-6 rounded-2xl bg-polar p-4">
          <p className="font-black text-eel">💎 {gems} gems</p>
          <p className="mt-1 text-sm font-extrabold text-wolf">Full refill: {cost} gems</p>
        </div>
        <button
          type="button"
          disabled={busy || !canRefill}
          onClick={onRefill}
          className="mt-5 w-full rounded-xl bg-macaw px-6 py-4 text-sm font-black uppercase tracking-wide text-white shadow-btn-blue active:translate-y-1 active:shadow-none disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? "Refilling…" : canRefill ? "Refill & try again" : "Not enough gems"}
        </button>
        <button type="button" onClick={onExit} className="mt-3 w-full rounded-xl px-6 py-3 text-sm font-black uppercase tracking-wide text-wolf hover:bg-polar">
          Back to path
        </button>
      </div>
    </div>
  );
}
