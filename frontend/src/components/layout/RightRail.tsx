import { useState } from "react";
import { Button3D } from "~/components/ui/Button3D";
import { Icon } from "~/components/ui/Icons";
import { ComingSoonModal } from "~/components/layout/ComingSoonModal";
import { TopStats } from "~/components/layout/TopStats";
import { useLearner } from "~/store/useLearner";

export function RightRail() {
  const me = useLearner((state) => state.me);
  const [comingSoon, setComingSoon] = useState<string | null>(null);
  const goal = me?.daily_goal_xp ?? 20;
  const xp = Math.min(me?.xp_today ?? 0, goal);
  const percentage = goal > 0 ? Math.round((xp / goal) * 100) : 0;

  return (
    <>
      <div className="flex flex-col gap-5">
        <TopStats />

        <section className="overflow-hidden rounded-2xl border-2 border-[#1899d6] bg-gradient-to-br from-[#1cb0f6] to-[#ce82ff] p-5 text-white shadow-duo-card">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.12em] opacity-80">Premium</p>
              <h2 className="mt-1 text-xl font-black">Try Super</h2>
            </div>
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-white/20">
              <Icon name="sparkle" size={25} />
            </div>
          </div>
          <p className="mt-2 text-sm font-bold leading-5 text-white/90">More practice, unlimited hearts, and extra perks.</p>
          <Button3D tone="neutral" fullWidth className="mt-4" onClick={() => setComingSoon("Super")}>
            Learn about Super
          </Button3D>
        </section>

        <section className="duo-card p-5">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.12em] text-[var(--color-text-muted)]">Daily Quests</p>
              <h2 className="mt-1 text-xl font-black">XP Goal</h2>
            </div>
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[#fff3bd] text-bee dark:bg-[#4a3b0d]">
              <Icon name="sparkle" size={24} />
            </div>
          </div>

          <div className="mt-5">
            <div className="mb-2 flex items-center justify-between gap-3">
              <span className="text-sm font-black">Earn {goal} XP</span>
              <span className="text-sm font-black text-[var(--color-text-muted)]">{xp}/{goal}</span>
            </div>
            <div className="h-4 overflow-hidden rounded-full bg-swan dark:bg-[#414141]" role="progressbar" aria-label="Daily XP goal" aria-valuemin={0} aria-valuemax={goal} aria-valuenow={xp}>
              <div className="h-full rounded-full bg-bee transition-[width] duration-500" style={{ width: `${percentage}%` }} />
            </div>
          </div>

          {me?.daily_goal_met ? (
            <div className="mt-4 flex items-center gap-2 text-sm font-black text-feather">
              <span className="flex h-6 w-6 items-center justify-center rounded-full bg-green-100 dark:bg-[#1f3d12]"><Icon name="check" size={16} /></span>
              Daily goal complete!
            </div>
          ) : (
            <p className="mt-4 text-sm font-bold text-[var(--color-text-muted)]">{Math.max(0, goal - xp)} XP to go today.</p>
          )}
        </section>

        <div className="flex flex-wrap gap-x-4 gap-y-2 px-2 text-xs font-black text-[var(--color-text-subtle)]">
          {[
            ["Friends", "Friends"],
            ["Courses", "More courses"],
            ["Help", "Help"],
          ].map(([label, title]) => (
            <button key={label} type="button" onClick={() => setComingSoon(title)} className="transition hover:text-[var(--color-text)]">
              {label}
            </button>
          ))}
        </div>
      </div>

      <ComingSoonModal
        open={comingSoon !== null}
        title={`${comingSoon ?? "Feature"} coming soon`}
        description="This part of the experience is represented as a polished placeholder for the assignment."
        onClose={() => setComingSoon(null)}
      />
    </>
  );
}
