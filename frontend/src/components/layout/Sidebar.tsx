import Link from "next/link";
import { useRouter } from "next/router";
import { useState } from "react";
import { Icon, type IconName } from "~/components/ui/Icons";
import { ComingSoonModal } from "~/components/layout/ComingSoonModal";

type SidebarItem =
  | { href: string; label: string; icon: IconName; comingSoon?: false }
  | { href?: undefined; label: string; icon: IconName; comingSoon: true };

const NAV_ITEMS: SidebarItem[] = [
  { href: "/learn", label: "Learn", icon: "home" },
  { href: "/leaderboard", label: "Leaderboards", icon: "trophy" },
  { label: "Quests", icon: "sparkle", comingSoon: true },
  { label: "Shop", icon: "gem", comingSoon: true },
  { href: "/profile", label: "Profile", icon: "profile" },
  { href: "/settings", label: "Settings", icon: "settings" },
  { label: "More", icon: "chevron-down", comingSoon: true },
];

export function Sidebar() {
  const router = useRouter();
  const [comingSoon, setComingSoon] = useState<string | null>(null);

  const isActive = (href: string) =>
    router.pathname === href ||
    (href !== "/learn" && router.pathname.startsWith(`${href}/`));

  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[256px] border-r-2 border-[var(--color-border)] bg-[var(--color-background)] px-4 py-5 lg:flex lg:flex-col">
        <Link href="/learn" className="mb-7 flex items-center gap-2 px-3" aria-label="Go to Learn">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-feather text-xl text-white shadow-[0_3px_0_#58a700]">
            D
          </span>
          <span className="text-[27px] font-black tracking-tight text-feather">learn</span>
        </Link>

        <nav aria-label="Primary navigation" className="flex flex-col gap-1.5">
          {NAV_ITEMS.map((item) => {
            if (item.comingSoon || !item.href) {
              return (
                <button
                  key={item.label}
                  type="button"
                  onClick={() => setComingSoon(item.label)}
                  className="group flex h-[52px] w-full items-center gap-3 rounded-xl border-2 border-transparent px-3 text-left text-[15px] font-black uppercase tracking-[0.8px] text-[var(--color-text-muted)] transition hover:bg-[var(--color-surface-raised)]"
                >
                  <span className="flex h-8 w-8 shrink-0 items-center justify-center">
                    <Icon name={item.icon} size={25} />
                  </span>
                  <span>{item.label}</span>
                </button>
              );
            }

            return (
              <Link
                key={item.href}
                href={item.href}
                className={[
                  "flex h-[52px] items-center gap-3 rounded-xl border-2 px-3 text-[15px] font-black uppercase tracking-[0.8px] transition",
                  isActive(item.href)
                    ? "border-macaw bg-[#ddf4ff] text-macaw dark:bg-[#143b4e]"
                    : "border-transparent text-[var(--color-text-muted)] hover:bg-[var(--color-surface-raised)]",
                ].join(" ")}
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center">
                  <Icon name={item.icon} size={25} />
                </span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="mt-auto rounded-2xl border-2 border-[var(--color-border)] bg-[var(--color-surface-raised)] p-4">
          <p className="text-xs font-black uppercase tracking-wider text-[var(--color-text-muted)]">Learning tip</p>
          <p className="mt-1 text-sm leading-5 text-[var(--color-text)]">A little practice every day goes a long way.</p>
        </div>
      </aside>

      <ComingSoonModal
        open={comingSoon !== null}
        title={`${comingSoon ?? "Feature"} coming soon`}
        description="This area is intentionally reserved for a later feature in the assignment."
        onClose={() => setComingSoon(null)}
      />
    </>
  );
}
