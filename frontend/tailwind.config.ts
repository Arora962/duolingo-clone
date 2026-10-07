import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Duolingo brand palette
        feather: { DEFAULT: "#58cc02", dark: "#58a700" },
        mask: "#89e219",
        macaw: { DEFAULT: "#1cb0f6", dark: "#1899d6" },
        cardinal: { DEFAULT: "#ff4b4b", dark: "#ea2b2b" },
        bee: { DEFAULT: "#ffc800", dark: "#e5b400" },
        fox: { DEFAULT: "#ff9600", dark: "#e08600" },
        beetle: { DEFAULT: "#ce82ff", dark: "#a568cc" },
        eel: "#4b4b4b",
        wolf: "#777777",
        hare: "#afafaf",
        swan: "#e5e5e5",
        polar: "#f7f7f7",
        // Lesson feedback bar
        "correct-bg": "#d7ffb8",
        "wrong-bg": "#ffdfe0",
      },
      boxShadow: {
        // The signature "3D" button edge
        "btn-green": "0 4px 0 #58a700",
        "btn-blue": "0 4px 0 #1899d6",
        "btn-red": "0 4px 0 #ea2b2b",
        "btn-gold": "0 4px 0 #e5b400",
        "btn-swan": "0 4px 0 #e5e5e5",
        "btn-hare": "0 4px 0 #afafaf",
      },
      fontFamily: {
        sans: ["Nunito", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;