import { useEffect, useState } from "react";

export function ChestReward({ claimed }: { claimed: boolean }) {
  const [burst, setBurst] = useState(false);

  useEffect(() => {
    if (!claimed) return;
    setBurst(true);
    const timer = window.setTimeout(() => setBurst(false), 700);
    return () => window.clearTimeout(timer);
  }, [claimed]);

  return (
    <div className="relative flex h-[92px] w-[92px] items-center justify-center">
      {burst &&
        Array.from({ length: 8 }).map((_, index) => (
          <span
            key={index}
            className="absolute h-2 w-2 animate-duo-pop rounded-full bg-[var(--color-bee)]"
            style={{
              transform: `rotate(${index * 45}deg) translateY(-48px)`,
            }}
          />
        ))}
      <svg viewBox="0 0 96 96" className="h-[82px] w-[82px]" aria-hidden>
        <rect x="12" y="34" width="72" height="46" rx="10" fill="#ffc800" />
        <rect x="12" y="34" width="72" height="12" rx="6" fill="#e5b400" />
        <path d="M42 34v46M54 34v46" stroke="#e5b400" strokeWidth="5" />
        <path d="M48 22c-5-13-21-11-21-1 0 9 13 13 21 13s21-4 21-13c0-10-16-12-21 1Z" fill="#58cc02" />
      </svg>
    </div>
  );
}
