import Link from "next/link";
import { useRouter } from "next/router";
import type { ReactNode } from "react";
import { RightRail } from "~/layout/RightRail";
import { TopStats } from "~/layout/TopStats";

const NAV = [
  { href: "/learn", label: "Learn", icon: "🏠" },
  { href: "/leaderboard", label: "Leaderboards", icon: "🛡️" },
  { href: "/profile", label: "Profile", icon: "👤" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
];

export function AppShell({ children }: { children: ReactNode }) {
  const { pathname } = useRouter();
  const active = (href: string) => pathname === href;

  return (
    <div className="min-h-screen bg-white">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 hidden w-[256px] flex-col border-r-2 border-swan px-4 py-6 lg:flex">
        <Link
          href="/learn"
          className="mb-6 px-3 text-[32px] font-black tracking-tight text-feather"
        >
          duolingo
        </Link>
        <nav className="flex flex-col gap-1.5">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-4 rounded-xl border-2 px-3 py-2.5 text-[15px] font-extrabold uppercase tracking-wider ${
                active(item.href)
                  ? "border-macaw bg-[#ddf4ff] text-macaw"
                  : "border-transparent text-wolf hover:bg-polar"
              }`}
            >
              <span className="w-8 text-center text-2xl">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Mobile / tablet top stats bar (desktop shows them in the right rail) */}
      <header className="fixed inset-x-0 top-0 z-30 flex h-14 items-center border-b-2 border-swan bg-white px-5 xl:hidden">
        <div className="mx-auto w-full max-w-[600px]">
          <TopStats />
        </div>
      </header>

      <div className="lg:pl-[256px]">
        <div className="mx-auto flex max-w-[1056px] justify-center gap-12 px-4">
          <main className="w-full max-w-[600px] pb-28 pt-20 lg:pb-12 xl:pt-6">
            {children}
          </main>
          <aside className="sticky top-6 hidden h-fit w-[368px] shrink-0 self-start pt-6 xl:block">
            <RightRail />
          </aside>
        </div>
      </div>

      {/* Mobile bottom nav */}
      <nav className="fixed inset-x-0 bottom-0 z-30 flex justify-around border-t-2 border-swan bg-white py-2 lg:hidden">
        {NAV.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            aria-label={item.label}
            className={`rounded-xl border-2 px-4 py-1.5 text-2xl ${
              active(item.href)
                ? "border-macaw bg-[#ddf4ff]"
                : "border-transparent"
            }`}
          >
            {item.icon}
          </Link>
        ))}
      </nav>
    </div>
  );
}