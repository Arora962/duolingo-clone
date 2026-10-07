import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}",
    "./src/hooks/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        feather: {
          DEFAULT: "#58cc02",
          dark: "#58a700",
        },
        macaw: {
          DEFAULT: "#1cb0f6",
          dark: "#1899d6",
        },
        cardinal: {
          DEFAULT: "#ff4b4b",
          dark: "#ea2b2b",
        },
        bee: {
          DEFAULT: "#ffc800",
          dark: "#e5b400",
        },
        fox: "#ff9600",
        beetle: "#ce82ff",
        eel: "#4b4b4b",
        wolf: "#777777",
        hare: "#afafaf",
        swan: "#e5e5e5",
        polar: "#f7f7f7",
        teal: "#00cd9c",
        "correct-bg": "#d7ffb8",
        "wrong-bg": "#ffdfe0",
      },
      fontFamily: {
        sans: ["Nunito", "system-ui", "sans-serif"],
      },
      borderRadius: {
        duo: "12px",
        "duo-lg": "16px",
        "duo-xl": "20px",
      },
      boxShadow: {
        "duo-card": "0 2px 0 var(--color-border)",
        "duo-soft": "0 4px 12px rgba(0, 0, 0, 0.08)",
        "duo-modal": "0 12px 40px rgba(0, 0, 0, 0.18)",
      },
      transitionTimingFunction: {
        bounce: "cubic-bezier(0.2, 0.8, 0.2, 1.15)",
      },
      keyframes: {
        "duo-pop": {
          "0%": {
            opacity: "0",
            transform: "scale(0.92)",
          },
          "100%": {
            opacity: "1",
            transform: "scale(1)",
          },
        },
        "duo-slide-up": {
          "0%": {
            opacity: "0",
            transform: "translateY(24px)",
          },
          "100%": {
            opacity: "1",
            transform: "translateY(0)",
          },
        },
        "duo-bounce": {
          "0%, 100%": {
            transform: "translateY(0)",
          },
          "50%": {
            transform: "translateY(-7px)",
          },
        },
        "duo-shake": {
          "0%, 100%": {
            transform: "translateX(0)",
          },
          "20%": {
            transform: "translateX(-6px)",
          },
          "40%": {
            transform: "translateX(6px)",
          },
          "60%": {
            transform: "translateX(-4px)",
          },
          "80%": {
            transform: "translateX(4px)",
          },
        },
        "duo-pulse-soft": {
          "0%, 100%": {
            opacity: "1",
          },
          "50%": {
            opacity: "0.65",
          },
        },
        "duo-confetti": {
          "0%": {
            transform: "translateY(-10px) rotate(0deg)",
            opacity: "1",
          },
          "100%": {
            transform: "translateY(80vh) rotate(540deg)",
            opacity: "0",
          },
        },
      },
      animation: {
        "duo-pop": "duo-pop 180ms cubic-bezier(0.2, 0.8, 0.2, 1.15)",
        "duo-slide-up": "duo-slide-up 220ms cubic-bezier(0.2, 0.8, 0.2, 1.05)",
        "duo-bounce": "duo-bounce 900ms ease-in-out infinite",
        "duo-shake": "duo-shake 360ms ease-in-out",
        "duo-pulse-soft": "duo-pulse-soft 1.4s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;