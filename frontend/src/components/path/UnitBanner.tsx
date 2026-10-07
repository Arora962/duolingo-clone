import type { UnitNode } from "~/lib/types";
import { useState } from "react";
import { OwlMascot } from "~/components/mascot/OwlMascot";
import { ComingSoonModal } from "~/components/layout/ComingSoonModal";
import { unitTheme } from "~/lib/unitTheme";

export function UnitBanner({ unit }: { unit: UnitNode }) {
  const [guideOpen, setGuideOpen] = useState(false);
  const theme = unitTheme(unit.color_bg, unit.color_border);

  return (
    <>
      <div
        className="sticky top-20 z-10 xl:top-4 flex min-h-[92px] items-center justify-between overflow-visible rounded-2xl px-5 py-4 text-white shadow-[0_4px_0_rgba(0,0,0,0.18)]"
        style={{ backgroundColor: theme.border }}
      >
        <div>
          <p className="text-sm font-extrabold uppercase tracking-wider opacity-80">
            Unit {unit.position}
          </p>
          <h2 className="text-2xl font-extrabold leading-tight">{unit.title}</h2>
          <p className="mt-1 max-w-[470px] text-sm font-bold text-white/90">
            {unit.description}
          </p>
        </div>

        <div className="hidden items-end gap-3 sm:flex">
          <OwlMascot size={82} className="-mb-5" />
          <button
            type="button"
            aria-label="Open guidebook"
            onClick={() => setGuideOpen(true)}
            className="rounded-xl border-2 border-white/30 bg-white/10 px-3 py-2 text-2xl shadow-[0_3px_0_rgba(0,0,0,0.18)]"
          >
            📖
          </button>
        </div>
      </div>

      <ComingSoonModal
        open={guideOpen}
        title="Guidebook"
        description="Unit guidebook content is coming soon."
        onClose={() => setGuideOpen(false)}
      />
    </>
  );
}
