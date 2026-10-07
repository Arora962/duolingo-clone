import { useLearner } from "~/store/useLearner";
import { TopStats } from "~/layout/TopStats";

export function RightRail() {
  const me = useLearner((s) => s.me);
  const goal = me?.daily_goal_xp ?? 20;
  const xp = Math.min(me?.xp_today ?? 0, goal);
  const pct = Math.round((xp / goal) * 100);

  return (
    <div className="flex flex-col gap-5">
      <TopStats />

      {/* Super promo (placeholder) */}
      <div className="rounded-2xl bg-gradient-to-r from-beetle to-macaw p-5 text-white">
        <p className="text-xl font-extrabold">Try Super for free</p>
        <p className="mt-1 text-sm font-bold opacity-90">
          No ads, unlimited hearts, and more.
        </p>
        <button
          disabled
          className="mt-4 w-full cursor-not-allowed rounded-xl bg-white py-3 text-sm font-extrabold uppercase tracking-wide text-macaw opacity-90"
        >
          Coming soon
        </button>
      </div>

      {/* Daily quests / XP goal */}
      <div className="rounded-2xl border-2 border-swan p-5">
        <p className="text-xl font-extrabold text-eel">Daily Quests</p>
        <div className="mt-4 flex items-center gap-4">
          <span className="text-3xl">⚡</span>
          <div className="flex-1">
            <p className="text-base font-extrabold text-eel">Earn {goal} XP</p>
            <div className="mt-2 flex items-center gap-2">
              <div className="relative h-4 flex-1 overflow-hidden rounded-full bg-swan">
                <div
                  className="h-full rounded-full bg-bee transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="text-sm font-extrabold text-wolf">
                {xp}/{goal}
              </span>
            </div>
          </div>
        </div>
        {me?.daily_goal_met && (
          <p className="mt-3 text-sm font-extrabold text-feather">
            ✓ Daily goal complete!
          </p>
        )}
      </div>
    </div>
  );
}