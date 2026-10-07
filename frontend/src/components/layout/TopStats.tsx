import { useState } from "react";
import { Icon } from "~/components/ui/Icons";
import { ComingSoonModal } from "~/components/layout/ComingSoonModal";
import { StatPopover, type StatPopoverKind } from "~/components/layout/StatPopover";
import { useLearner } from "~/store/useLearner";

type TopStatsProps = {
  compact?: boolean;
};

export function TopStats({ compact = false }: TopStatsProps) {
  const me = useLearner((state) => state.me);
  const [open, setOpen] = useState<StatPopoverKind | null>(null);
  const [courseModalOpen, setCourseModalOpen] = useState(false);

  const toggle = (kind: StatPopoverKind) => {
    setOpen((current) => (current === kind ? null : kind));
  };

  return (
    <div
      className={[
        "relative flex items-center",
        compact ? "justify-between gap-2" : "gap-5",
      ].join(" ")}
    >
      <button
        type="button"
        onClick={() => {
          setOpen(null);
          setCourseModalOpen(true);
        }}
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-2xl transition hover:bg-[var(--color-surface-raised)]"
        title={me?.current_course?.name ?? "Current course"}
        aria-label="Current course"
      >
        {me?.current_course?.flag_emoji ?? "🌍"}
      </button>

      <StatButton
        kind="streak"
        label={me?.current_streak?.toString() ?? "–"}
        open={open === "streak"}
        onClick={() => toggle("streak")}
        compact={compact}
      />
      <StatButton
        kind="gems"
        label={me?.gems?.toString() ?? "–"}
        open={open === "gems"}
        onClick={() => toggle("gems")}
        compact={compact}
      />
      <StatButton
        kind="hearts"
        label={`${me?.hearts ?? "–"}`}
        open={open === "hearts"}
        onClick={() => toggle("hearts")}
        compact={compact}
      />

      {open && <StatPopover kind={open} onClose={() => setOpen(null)} />}

      <ComingSoonModal
        open={courseModalOpen}
        title="Course switcher coming soon"
        description="The seeded backend currently provides one course, so course switching is intentionally a placeholder."
        onClose={() => setCourseModalOpen(false)}
      />
    </div>
  );
}

type StatButtonProps = {
  kind: StatPopoverKind;
  label: string;
  open: boolean;
  compact: boolean;
  onClick: () => void;
};

function StatButton({ kind, label, open, onClick, compact }: StatButtonProps) {
  const icon = kind === "streak" ? "flame" : kind === "gems" ? "gem" : "heart";
  const color = kind === "streak" ? "text-fox" : kind === "gems" ? "text-macaw" : "text-cardinal";

  return (
    <div className="relative">
      <button
        type="button"
        onPointerDown={(event) => event.stopPropagation()}
        onClick={onClick}
        aria-expanded={open}
        aria-haspopup="dialog"
        className={[
          "flex min-w-12 items-center justify-center gap-1.5 rounded-xl border-2 px-2 py-2 text-sm font-black transition",
          open
            ? "border-[var(--color-border-strong)] bg-[var(--color-surface-raised)]"
            : "border-transparent hover:bg-[var(--color-surface-raised)]",
        ].join(" ")}
        title={kind}
      >
        <Icon name={icon} size={compact ? 19 : 20} className={color} strokeWidth={2.7} />
        <span className={color}>{label}</span>
      </button>
    </div>
  );
}
