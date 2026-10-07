import type { CSSProperties } from "react";

type ProgressBarProps = {
  value: number;
  max?: number;
  height?: number;
  label?: string;
  showLabel?: boolean;
  className?: string;
  fillClassName?: string;
};

export function ProgressBar({
  value,
  max = 100,
  height = 12,
  label,
  showLabel = false,
  className = "",
  fillClassName = "bg-feather",
}: ProgressBarProps) {
  const safeMax = max > 0 ? max : 100;
  const percentage = Math.min(100, Math.max(0, (value / safeMax) * 100));

  const trackStyle: CSSProperties = {
    height,
  };

  return (
    <div className={className}>
      {showLabel && (
        <div className="mb-2 flex items-center justify-between text-sm font-extrabold">
          <span>{label ?? "Progress"}</span>
          <span>{Math.round(percentage)}%</span>
        </div>
      )}

      <div
        className="relative w-full overflow-hidden rounded-full bg-swan dark:bg-[#414141]"
        style={trackStyle}
        role="progressbar"
        aria-label={label ?? "Progress"}
        aria-valuemin={0}
        aria-valuemax={safeMax}
        aria-valuenow={Math.min(value, safeMax)}
      >
        <div
          className={[
            "relative h-full overflow-hidden rounded-full transition-[width] duration-300 ease-out",
            fillClassName,
          ].join(" ")}
          style={{ width: `${percentage}%` }}
        >
          <span className="absolute inset-x-0 top-0 h-1/3 rounded-full bg-white/25" />
        </div>
      </div>
    </div>
  );
}