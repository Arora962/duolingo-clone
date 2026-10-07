import { useEffect } from "react";
import { useToast, type ToastItem, type ToastTone } from "~/store/useToast";

const toneStyles: Record<ToastTone, string> = {
  info: "border-macaw bg-[var(--color-surface)]",
  success: "border-feather bg-[var(--color-green-surface)]",
  error: "border-cardinal bg-[var(--color-red-surface)]",
  warning: "border-bee bg-[var(--color-surface)]",
};

function ToastCard({ toast }: { toast: ToastItem }) {
  const remove = useToast((state) => state.remove);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      remove(toast.id);
    }, 3600);

    return () => {
      window.clearTimeout(timer);
    };
  }, [remove, toast.id]);

  return (
    <div
      className={[
        "animate-duo-slide-up flex max-w-sm items-center gap-3 rounded-2xl border-2",
        "px-4 py-3 text-sm font-extrabold shadow-duo-soft",
        toneStyles[toast.tone],
      ].join(" ")}
      role="status"
    >
      <span className="min-w-0 flex-1">{toast.message}</span>

      <button
        type="button"
        onClick={() => remove(toast.id)}
        className="shrink-0 rounded-full px-2 py-1 text-base text-[var(--color-text-muted)] hover:bg-black/5 dark:hover:bg-white/10"
        aria-label="Dismiss notification"
      >
        ×
      </button>
    </div>
  );
}

export function ToastViewport() {
  const toasts = useToast((state) => state.toasts);

  if (toasts.length === 0) {
    return null;
  }

  return (
    <div className="pointer-events-none fixed inset-x-4 bottom-5 z-[120] flex flex-col items-center gap-3 sm:items-end">
      {toasts.map((toast) => (
        <div key={toast.id} className="pointer-events-auto">
          <ToastCard toast={toast} />
        </div>
      ))}
    </div>
  );
}