import { create } from "zustand";

export type ToastTone = "info" | "success" | "error" | "warning";

export type ToastItem = {
  id: number;
  message: string;
  tone: ToastTone;
  /** Backwards-compatible alias used by the original Phase 1 UI. */
  kind: ToastTone;
};

type ToastState = {
  toasts: ToastItem[];
  /** Backwards-compatible alias used by the Phase 3 ZIP's ToastViewport. */
  items: ToastItem[];
  push: (message: string, tone?: ToastTone) => void;
  remove: (id: number) => void;
  /** Backwards-compatible alias. */
  dismiss: (id: number) => void;
};

let nextToastId = 1;

export const useToast = create<ToastState>()((set) => {
  const remove = (id: number) => {
    set((state) => {
      const toasts = state.toasts.filter((toast) => toast.id !== id);
      return { toasts, items: toasts };
    });
  };

  const push = (message: string, tone: ToastTone = "info") => {
    const id = nextToastId++;
    set((state) => {
      const toast: ToastItem = { id, message, tone, kind: tone };
      const toasts = [...state.toasts, toast].slice(-3);
      return { toasts, items: toasts };
    });

    if (typeof window !== "undefined") {
      window.setTimeout(() => remove(id), 3000);
    }
  };

  return {
    toasts: [],
    items: [],
    push,
    remove,
    dismiss: remove,
  };
});
