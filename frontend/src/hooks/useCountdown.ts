import { useEffect, useState } from "react";

function clampSeconds(value: number | null | undefined): number {
  if (value == null || !Number.isFinite(value)) {
    return 0;
  }

  return Math.max(0, Math.floor(value));
}

export function useCountdown(initialSeconds: number | null | undefined) {
  const [seconds, setSeconds] = useState(() => clampSeconds(initialSeconds));

  useEffect(() => {
    setSeconds(clampSeconds(initialSeconds));
  }, [initialSeconds]);

  useEffect(() => {
    if (seconds <= 0) {
      return;
    }

    const interval = window.setInterval(() => {
      setSeconds((current) => Math.max(0, current - 1));
    }, 1000);

    return () => window.clearInterval(interval);
  }, [seconds]);

  return seconds;
}

export function formatCountdown(totalSeconds: number): string {
  const safeSeconds = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safeSeconds / 60);
  const seconds = safeSeconds % 60;

  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}
