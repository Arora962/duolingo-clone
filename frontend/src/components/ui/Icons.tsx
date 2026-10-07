import type { SVGProps } from "react";

export type IconName =
  | "book"
  | "trophy"
  | "gem"
  | "heart"
  | "flame"
  | "settings"
  | "profile"
  | "home"
  | "lock"
  | "check"
  | "close"
  | "volume"
  | "volume-off"
  | "chest"
  | "dumbbell"
  | "star"
  | "fast-forward"
  | "question"
  | "chevron-down"
  | "chevron-right"
  | "sparkle"
  | "sun"
  | "moon";

type IconProps = SVGProps<SVGSVGElement> & {
  name: IconName;
  size?: number;
};

function paths(name: IconName): React.ReactNode {
  switch (name) {
    case "book":
      return (
        <>
          <path d="M5 5.5A2.5 2.5 0 0 1 7.5 3H20v17H7.5A2.5 2.5 0 0 0 5 22V5.5Z" />
          <path d="M5 5.5V22" />
          <path d="M9 7h7" />
          <path d="M9 11h6" />
        </>
      );

    case "trophy":
      return (
        <>
          <path d="M8 4h8v5a4 4 0 0 1-8 0V4Z" />
          <path d="M8 6H4v2a4 4 0 0 0 4 4" />
          <path d="M16 6h4v2a4 4 0 0 1-4 4" />
          <path d="M12 13v4" />
          <path d="M8 21h8" />
          <path d="M9 17h6" />
        </>
      );

    case "gem":
      return (
        <>
          <path d="m5 8 4-4h6l4 4-7 12L5 8Z" />
          <path d="M5 8h14" />
          <path d="m9 4 3 4 3-4" />
          <path d="m9 8 3 12 3-12" />
        </>
      );

    case "heart":
      return (
        <path d="M12 21S4 15.7 4 9.4A4.4 4.4 0 0 1 12 7a4.4 4.4 0 0 1 8 2.4C20 15.7 12 21 12 21Z" />
      );

    case "flame":
      return (
        <path d="M13.5 3c.4 3.2-1.1 4.9-2.7 6.3C9.7 7.5 8.4 6.7 8 5.1 5.7 7.2 4 10.1 4 13.2A8 8 0 0 0 12 21a8 8 0 0 0 8-8c0-4.1-2.5-7.3-6.5-10ZM12 18a3.2 3.2 0 0 1-3.2-3.2c0-1.1.6-2.2 1.6-3.1.4 1 .9 1.5 1.8 2.1.8-.8 1.3-1.6 1.2-2.7 1.1 1.1 1.8 2.4 1.8 3.7A3.2 3.2 0 0 1 12 18Z" />
      );

    case "settings":
      return (
        <>
          <circle cx="12" cy="12" r="3" />
          <path d="m19 12 2-1-1-3-2 .2a7.7 7.7 0 0 0-1.3-1.3L17 5l-3-1-1 2a7.7 7.7 0 0 0-2 0L10 4 7 5l.3 2.1A7.7 7.7 0 0 0 6 8.4L4 8l-1 3 2 1a7.7 7.7 0 0 0 0 2l-2 1 1 3 2-.3a7.7 7.7 0 0 0 1.3 1.3L7 20l3 1 1-2a7.7 7.7 0 0 0 2 0l1 2 3-1-.3-2.1a7.7 7.7 0 0 0 1.3-1.3L20 17l1-3-2-1a7.7 7.7 0 0 0 0-2Z" />
        </>
      );

    case "profile":
      return (
        <>
          <circle cx="12" cy="8" r="3.5" />
          <path d="M5 21c.7-4 3-6 7-6s6.3 2 7 6" />
        </>
      );

    case "home":
      return (
        <>
          <path d="m4 11 8-7 8 7v9H4v-9Z" />
          <path d="M9 20v-5h6v5" />
        </>
      );

    case "lock":
      return (
        <>
          <rect x="5" y="10" width="14" height="11" rx="2" />
          <path d="M8 10V7a4 4 0 0 1 8 0v3" />
          <path d="M12 14v3" />
        </>
      );

    case "check":
      return <path d="m5 12 4 4L19 7" />;

    case "close":
      return (
        <>
          <path d="m6 6 12 12" />
          <path d="M18 6 6 18" />
        </>
      );

    case "volume":
      return (
        <>
          <path d="M4 10v4h4l5 4V6l-5 4H4Z" />
          <path d="M16 9a4 4 0 0 1 0 6" />
          <path d="M18.5 6.5a8 8 0 0 1 0 11" />
        </>
      );

    case "volume-off":
      return (
        <>
          <path d="m4 10 4 4h1l4 3V7l-4 3H4v0Z" />
          <path d="m17 9 4 6" />
          <path d="m21 9-4 6" />
        </>
      );

    case "chest":
      return (
        <>
          <path d="M4 9h16v10H4V9Z" />
          <path d="M3 9h18l-2-4H5L3 9Z" />
          <path d="M12 9v10" />
          <path d="M10 13h4" />
        </>
      );

    case "dumbbell":
      return (
        <>
          <path d="M7 9v6M17 9v6M4 10v4M20 10v4" />
          <path d="M7 12h10" />
          <path d="M4 12H2M22 12h-2" />
        </>
      );

    case "star":
      return (
        <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z" />
      );

    case "fast-forward":
      return (
        <>
          <path d="m4 5 8 7-8 7V5Z" />
          <path d="m12 5 8 7-8 7V5Z" />
        </>
      );

    case "question":
      return (
        <>
          <circle cx="12" cy="12" r="9" />
          <path d="M9.5 9a2.6 2.6 0 1 1 4.3 2c-1 .8-1.8 1.2-1.8 2.7" />
          <path d="M12 17h.01" />
        </>
      );

    case "chevron-down":
      return <path d="m6 9 6 6 6-6" />;

    case "chevron-right":
      return <path d="m9 6 6 6-6 6" />;

    case "sparkle":
      return (
        <>
          <path d="m12 3 1.4 6.6L20 12l-6.6 1.4L12 20l-1.4-6.6L4 12l6.6-2.4L12 3Z" />
          <path d="m19 3 .5 2.5L22 6l-2.5.5L19 9l-.5-2.5L16 6l2.5-.5L19 3Z" />
        </>
      );

    case "sun":
      return (
        <>
          <circle cx="12" cy="12" r="4" />
          <path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
        </>
      );

    case "moon":
      return <path d="M20 15.5A8.5 8.5 0 0 1 8.5 4a8.6 8.6 0 1 0 11.5 11.5Z" />;
  }
}

export function Icon({
  name,
  size = 24,
  strokeWidth = 2.5,
  className,
  ...props
}: IconProps) {
  return (
    <svg
      {...props}
      className={className}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths(name)}
    </svg>
  );
}