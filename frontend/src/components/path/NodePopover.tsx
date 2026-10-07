import { useEffect, useRef } from "react";
import { Button3D } from "~/components/ui/Button3D";
import { useOutsideClick } from "~/hooks/useOutsideClick";

type Props = {
  open: boolean;
  title: string;
  subtitle: string;
  cta: string;
  disabled?: boolean;
  onClose: () => void;
  onAction: () => void;
};

export function NodePopover({
  open,
  title,
  subtitle,
  cta,
  disabled = false,
  onClose,
  onAction,
}: Props) {
  const ref = useRef<HTMLDivElement>(null);
  useOutsideClick(ref, onClose, open);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      ref={ref}
      className="absolute top-full z-40 mt-3 w-[294px] max-w-[calc(100vw-32px)] -translate-x-1/2 rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-4 text-[var(--color-text)] shadow-duo-modal"
      style={{ left: "clamp(147px, 50%, calc(100vw - 147px))" }}
    >
      <span className="absolute -top-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 border-l-2 border-t-2 border-[var(--color-border)] bg-[var(--color-surface)]" />
      <p className="text-xl font-extrabold">{title}</p>
      <p className="mt-1 text-sm font-bold text-[var(--color-text-muted)]">{subtitle}</p>
      <Button3D tone="green" fullWidth disabled={disabled} onClick={onAction} className="mt-4">
        {cta}
      </Button3D>
    </div>
  );
}
