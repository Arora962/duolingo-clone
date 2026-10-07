import { create } from "zustand";
import { api } from "~/lib/api";
import type { Me } from "~/lib/types";

type LearnerState = {
  me: Me | null;
  error: string | null;
  /** Re-fetch /api/me. Call after finishing a lesson, refilling hearts, etc. */
  refresh: () => Promise<void>;
  /** Optimistically patch a few fields (e.g. hearts while in a lesson). */
  patch: (partial: Partial<Me>) => void;
};

export const useLearner = create<LearnerState>()((set) => ({
  me: null,
  error: null,
  refresh: async () => {
    try {
      set({ me: await api.me(), error: null });
    } catch (e) {
      set({ error: e instanceof Error ? e.message : "Something went wrong" });
    }
  },
  patch: (partial) =>
    set((state) => (state.me ? { me: { ...state.me, ...partial } } : state)),
}));