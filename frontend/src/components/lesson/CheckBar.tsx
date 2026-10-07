import { Button3D } from "~/components/ui/Button3D";

type Props = {
  ready: boolean;
  onCheck: () => void;
  onSkip?: () => void;
  checking?: boolean;
};

export function CheckBar({ ready, onCheck, onSkip, checking = false }: Props) {
  return (
    <div className="fixed inset-x-0 bottom-0 z-50 border-t-2 border-[var(--color-border)] bg-[var(--color-surface)] px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-3 shadow-[0_-4px_18px_rgba(0,0,0,0.08)]">
      <div className="mx-auto flex max-w-3xl items-center gap-3">
        <Button3D
          tone="neutral"
          className="hidden min-w-[92px] sm:inline-flex"
          disabled={checking || !onSkip}
          onClick={onSkip}
        >
          Skip
        </Button3D>
        <Button3D
          tone="green"
          fullWidth
          disabled={!ready || checking}
          onClick={onCheck}
        >
          {checking ? "Checking…" : "Check"}
        </Button3D>
      </div>
    </div>
  );
}
