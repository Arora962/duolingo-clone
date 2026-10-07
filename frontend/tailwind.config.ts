import type { Config } from "tailwindcss";

// Palette from CLAUDE.md §8 — these exact values are what make the UI read as
// Duolingo rather than "a green quiz app".
const config: Config = {
  content: ["./src/app/**/*.{ts,tsx}", "./src/components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        duo: {
          green: "#58CC02",
          greenDark: "#46A302", // the "3D pressed" shadow under green buttons
          greenSoft: "rgb(var(--duo-green-soft) / <alpha-value>)", // green-tinted panel on the dark background
          blue: "#1CB0F6",
          blueDark: "#1899D6",
          pink: "#FF4B8C",
          pinkDark: "#D63C73",
          red: "#FF4B4B",
          redDark: "#E03131",
          redSoft: "rgb(var(--duo-red-soft) / <alpha-value>)",
          gold: "#FFC800",
          purple: "#CE82FF",
          bg: "rgb(var(--duo-bg) / <alpha-value>)",
          card: "rgb(var(--duo-card) / <alpha-value>)",
          cardHover: "rgb(var(--duo-card-hover) / <alpha-value>)",
          border: "rgb(var(--duo-border) / <alpha-value>)",
          text: "rgb(var(--duo-text) / <alpha-value>)",
          muted: "rgb(var(--duo-muted) / <alpha-value>)",

          // Right-rail tokens, taken from the computed styles of the real
          // /learn page (see rightbar.css in the repo root).
          body: "rgb(var(--duo-body) / <alpha-value>)",
          link: "rgb(var(--duo-link) / <alpha-value>)",
          footer: "rgb(var(--duo-footer) / <alpha-value>)",
          streak: "#FFAB33", // streak count sits in orange, not white
          streakSoft: "#A9661E", // muted amber behind the streak popover's header
          gemText: "#49C0F8",
          heartText: "#EE5555",
          quest: "#FFC700", // quest progress fill
          questOn: "#CD7900", // label colour over the filled portion
          questOff: "#AFAFAF", // label colour over the empty track
          super: "#4C47E8", // Super CTA
          superDark: "#3A35C4",
        },
      },
      fontFamily: {
        // Loaded via next/font in app/layout.tsx.
        sans: ["var(--font-nunito)", "system-ui", "sans-serif"],
      },
      keyframes: {
        "slide-up": {
          from: { transform: "translateY(100%)" },
          to: { transform: "translateY(0)" },
        },
        "pop-in": {
          "0%": { transform: "scale(0.9)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        "float-pill": {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-4px)" },
        },
        // The path characters' idles are NOT here — each figure has its own
        // keyframes, pivot and timing, driven by data in `lib/characters.ts`.
        // They live in globals.css because per-character custom properties
        // don't fit Tailwind's static utility model.
      },
      animation: {
        "slide-up": "slide-up 220ms ease-out",
        "pop-in": "pop-in 200ms ease-out",
        "float-pill": "float-pill 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
