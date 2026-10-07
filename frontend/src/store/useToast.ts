import { create } from "zustand";

export type ToastTone = "info" | "success" | "error" | "warning";

export type ToastItem = {
  id: number;
  message: string;
  tone: ToastTone;
};

type ToastState = {
  toasts: ToastItem[];
  push: (message: string, tone?: ToastTone) => void;
  remove: (id: number) => void;
};

let nextToastId = 1;

export const useToast = create<ToastState>()((set) => {
  const remove = (id: number) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  };

  const push = (message: string, tone: ToastTone = "info") => {
    const id = nextToastId++;
    set((state) => ({
      toasts: [...state.toasts, { id, message, tone }].slice(-3),
    }));
    if (typeof window !== "undefined") {
      window.setTimeout(() => remove(id), 3600);
    }
  };

  return { toasts: [], push, remove };
});
