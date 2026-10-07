import { useEffect, useMemo, useState } from "react";
import type { CompleteResult } from "~/lib/types";
import { OwlMascot } from "~/components/mascot/OwlMascot";
import { Button3D } from "~/components/ui/Button3D";
import { formatNumber } from "~/lib/format";

type Props = {
  result: CompleteResult;
  onContinue: () => void;
};

export function CompleteFlow({ result, onContinue }: Props) {
  const hasAchievements = result.newly_unlocked_achievements.length > 0;
  const maxStage = result.streak_extended && hasAchievements ? 3 : (result.streak_extended || hasAchievements ? 2 : 1);
  const [stage, setStage] = useState(0);

  const confetti = useMemo(
    () =>
      Array.from({ length: 18 }, (_, index) => ({
        left: `${(index * 17) % 100}%`,
        delay: `${(index % 6) * 90}ms`,
      })),
    [],
  );

  useEffect(() => {
    if (stage >= maxStage) return;
    const timer = window.setTimeout(
      () => setStage((current) => Math.min(current + 1, maxStage)),
      1300,
    );
    return () => window.clearTimeout(timer);
  }, [maxStage, stage]);

  return (
    <div className="fixed inset-0 z-[80] overflow-y-auto bg-[var(--color-background)]">
      <div className="relative mx-auto flex min-h-full w-full max-w-lg flex-col items-center px-5 py-8 text-center">
        {confetti.map((piece, index) => (
          <span
            key={`${piece.left}-${piece.delay}-${index}`}
            className="pointer-events-none absolute top-0 h-3 w-2 animate-duo-confetti rounded-sm bg-[var(--color-bee)]"
            style={{ left: piece.left, animationDelay: piece.delay }}
          />
        ))}

        {stage === 0 && (
          <>
            <OwlMascot size={170} mood="happy" />
            <h1 className="mt-2 text-4xl font-black text-[var(--color-text)]">
              Lesson complete!
            </h1>
            <p className="mt-2 font-extrabold text-[var(--color-text-muted)]">
              Nicely done. Your progress is saved.
            </p>
          </>
        )}

        {stage === 1 && (
          <>
            <OwlMascot size={135} mood="happy" />
            <h2 className="mt-2 text-3xl font-black text-[var(--color-text)]">
              Here’s your result
            </h2>
            <div className="mt-7 grid w-full grid-cols-3 gap-2">
              <div className="rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-4">
                <p className="text-2xl font-black text-[var(--color-green-text)]">
                  +{formatNumber(result.xp_earned)}
                </p>
                <p className="text-xs font-extrabold uppercase text-[var(--color-text-muted)]">XP</p>
              </div>
              <div className="rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-4">
                <p className="text-2xl font-black text-[var(--color-blue-text)]">
                  {Math.round(result.accuracy_percent)}%
                </p>
                <p className="text-xs font-extrabold uppercase text-[var(--color-text-muted)]">Accuracy</p>
              </div>
              <div className="rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-4">
                <p className="text-2xl font-black text-[var(--color-orange-text)]">
                  {result.streak_after}
                </p>
                <p className="text-xs font-extrabold uppercase text-[var(--color-text-muted)]">Streak</p>
              </div>
            </div>
          </>
        )}

        {stage === 2 && result.streak_extended && (
          <>
            <OwlMascot size={150} mood="happy" />
            <div className="mt-5 text-7xl">🔥</div>
            <h2 className="mt-3 text-4xl font-black text-[var(--color-orange-text)]">
              Streak extended!
            </h2>
            <p className="mt-2 font-extrabold text-[var(--color-text-muted)]">
              {result.streak_before} → {result.streak_after} days
            </p>
          </>
        )}

        {((stage === 2 && !result.streak_extended) || (stage === 3 && result.streak_extended)) && hasAchievements && (
          <>
            <OwlMascot size={130} mood="happy" />
            <h2 className="mt-2 text-3xl font-black text-[var(--color-text)]">
              Achievement unlocked!
            </h2>
            <div className="mt-5 w-full space-y-2 text-left">
              {result.newly_unlocked_achievements.map((achievement) => (
                <div
                  key={achievement.code}
                  className="rounded-2xl border-2 border-[var(--color-beetle,#ce82ff)] bg-[var(--color-surface)] p-4"
                >
                  <p className="font-black text-[var(--color-text)]">
                    {achievement.icon} {achievement.name}
                  </p>
                  <p className="mt-1 text-sm font-extrabold text-[var(--color-text-muted)]">
                    {achievement.description}
                  </p>
                </div>
              ))}
            </div>
          </>
        )}

        {result.goal_just_met && stage === maxStage && (
          <p className="mt-5 font-black text-[var(--color-orange-text)]">
            🎯 Daily goal reached!
          </p>
        )}

        {result.skill_just_completed && stage === maxStage && (
          <p className="mt-2 font-black text-[var(--color-green-text)]">
            👑 Skill completed — crowns earned!
          </p>
        )}

        {result.next_skill_unlocked && stage === maxStage && (
          <p className="mt-2 text-sm font-extrabold text-[var(--color-text-muted)]">
            🔓 {result.next_skill_unlocked.title} is now unlocked.
          </p>
        )}

        <Button3D
          tone="green"
          fullWidth
          onClick={onContinue}
          className="mt-8"
        >
          {stage < maxStage ? "Continue" : "Continue learning"}
        </Button3D>
      </div>
    </div>
  );
}
