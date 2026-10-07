import Link from "next/link";
import { useRouter } from "next/router";
import { useState } from "react";
import { Icon, type IconName } from "~/components/ui/Icons";
import { ComingSoonModal } from "~/components/layout/ComingSoonModal";

type BottomItem = {
  label: string;
  icon: IconName;
  href?: string;
  comingSoon?: boolean;
};

const ITEMS: BottomItem[] = [
  { href: "/learn", label: "Learn", icon: "home" },
  { href: "/leaderboard", label: "Leagues", icon: "trophy" },
  { label: "Quests", icon: "sparkle", comingSoon: true },
  { href: "/profile", label: "Profile", icon: "profile" },
  { href: "/settings", label: "Settings", icon: "settings" },
];

export function BottomNav() {
  const router = useRouter();
  const [comingSoon, setComingSoon] = useState<string | null>(null);
  const active = (href: string) =>
    router.pathname === href ||
    (href !== "/learn" && router.pathname.startsWith(`${href}/`));

  return (
    <>
      <nav aria-label="Mobile navigation" className="fixed inset-x-0 bottom-0 z-40 border-t-2 border-[var(--color-border)] bg-[var(--color-surface)] px-2 pb-[max(8px,env(safe-area-inset-bottom))] pt-2 lg:hidden">
        <div className="mx-auto flex max-w-[600px] items-center justify-around">
          {ITEMS.map((item) => {
            if (item.comingSoon || !item.href) {
              return (
                <button
                  key={item.label}
                  type="button"
                  onClick={() => setComingSoon(item.label)}
                  className="flex min-w-14 flex-col items-center gap-1 rounded-xl px-2 py-1.5 text-[var(--color-text-subtle)]"
                >
                  <Icon name={item.icon} size={23} />
                  <span className="text-[10px] font-black uppercase tracking-wide">{item.label}</span>
                </button>
              );
            }

            return (
              <Link
                key={item.href}
                href={item.href}
                className={[
                  "flex min-w-14 flex-col items-center gap-1 rounded-xl border-2 px-2 py-1.5 transition",
                  active(item.href)
                    ? "border-macaw bg-[#ddf4ff] text-macaw dark:bg-[#143b4e]"
                    : "border-transparent text-[var(--color-text-subtle)]",
                ].join(" ")}
              >
                <Icon name={item.icon} size={23} />
                <span className="text-[10px] font-black uppercase tracking-wide">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>

      <ComingSoonModal
        open={comingSoon !== null}
        title={`${comingSoon ?? "Feature"} coming soon`}
        description="This mobile navigation destination is reserved for a later feature."
        onClose={() => setComingSoon(null)}
      />
    </>
  );
}
