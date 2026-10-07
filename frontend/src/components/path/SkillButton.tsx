import { useState } from "react";
import type { NodeState, SkillNode as SkillData } from "~/lib/types";
import { SkillGlyph } from "~/components/path/SkillGlyph";

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
  open: boolean;
  busy: boolean;
  onToggle: () => void;
  onAction: (action: SkillAction) => void;
};

const RING_R = 40;
const RING_LEN = 2 * Math.PI * RING_R;

export function SkillButton({
  skill,
  offset,
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
    skill.lessons.find((l) => l.id === skill.next_lesson_id)?.xp_reward ?? 0;

  // ----- popover content -----
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
    cta = done ? "Practice again" : "Start practice";
  } else {
    subtitle = `Lesson ${Math.min(
      skill.lessons_completed + 1,
      skill.lessons_total,
    )} of ${skill.lessons_total}`;
    cta = done ? "Practice again" : `Start +${nextXp} XP`;
  }

  const cardBg = locked ? "#e5e5e5" : isTreasure ? "#1cb0f6" : p.bg;
  const cardText = locked ? "#777777" : "#ffffff";

  const handleAction = () => {
    if (!canAct || busy) return;
    if (isTreasure) onAction({ kind: "treasure", skillId: skill.id });
    else if (lessonId !== null) onAction({ kind: "lesson", lessonId });
  };

  return (
    <div
      className="relative flex h-[104px] w-full items-center justify-center"
      style={{
        transform: `translateX(${offset}px)`,
        zIndex: open ? 30 : 1,
      }}
    >
      {/* floating START bubble above the current skill */}
      {skill.is_current && !locked && !open && !isTreasure && (
        <div className="pointer-events-none absolute -top-1 left-0 right-0 flex justify-center">
          <div className="animate-bounce">
            <div className="relative rounded-xl border-2 border-swan bg-white px-4 py-2 text-sm font-extrabold uppercase tracking-wide text-feather">
              Start
              <span className="absolute -bottom-[7px] left-1/2 h-3 w-3 -translate-x-1/2 rotate-45 border-b-2 border-r-2 border-swan bg-white" />
            </div>
          </div>
        </div>
      )}

      {isTreasure ? (
        <button
          type="button"
          aria-label={skill.title}
          onClick={(e) => {
            e.stopPropagation();
            onToggle();
          }}
          className={`text-[64px] leading-none transition-transform active:scale-95 ${
            locked ? "opacity-50 grayscale" : done ? "opacity-70" : ""
          }`}
        >
          🎁
        </button>
      ) : (
        <div className="relative mt-4 flex h-[92px] w-[92px] items-center justify-center">
          {/* progress ring on the current skill */}
          {skill.is_current && !locked && (
            <svg
              className="absolute inset-0 -rotate-90"
              viewBox="0 0 92 92"
              aria-hidden
            >
              <circle
                cx="46"
                cy="46"
                r={RING_R}
                fill="none"
                stroke="#e5e5e5"
                strokeWidth="6"
              />
              <circle
                cx="46"
                cy="46"
                r={RING_R}
                fill="none"
                stroke="#58cc02"
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray={`${RING_LEN * skill.progress_ratio} ${RING_LEN}`}
              />
            </svg>
          )}
          <button
            type="button"
            aria-label={skill.title}
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }}
            onPointerDown={() => setPressed(true)}
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
          </button>
        </div>
      )}

      {/* popover card */}
      {open && (
        <div
          onClick={(e) => e.stopPropagation()}
          className="absolute left-1/2 top-full z-30 mt-1 w-[280px] -translate-x-1/2 rounded-2xl p-4"
          style={{ backgroundColor: cardBg, color: cardText }}
        >
          <span
            className="absolute -top-2 left-1/2 h-4 w-4 -translate-x-1/2 rotate-45 rounded-sm"
            style={{ backgroundColor: cardBg }}
          />
          <p className="text-xl font-extrabold">{skill.title}</p>
          <p className="mt-0.5 text-base font-bold opacity-90">{subtitle}</p>
          <button
            type="button"
            disabled={!canAct || busy}
            onClick={handleAction}
            className="mt-3 w-full rounded-xl bg-white py-3 text-base font-extrabold uppercase tracking-wide transition-transform active:translate-y-1 disabled:cursor-not-allowed disabled:opacity-60"
            style={{
              color: locked ? "#afafaf" : cardBg,
              boxShadow: "0 4px 0 rgba(0,0,0,0.18)",
            }}
          >
            {busy ? "…" : cta}
          </button>
        </div>
      )}
    </div>
  );
}