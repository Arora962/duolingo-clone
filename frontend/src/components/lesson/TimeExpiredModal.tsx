import { Modal } from "~/components/ui/Modal";
import { Button3D } from "~/components/ui/Button3D";

type Props = {
  open: boolean;
  onRetry: () => void;
  onExit: () => void;
};

export function TimeExpiredModal({ open, onRetry, onExit }: Props) {
  return (
    <Modal open={open} title="Time is up!" onClose={onExit} widthClassName="max-w-sm">
      <div className="text-center">
        <div className="text-6xl" aria-hidden>⏱️</div>
        <p className="mt-4 text-base font-extrabold text-[var(--color-text-muted)]">
          Your timed practice expired. Try it again when you’re ready.
        </p>
        <div className="mt-6 grid gap-3">
          <Button3D tone="green" fullWidth onClick={onRetry}>
            Try again
          </Button3D>
          <Button3D tone="neutral" fullWidth onClick={onExit}>
            Back to path
          </Button3D>
        </div>
      </div>
    </Modal>
  );
}
