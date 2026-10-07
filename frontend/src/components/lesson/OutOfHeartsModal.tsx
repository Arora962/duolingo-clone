import { Modal } from "~/components/ui/Modal";
import { Button3D } from "~/components/ui/Button3D";
import { useCountdown, formatCountdown } from "~/hooks/useCountdown";
import type { HeartsResponse } from "~/lib/types";

type Props = {
  hearts: HeartsResponse | null;
  busy: boolean;
  onRefillGems: () => void;
  onPractice: () => void;
  onExit: () => void;
};

export function OutOfHeartsModal({
  hearts,
  busy,
  onRefillGems,
  onPractice,
  onExit,
}: Props) {
  const cost = hearts?.refill_cost_gems ?? 100;
  const gems = hearts?.gems ?? 0;
  const canRefill = gems >= cost;
  const regen = useCountdown(hearts?.next_heart_in_seconds ?? 0);

  return (
    <Modal open title="Out of hearts" onClose={onExit} widthClassName="max-w-md">
      <div className="text-center">
        <div className="text-6xl" aria-hidden>💔</div>
        <p className="mt-3 font-extrabold text-[var(--color-text-muted)]">
          You can refill with gems, practice to earn one heart, or wait for regeneration.
        </p>

        <div className="mt-5 rounded-2xl bg-[var(--color-surface-raised)] p-4">
          <p className="font-black text-[var(--color-text)]">💎 {gems} gems</p>
          <p className="mt-1 text-sm font-extrabold text-[var(--color-text-muted)]">
            Full refill: {cost} gems
          </p>
          {regen > 0 && (
            <p className="mt-2 text-sm font-black text-[var(--color-red-text)]">
              Next heart in {formatCountdown(regen)}
            </p>
          )}
        </div>

        <div className="mt-5 grid gap-3">
          <Button3D tone="blue" fullWidth disabled={busy || !canRefill} onClick={onRefillGems}>
            {busy ? "Refilling…" : canRefill ? `Refill for ${cost} gems` : "Not enough gems"}
          </Button3D>
          <Button3D tone="green" fullWidth disabled={busy} onClick={onPractice}>
            Practice to earn a heart
          </Button3D>
          <Button3D tone="neutral" fullWidth onClick={onExit}>
            No thanks
          </Button3D>
        </div>
      </div>
    </Modal>
  );
}
