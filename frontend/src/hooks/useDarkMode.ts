import { useEffect } from "react";
import { useSettings } from "~/store/useSettings";

export function useDarkMode(): void {
  const enabled = useSettings(
    (state) => state.settings?.dark_mode_enabled ?? false,
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", enabled);
    document.documentElement.style.colorScheme = enabled ? "dark" : "light";
  }, [enabled]);
}
