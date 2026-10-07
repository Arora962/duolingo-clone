import { useCallback, useEffect, useState } from "react";
import type { NextPage } from "next";
import { useRouter } from "next/router";
import { AppShell } from "~/components/layout/AppShell";
import { SkillButton, type SkillAction } from "~/components/path/SkillButton";
import { UnitBanner } from "~/components/path/UnitBanner";
import { api, ApiError } from "~/lib/api";
import { nodeLayout } from "~/lib/pathGeometry";
import type { PathResponse } from "~/lib/types";
import { useToast } from "~/store/useToast";

const Learn: NextPage = () => {
  const router = useRouter();
  const pushToast = useToast((state) => state.push);
  const [path, setPath] = useState<PathResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openId, setOpenId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setPath(await api.path());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load your path.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleAction = async (action: SkillAction) => {
    if (action.kind === "lesson") {
      await router.push(`/lesson/${action.lessonId}`);
      return;
    }

    setBusy(true);
    try {
      const result = await api.claimTreasure(action.skillId);
      pushToast(`+${result.gems_awarded} gems! 💎`, "success");
      setOpenId(null);
      await load();
    } catch (e) {
      pushToast(e instanceof ApiError ? e.message : "Something went wrong.", "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AppShell>
      {loading && (
        <div className="flex flex-col gap-6">
          <div className="h-[92px] animate-pulse rounded-2xl bg-[var(--color-border)]" />
          <div className="mx-auto h-[70px] w-[70px] animate-pulse rounded-full bg-[var(--color-border)]" />
          <div className="mx-auto h-[70px] w-[70px] animate-pulse rounded-full bg-[var(--color-border)]" />
        </div>
      )}

      {error && !loading && (
        <div className="rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-6 text-center">
          <p className="text-lg font-extrabold text-[var(--color-red-text)]">{error}</p>
          <button
            type="button"
            onClick={() => {
              setLoading(true);
              void load();
            }}
            className="mt-4 rounded-xl bg-[var(--color-blue-border)] px-6 py-3 text-sm font-extrabold uppercase tracking-wide text-white shadow-btn-blue active:translate-y-1 active:shadow-none"
          >
            Try again
          </button>
        </div>
      )}

      {!loading && !error && !path && (
        <p className="text-center text-lg font-extrabold text-[var(--color-text-muted)]">
          No course selected yet.
        </p>
      )}

      {path?.units.map((unit, unitIndex) => (
        <section key={unit.id} className="mb-10">
          <UnitBanner unit={unit} />
          <div className="mt-2 flex flex-col items-center">
            {unit.skills.map((skill, index) => {
              const layout = nodeLayout(
                index,
                unitIndex,
                skill.is_current,
                index === unit.skills.length - 1,
              );
              return (
                <SkillButton
                  key={skill.id}
                  skill={skill}
                  offset={layout.dx}
                  marginTop={layout.marginTop}
                  marginBottom={layout.marginBottom}
                  open={openId === skill.id}
                  busy={busy}
                  onToggle={() =>
                    setOpenId((current) => (current === skill.id ? null : skill.id))
                  }
                  onAction={handleAction}
                />
              );
            })}
          </div>
        </section>
      ))}
    </AppShell>
  );
};

export default Learn;
