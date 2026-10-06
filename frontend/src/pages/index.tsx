import { useEffect, useState } from "react";
import type { NextPage } from "next";

type Me = {
  id: number;
  username: string;
  xp: number;
  streak: number;
  hearts: number;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const Home: NextPage = () => {
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/me`)
      .then((res) => {
        if (!res.ok) throw new Error(`Backend returned ${res.status}`);
        return res.json() as Promise<Me>;
      })
      .then(setMe)
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-bold text-[#58cc02]">Duolingo Clone</h1>
      {error && <p className="text-red-500">Error: {error}</p>}
      {!me && !error && <p>Loading...</p>}
      {me && (
        <p className="text-lg">
          Hi {me.username}! 🔥 {me.streak} day streak · ⭐ {me.xp} XP · ❤️{" "}
          {me.hearts} hearts
        </p>
      )}
    </main>
  );
};

export default Home;