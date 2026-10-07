import { create } from "zustand";

export type ToastTone = "info" | "success" | "error" | "warning";

export type ToastItem = {
  id: string;
  message: string;
  tone: ToastTone;
};

type ToastState = {
  toasts: ToastItem[];
  push: (message: string, tone?: ToastTone) => string;
  remove: (id: string) => void;
  clear: () => void;
};

let toastSequence = 0;

function createToastId(): string {
  toastSequence += 1;
  return `toast-${Date.now()}-${toastSequence}`;
}

export const useToast = create<ToastState>()((set) => ({
  toasts: [],

  push: (message, tone = "info") => {
    const id = createToastId();

    set((state) => ({
      toasts: [...state.toasts, { id, message, tone }],
    }));

    return id;
  },

  remove: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((toast) => toast.id !== id),
    }));
  },

  clear: () => {
    set({ toasts: [] });
  },
}));