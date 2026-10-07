import { useState } from "react";
import type { NodeState, SkillNode as SkillData } from "~/lib/types";
import { SkillGlyph } from "~/components/path/SkillGlyph";
import { NodePopover } from "~/components/path/NodePopover";
import { ChestReward } from "~/components/path/ChestReward";

const PALETTE: Record<NodeState, { bg: string; edge: string; glyph: string }> = {
  COMPLETED: { bg: "#ffc800", edge: "#e5b400", glyph: "#ffffff" },
  AVAILABLE: { bg: "#58cc02", edge: "#58a700", glyph: "#ffffff" },
  LOCKED: { bg: "#e5e5e5", edge: "#b7b7b7", glyph: "#afafaf" },
};

export type SkillAction =
  | { kind: "lesson"; lessonId: number }
  | { kind: "treasure"; skillId: number };

type Props = {
  skill: SkillData;
  offset: number;
  marginTop: number;
  marginBottom: number;
  open: boolean;
  busy: boolean;
  onToggle: () => void;
  onAction: (action: SkillAction) => void;
};

const RING_R = 42;
const RING_LEN = 2 * Math.PI * RING_R;

export function SkillButton({
  skill,
  offset,
  marginTop,
  marginBottom,
  open,
  busy,
  onToggle,
  onAction,
}: Props) {
  const [pressed, setPressed] = useState(false);
  const p = PALETTE[skill.state];
  const locked = skill.state === "LOCKED";
  const done = skill.state === "COMPLETED";
  const isTreasure = skill.skill_type === "TREASURE";
  const isPractice = skill.skill_type === "PRACTICE";
  const lessonId = skill.next_lesson_id ?? skill.lessons[0]?.id ?? null;
  const nextXp =
    skill.lessons.find((lesson) => lesson.id === skill.next_lesson_id)?.xp_reward ?? 0;

  let subtitle = "";
  let cta = "";
  let canAct = !locked;
  if (locked) {
    subtitle = "Finish the skills above to unlock this.";
    cta = "Locked";
  } else if (isTreasure) {
    subtitle = done ? "You already opened this chest." : "Open it for a gem reward!";
    cta = done ? "Opened" : "Open chest";
    canAct = !done;
  } else if (isPractice) {
    subtitle = "Timed practice · 3 minutes";
    cta = "Start practice";
  } else {
    subtitle = `Lesson ${Math.min(skill.lessons_completed + 1, skill.lessons_total)} of ${skill.lessons_total} · Crowns ${skill.crowns}/${skill.crowns_max}`;
    cta = done ? "Practice again" : `Start +${nextXp} XP`;
  }

  const handleAction = () => {
    if (!canAct || busy) return;
    if (isTreasure) onAction({ kind: "treasure", skillId: skill.id });
    else if (lessonId !== null) onAction({ kind: "lesson", lessonId });
  };

  return (
    <div
      className="relative flex w-full items-center justify-center"
      style={{
        height: 89,
        marginTop,
        marginBottom,
        transform: `translateX(${offset}px)`,
        zIndex: open ? 30 : 1,
      }}
    >
      {skill.is_current && !locked && !open && !isTreasure && (
        <div className="pointer-events-none absolute -top-8 left-0 right-0 flex justify-center">
          <div className="animate-duo-bounce relative rounded-xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2 text-sm font-extrabold uppercase tracking-wide text-[var(--color-green-text)] shadow-duo-soft">
            Start
            <span className="absolute -bottom-[7px] left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 border-b-2 border-r-2 border-[var(--color-border)] bg-[var(--color-surface)]" />
          </div>
        </div>
      )}

      {isTreasure ? (
        <button
          type="button"
          aria-label={skill.title}
          onPointerDown={(event) => event.stopPropagation()}
          onClick={(event) => {
            event.stopPropagation();
            onToggle();
          }}
          className="transition-transform active:scale-95"
        >
          <ChestReward claimed={done} />
        </button>
      ) : (
        <div className="relative flex h-[93px] w-[93px] items-center justify-center">
          {skill.is_current && !locked && (
            <svg className="absolute inset-0 -rotate-90" viewBox="0 0 93 93" aria-hidden>
              <circle cx="46.5" cy="46.5" r={RING_R} fill="none" stroke="var(--color-border)" strokeWidth="8" />
              <circle
                cx="46.5"
                cy="46.5"
                r={RING_R}
                fill="none"
                stroke="#58cc02"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${RING_LEN * skill.progress_ratio} ${RING_LEN}`}
              />
            </svg>
          )}
          <button
            type="button"
            aria-label={skill.title}
            onPointerDown={(event) => {
              event.stopPropagation();
              setPressed(true);
            }}
            onClick={(event) => {
              event.stopPropagation();
              onToggle();
            }}
            onPointerUp={() => setPressed(false)}
            onPointerLeave={() => setPressed(false)}
            className="flex h-[70px] w-[70px] items-center justify-center rounded-full transition-transform"
            style={{
              backgroundColor: p.bg,
              boxShadow: pressed ? `0 2px 0 ${p.edge}` : `0 8px 0 ${p.edge}`,
              transform: pressed ? "translateY(6px)" : undefined,
            }}
          >
            <SkillGlyph type={skill.icon_type} color={p.glyph} />
            {done && (
              <span className="absolute -right-1 -top-1 flex h-7 w-7 items-center justify-center rounded-full border-2 border-[var(--color-surface)] bg-[var(--color-bee)] text-xs font-black text-white">
                ✓
              </span>
            )}
          </button>
        </div>
      )}

      <NodePopover
        open={open}
        title={skill.title}
        subtitle={subtitle}
        cta={cta}
        disabled={!canAct || busy}
        onClose={onToggle}
        onAction={handleAction}
      />
    </div>
  );
}
