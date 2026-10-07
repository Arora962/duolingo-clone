import { useEffect, useRef, useState, type ReactNode, type RefObject } from "react";
import { Button3D } from "~/components/ui/Button3D";
import { ConfirmModal } from "~/components/layout/ConfirmModal";
import { Icon, type IconName } from "~/components/ui/Icons";
import { formatCountdown, useCountdown } from "~/hooks/useCountdown";
import { useOutsideClick } from "~/hooks/useOutsideClick";
import { ApiError, api } from "~/lib/api";
import { useLearner } from "~/store/useLearner";
import { useToast } from "~/store/useToast";

export type StatPopoverKind = "streak" | "gems" | "hearts";

type StatPopoverProps = {
  kind: StatPopoverKind;
  onClose: () => void;
};

const META: Record<
  StatPopoverKind,
  { title: string; icon: IconName; iconClass: string }
> = {
  streak: { title: "Streak", icon: "flame", iconClass: "text-fox" },
  gems: { title: "Gems", icon: "gem", iconClass: "text-macaw" },
  hearts: { title: "Hearts", icon: "heart", iconClass: "text-cardinal" },
};

export function StatPopover({ kind, onClose }: StatPopoverProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  useOutsideClick(containerRef, onClose);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (kind === "streak") {
    return <StreakPopover containerRef={containerRef} />;
  }

  if (kind === "gems") {
    return <GemsPopover containerRef={containerRef} />;
  }

  return <HeartsPopover containerRef={containerRef} />;
}

type InnerPopoverProps = { containerRef: RefObject<HTMLDivElement> };

function PopoverFrame({
  title,
  icon,
  iconClass,
  containerRef,
  children,
}: InnerPopoverProps & {
  title: string;
  icon: IconName;
  iconClass: string;
  children: ReactNode;
}) {
  return (
    <div
      ref={containerRef}
      className="absolute right-0 top-[calc(100%+10px)] z-50 w-[min(300px,calc(100vw-32px))] animate-duo-pop rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-4 text-left shadow-duo-modal"
      role="dialog"
    >
      <div className="mb-3 flex items-center gap-3">
        <div
          className={`flex h-10 w-10 items-center justify-center rounded-full bg-[var(--color-surface-raised)] ${iconClass}`}
        >
          <Icon name={icon} size={23} />
        </div>
        <h3 className="text-base font-black text-[var(--color-text)]">{title}</h3>
      </div>
      {children}
    </div>
  );
}

function StreakPopover({ containerRef }: InnerPopoverProps) {
  const me = useLearner((state) => state.me);

  return (
    <PopoverFrame
      title={META.streak.title}
      icon={META.streak.icon}
      iconClass={META.streak.iconClass}
      containerRef={containerRef}
    >
      <div className="rounded-xl bg-orange-50 p-4 dark:bg-[#422a14]">
        <p className="text-center text-4xl font-black text-fox">
          {me?.current_streak ?? 0}
        </p>
        <p className="mt-1 text-center text-sm font-extrabold text-[var(--color-text-muted)]">
          day{me?.current_streak === 1 ? "" : "s"} in a row
        </p>
      </div>
      <p className="mt-4 text-sm leading-5 text-[var(--color-text-muted)]">
        {me?.streak_active_today
          ? "Nice work — your streak is safe for today."
          : "Complete a lesson today to keep your streak alive."}
      </p>
    </PopoverFrame>
  );
}

function GemsPopover({ containerRef }: InnerPopoverProps) {
  const me = useLearner((state) => state.me);

  return (
    <PopoverFrame
      title={META.gems.title}
      icon={META.gems.icon}
      iconClass={META.gems.iconClass}
      containerRef={containerRef}
    >
      <div className="rounded-xl bg-blue-50 p-4 dark:bg-[#143b4e]">
        <p className="text-center text-3xl font-black text-macaw">
          {me?.gems ?? 0}
        </p>
        <p className="mt-1 text-center text-xs font-extrabold uppercase tracking-wide text-[var(--color-text-muted)]">
          available gems
        </p>
      </div>
      <p className="mt-4 text-sm leading-5 text-[var(--color-text-muted)]">
        Gems can be used for useful boosts and heart refills.
      </p>
    </PopoverFrame>
  );
}

function HeartsPopover({ containerRef }: InnerPopoverProps) {
  const me = useLearner((state) => state.me);
  const patch = useLearner((state) => state.patch);
  const pushToast = useToast((state) => state.push);
  const countdown = useCountdown(me?.next_heart_in_seconds);

  const hearts = me?.hearts ?? 0;
  const maxHearts = me?.max_hearts ?? 5;
  const gems = me?.gems ?? 0;
  const canRefill = hearts < maxHearts;
  const [practiceConfirmOpen, setPracticeConfirmOpen] = useState(false);

  const refill = async (method: "GEMS" | "PRACTICE") => {
    try {
      const result = await api.refillHearts(method);
      patch({
        hearts: result.hearts,
        max_hearts: result.max_hearts,
        next_heart_in_seconds: result.next_heart_in_seconds,
        gems: result.gems,
      });
      pushToast(
        method === "GEMS"
          ? "Your hearts are full again!"
          : "You earned one heart from practice!",
        "success",
      );
    } catch (error) {
      pushToast(
        error instanceof ApiError
          ? error.message
          : "We couldn't restore your hearts.",
        "error",
      );
    }
  };

  return (
    <PopoverFrame
      title={META.hearts.title}
      icon={META.hearts.icon}
      iconClass={META.hearts.iconClass}
      containerRef={containerRef}
    >
      <div className="flex items-center justify-between rounded-xl bg-red-50 p-4 dark:bg-[#4a2022]">
        <div>
          <p className="text-3xl font-black text-cardinal">
            {hearts}/{maxHearts}
          </p>
          <p className="mt-1 text-xs font-extrabold uppercase tracking-wide text-[var(--color-text-muted)]">
            hearts remaining
          </p>
        </div>
        <div className="flex gap-0.5">
          {Array.from({ length: maxHearts }).map((_, index) => (
            <Icon
              key={index}
              name="heart"
              size={17}
              className={
                index < hearts
                  ? "fill-cardinal text-cardinal"
                  : "text-[var(--color-border-strong)]"
              }
            />
          ))}
        </div>
      </div>

      {canRefill ? (
        <p className="mt-3 text-sm font-extrabold text-[var(--color-text-muted)]">
          Next heart in{" "}
          <span className="text-[var(--color-text)]">
            {formatCountdown(countdown)}
          </span>
        </p>
      ) : (
        <p className="mt-3 text-sm font-extrabold text-feather">
          Your hearts are full!
        </p>
      )}

      <div className="mt-4 grid gap-2">
        <Button3D
          tone="blue"
          fullWidth
          disabled={!canRefill || gems < 100}
          onClick={() => void refill("GEMS")}
        >
          {!canRefill ? "Hearts full" : gems < 100 ? "Need 100 gems" : "Refill — 100 gems"}
        </Button3D>

        <Button3D
          tone="neutral"
          fullWidth
          disabled={!canRefill}
          onClick={() => setPracticeConfirmOpen(true)}
        >
          Practice for a heart
        </Button3D>
      </div>

      <ConfirmModal
        open={practiceConfirmOpen}
        title="Practice for a heart?"
        description="Practice refill is a mock flow for this assignment. Confirm to restore one heart."
        confirmLabel="Restore heart"
        onCancel={() => setPracticeConfirmOpen(false)}
        onConfirm={() => {
          setPracticeConfirmOpen(false);
          void refill("PRACTICE");
        }}
      />
    </PopoverFrame>
  );
}
