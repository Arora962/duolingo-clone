const WHITE = "brightness(0) invert(1)";
const GRAY = "brightness(0) invert(0.7)";

/** White (or grey, when locked) icon drawn inside a skill circle. */
export function SkillGlyph({
  type,
  color,
  size = 34,
}: {
  type: string;
  color: string;
  size?: number;
}) {
  const svg = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    style: { color },
  };

  switch (type) {
    case "BOOK":
      return (
        <svg
          {...svg}
          fill="none"
          stroke="currentColor"
          strokeWidth={2.4}
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
        </svg>
      );
    case "FAST_FORWARD":
      return (
        <svg
          {...svg}
          fill="currentColor"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinejoin="round"
        >
          <polygon points="13 19 22 12 13 5 13 19" />
          <polygon points="2 19 11 12 2 5 2 19" />
        </svg>
      );
    case "DUMBBELL":
    case "TROPHY":
      return (
        <span
          style={{
            fontSize: size,
            lineHeight: 1,
            filter: color === "#ffffff" ? WHITE : GRAY,
          }}
        >
          {type === "TROPHY" ? "🏆" : "🏋️"}
        </span>
      );
    default:
      return (
        <svg
          {...svg}
          fill="currentColor"
          stroke="currentColor"
          strokeWidth={2}
          strokeLinejoin="round"
        >
          <path d="M12 2.5l2.94 6.1 6.56.85-4.8 4.62 1.2 6.63L12 17.45 6.1 20.7l1.2-6.63L2.5 9.45l6.56-.85z" />
        </svg>
      );
  }
}