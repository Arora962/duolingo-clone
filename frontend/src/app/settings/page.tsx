"use client";

import RailLayout from "@/components/layout/RailLayout";
import RightRail from "@/components/rail/RightRail";
import DuoButton from "@/components/shared/DuoButton";
import { useTheme } from "@/components/shared/ThemeProvider";
import { useToast } from "@/components/shared/ToastProvider";

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme();
  const { showUnimplemented } = useToast();

  const isDark = theme === "dark";

  const settings = [
    ["Sound effects", "Coming soon"],
    ["Daily reminders", "Coming soon"],
    ["Daily XP goal", "Available in Quests"],
  ];

  return (
    <RailLayout rail={<RightRail />}>
      <div className="mx-auto max-w-2xl pt-6">
        <div className="mb-6">
          <p className="text-xs font-extrabold uppercase tracking-[1px] text-duo-muted">
            Account
          </p>

          <h1 className="mt-1 text-3xl font-extrabold">
            Settings
          </h1>

          <p className="mt-2 text-sm text-duo-muted">
            Personalize your Duolingo experience.
          </p>
        </div>

        <div className="space-y-3">
          {/* Dark mode */}
          <div className="flex w-full items-center justify-between rounded-2xl border-2 border-duo-border bg-duo-card p-5">
            <div>
              <p className="font-extrabold text-duo-text">
                Dark mode
              </p>

              <p className="mt-1 text-sm font-bold text-duo-muted">
                {isDark
                  ? "Dark colors are enabled"
                  : "Light colors are enabled"}
              </p>
            </div>

            <button
              type="button"
              role="switch"
              aria-checked={isDark}
              aria-label="Toggle dark mode"
              onClick={toggleTheme}
              className={[
                "relative h-8 w-14 shrink-0 rounded-full border-2 transition-colors",
                isDark
                  ? "border-duo-green bg-duo-green"
                  : "border-duo-border bg-duo-cardHover",
              ].join(" ")}
            >
              <span
                className={[
                  "absolute top-1 h-5 w-5 rounded-full bg-white shadow-sm transition-transform",
                  isDark
                    ? "translate-x-6"
                    : "translate-x-1",
                ].join(" ")}
              />
            </button>
          </div>

          {settings.map(([label, value]) => (
            <button
              key={label}
              type="button"
              onClick={() => showUnimplemented(label)}
              className="flex w-full items-center justify-between rounded-2xl border-2 border-duo-border bg-duo-card p-5 text-left transition-colors hover:bg-duo-cardHover"
            >
              <span className="font-extrabold text-duo-text">
                {label}
              </span>

              <span className="text-sm font-bold text-duo-muted">
                {value}
              </span>
            </button>
          ))}
        </div>

        <div className="mt-6 rounded-2xl border-2 border-duo-border p-5">
          <h2 className="text-lg font-extrabold text-duo-text">
            About this demo
          </h2>

          <p className="mt-2 text-sm leading-6 text-duo-muted">
            This project is a seeded Duolingo-style learning
            experience. Real purchases, social features, speech
            recognition and account management are intentionally
            outside the demo scope.
          </p>

          <DuoButton
            className="mt-4"
            variant="outline"
            onClick={() =>
              showUnimplemented("Account management")
            }
          >
            Account management
          </DuoButton>
        </div>
      </div>
    </RailLayout>
  );
}