import { useRouter } from "next/router";
import type { ReactNode } from "react";
import { BottomNav } from "~/components/layout/BottomNav";
import { RightRail } from "~/components/layout/RightRail";
import { Sidebar } from "~/components/layout/Sidebar";
import { TopStats } from "~/components/layout/TopStats";

type AppShellProps = { children: ReactNode };

export function AppShell({ children }: AppShellProps) {
  const router = useRouter();
  const isLessonRoute = router.pathname.startsWith("/lesson/");

  if (isLessonRoute) return <>{children}</>;

  return (
    <div className="min-h-screen bg-[var(--color-background)] text-[var(--color-text)]">
      <Sidebar />
      <header className="fixed inset-x-0 top-0 z-30 border-b-2 border-[var(--color-border)] bg-[var(--color-background)] lg:left-[256px] xl:hidden">
        <div className="mx-auto flex h-16 w-full max-w-[720px] items-center px-4">
          <TopStats compact />
        </div>
      </header>
      <div className="lg:pl-[256px]">
        <div className="mx-auto flex max-w-[1110px] justify-center gap-12 px-4 sm:px-6">
          <main className="w-full max-w-[600px] pb-28 pt-20 lg:pb-12 xl:pt-10">
            {children}
          </main>
          <aside className="sticky top-6 hidden h-fit w-[368px] shrink-0 self-start xl:block">
            <RightRail />
          </aside>
        </div>
      </div>
      <BottomNav />
    </div>
  );
}
