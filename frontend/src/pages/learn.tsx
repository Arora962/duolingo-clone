import { useCallback, useEffect, useState } from "react";
import type { NextPage } from "next";
import { useRouter } from "next/router";
import { AppShell } from "~/components/layout/AppShell";
import { SkillButton, type SkillAction } from "~/components/path/SkillButton";
import { UnitBanner } from "~/components/path/UnitBanner";
import { api, ApiError } from "~/lib/api";
import type { PathResponse } from "~/lib/types";
import { useLearner } from "~/store/useLearner";

// Horizontal wiggle of the nodes inside a unit (the Duolingo zig-zag).
const OFFSETS = [0, 44, 72, 44, 0, -44, -72, -44];

const Learn: NextPage = () => {
  const router = useRouter();
  const refreshMe = useLearner((s) => s.refresh);
  const [path, setPath] = useState<PathResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openId, setOpenId] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

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
    load();
    refreshMe();
  }, [load, refreshMe]);

  // Click anywhere outside a skill to close its popover.
  useEffect(() => {
    const close = () => setOpenId(null);
    window.addEventListener("click", close);
    return () => window.removeEventListener("click", close);
  }, []);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(null), 2500);
  };

  const handleAction = async (action: SkillAction) => {
    if (action.kind === "lesson") {
      router.push(`/lesson/${action.lessonId}`);
      return;
    }
    setBusy(true);
    try {
      const result = await api.claimTreasure(action.skillId);
      showToast(`+${result.gems_awarded} gems! 💎`);
      setOpenId(null);
      await Promise.all([load(), refreshMe()]);
    } catch (e) {
      showToast(e instanceof ApiError ? e.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <AppShell>
      {loading && (
        <div className="flex flex-col gap-6">
          <div className="h-[84px] animate-pulse rounded-2xl bg-swan" />
          <div className="mx-auto h-[70px] w-[70px] animate-pulse rounded-full bg-swan" />
          <div className="mx-auto h-[70px] w-[70px] animate-pulse rounded-full bg-swan" />
        </div>
      )}

      {error && !loading && (
        <div className="rounded-2xl border-2 border-swan p-6 text-center">
          <p className="text-lg font-extrabold text-cardinal">{error}</p>
          <button
            onClick={() => {
              setLoading(true);
              load();
            }}
            className="mt-4 rounded-xl bg-macaw px-6 py-3 text-sm font-extrabold uppercase tracking-wide text-white shadow-btn-blue active:translate-y-1 active:shadow-none"
          >
            Try again
          </button>
        </div>
      )}

      {!loading && !error && !path && (
        <p className="text-center text-lg font-extrabold text-wolf">
          No course selected yet.
        </p>
      )}

      {path?.units.map((unit) => (
        <section key={unit.id} className="mb-10">
          <UnitBanner unit={unit} />
          <div className="mt-6 flex flex-col items-center">
            {unit.skills.map((skill, index) => (
              <SkillButton
                key={skill.id}
                skill={skill}
                offset={OFFSETS[index % OFFSETS.length]}
                open={openId === skill.id}
                busy={busy}
                onToggle={() =>
                  setOpenId((cur) => (cur === skill.id ? null : skill.id))
                }
                onAction={handleAction}
              />
            ))}
          </div>
        </section>
      ))}

      {toast && (
        <div className="fixed bottom-24 left-1/2 z-40 -translate-x-1/2 rounded-2xl bg-eel px-5 py-3 text-base font-extrabold text-white lg:bottom-8">
          {toast}
        </div>
      )}
    </AppShell>
  );
};

export default Learn;