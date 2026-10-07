import type { CompleteResult } from "~/lib/types";

type Props = {
  result: CompleteResult;
  onContinue: () => void;
};

export function LessonCompleteModal({ result, onContinue }: Props) {
  return (
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/45 px-4 py-8">
      <div className="w-full max-w-md overflow-hidden rounded-3xl bg-white shadow-2xl">
        <div className="bg-feather px-6 pb-8 pt-10 text-center text-white">
          <div className="text-6xl">🏆</div>
          <h1 className="mt-3 text-3xl font-black">Lesson complete!</h1>
          <p className="mt-1 font-extrabold text-white/90">Keep going — your path is moving forward.</p>
        </div>
        <div className="grid grid-cols-3 gap-2 p-6 text-center">
          <div className="rounded-2xl bg-polar p-4">
            <p className="text-2xl font-black text-feather">+{result.xp_earned}</p>
            <p className="text-xs font-extrabold uppercase text-wolf">XP</p>
          </div>
          <div className="rounded-2xl bg-polar p-4">
            <p className="text-2xl font-black text-macaw">{Math.round(result.accuracy_percent)}%</p>
            <p className="text-xs font-extrabold uppercase text-wolf">Accuracy</p>
          </div>
          <div className="rounded-2xl bg-polar p-4">
            <p className="text-2xl font-black text-fox">🔥 {result.streak_after}</p>
            <p className="text-xs font-extrabold uppercase text-wolf">Streak</p>
          </div>
        </div>
        {(result.goal_just_met || result.skill_just_completed || result.next_skill_unlocked) && (
          <div className="mx-6 rounded-2xl border-2 border-swan p-4 text-center">
            {result.goal_just_met && <p className="font-black text-fox">🎯 Daily goal reached!</p>}
            {result.skill_just_completed && <p className="mt-1 font-black text-feather">👑 Skill completed!</p>}
            {result.next_skill_unlocked && (
              <p className="mt-1 text-sm font-extrabold text-eel">🔓 {result.next_skill_unlocked.title} is now unlocked.</p>
            )}
          </div>
        )}
        <div className="p-6 pt-5">
          <button
            type="button"
            onClick={onContinue}
            className="w-full rounded-xl bg-feather px-6 py-4 text-sm font-black uppercase tracking-wide text-white shadow-btn-green active:translate-y-1 active:shadow-none"
          >
            Continue learning
          </button>
        </div>
      </div>
    </div>
  );
}
