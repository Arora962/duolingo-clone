import { useEffect, useState } from "react";

function secondsUntil(expiresAt: string | number | null | undefined): number {
  if (expiresAt == null) return 0;
  if (typeof expiresAt === "number") return Math.max(0, Math.floor(expiresAt));
  const target = new Date(expiresAt).getTime();
  if (!Number.isFinite(target)) return 0;
  return Math.max(0, Math.ceil((target - Date.now()) / 1000));
}

export function useCountdown(
  target: string | number | null | undefined,
): number {
  const [seconds, setSeconds] = useState(() => secondsUntil(target));

  useEffect(() => {
    const tick = () => setSeconds(secondsUntil(target));
    tick();
    if (secondsUntil(target) <= 0) return;
    const interval = window.setInterval(tick, 1000);
    return () => window.clearInterval(interval);
  }, [target]);

  return seconds;
}

export function formatCountdown(totalSeconds: number): string {
  const safe = Math.max(0, Math.floor(totalSeconds));
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${minutes}:${seconds.toString().padStart(2, "0")}`;
}
