import type { UnitNode } from "~/lib/types";

export function UnitBanner({ unit }: { unit: UnitNode }) {
  return (
    <div
      className="sticky top-[64px] z-10 flex items-center justify-between rounded-2xl px-5 py-4 text-white xl:top-4"
      style={{
        backgroundColor: unit.color_border,
        boxShadow: "0 4px 0 rgba(0,0,0,0.2)",
      }}
    >
      <div>
        <p className="text-sm font-extrabold uppercase tracking-wider opacity-80">
          Section 1, Unit {unit.position}
        </p>
        <h2 className="text-2xl font-extrabold leading-tight">
          {unit.description || unit.title}
        </h2>
      </div>
      <button
        type="button"
        aria-label="Guidebook"
        className="rounded-xl border-2 border-white/30 px-3 py-2 text-xl"
        style={{ boxShadow: "0 3px 0 rgba(0,0,0,0.2)" }}
      >
        📖
      </button>
    </div>
  );
}