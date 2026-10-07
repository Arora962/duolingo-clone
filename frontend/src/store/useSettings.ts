import { create } from "zustand";
import { api } from "~/lib/api";
import type { Settings } from "~/lib/types";

type SettingsState = {
  settings: Settings | null;
  loading: boolean;
  refresh: () => Promise<void>;
  patch: (partial: Partial<Settings>) => void;
};

export const useSettings = create<SettingsState>()((set) => ({
  settings: null,
  loading: false,
  refresh: async () => {
    set({ loading: true });
    try {
      set({ settings: await api.settings(), loading: false });
    } catch {
      set({ loading: false });
    }
  },
  patch: (partial) =>
    set((state) =>
      state.settings
        ? { settings: { ...state.settings, ...partial } }
        : state,
    ),
}));
