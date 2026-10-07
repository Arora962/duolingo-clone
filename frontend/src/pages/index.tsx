import { useEffect } from "react";
import type { NextPage } from "next";
import { useLearner } from "~/store/useLearner";

// Temporary smoke-test page: proves the API client, types and store work.
const Home: NextPage = () => {
  const { me, error, refresh } = useLearner();

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-extrabold text-feather">duolingo</h1>
      {error && <p className="text-cardinal">Error: {error}</p>}
      {!me && !error && <p>Loading...</p>}
      {me && (
        <p className="text-lg">
          Hi {me.display_name}! 🔥 {me.current_streak} · ⚡ {me.total_xp} XP · ❤️{" "}
          {me.hearts} · 💎 {me.gems}
        </p>
      )}
      <button className="rounded-2xl bg-feather px-8 py-3 font-extrabold uppercase tracking-wide text-white shadow-btn-green active:translate-y-1 active:shadow-none">
        Continue
      </button>
    </main>
  );
};

export default Home;