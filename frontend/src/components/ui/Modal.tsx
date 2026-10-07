import { useEffect, type ReactNode } from "react";

type ModalProps = {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
  closeLabel?: string;
  widthClassName?: string;
};

export function Modal({
  open,
  title,
  children,
  onClose,
  closeLabel = "Close",
  widthClassName = "max-w-md",
}: ModalProps) {
  useEffect(() => {
    if (!open) {
      return;
    }

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    document.addEventListener("keydown", handleKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-[var(--color-overlay)] p-4"
      role="presentation"
      onMouseDown={(event) => {
        if (event.currentTarget === event.target) {
          onClose();
        }
      }}
    >
      <section
        className={[
          "animate-duo-pop w-full rounded-2xl border-2 border-[var(--color-border)]",
          "bg-[var(--color-surface)] p-5 shadow-duo-modal sm:p-6",
          widthClassName,
        ].join(" ")}
        role="dialog"
        aria-modal="true"
        aria-labelledby="duo-modal-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="mb-5 flex items-start justify-between gap-4">
          <h2
            id="duo-modal-title"
            className="text-xl font-black tracking-tight text-[var(--color-text)]"
          >
            {title}
          </h2>

          <button
            type="button"
            onClick={onClose}
            aria-label={closeLabel}
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-xl font-black text-[var(--color-text-muted)] transition hover:bg-[var(--color-surface-raised)]"
          >
            ×
          </button>
        </div>

        {children}
      </section>
    </div>
  );
}