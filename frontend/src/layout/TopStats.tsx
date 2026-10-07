import { useLearner } from "~/store/useLearner";

/** Flag · streak · gems · hearts — the Duolingo stats row. */
export function TopStats() {
  const me = useLearner((s) => s.me);

  return (
    <div className="flex items-center justify-between gap-3 text-lg font-extrabold">
      <span className="text-2xl" title={me?.current_course?.name}>
        {me?.current_course?.flag_emoji ?? "🌍"}
      </span>
      <span className="flex items-center gap-1.5 text-fox" title="Day streak">
        🔥 {me?.current_streak ?? "–"}
      </span>
      <span className="flex items-center gap-1.5 text-macaw" title="Gems">
        💎 {me?.gems ?? "–"}
      </span>
      <span className="flex items-center gap-1.5 text-cardinal" title="Hearts">
        ❤️ {me?.hearts ?? "–"}
      </span>
    </div>
  );
}