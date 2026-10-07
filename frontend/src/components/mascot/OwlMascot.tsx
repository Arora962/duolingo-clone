import type { SVGProps } from "react";

type OwlMascotProps = SVGProps<SVGSVGElement> & {
  size?: number;
  mood?: "happy" | "thinking" | "sad";
};

export function OwlMascot({
  size = 180,
  mood = "happy",
  className = "",
  ...props
}: OwlMascotProps) {
  const eyeY = mood === "sad" ? 80 : 75;

  return (
    <svg
      {...props}
      width={size}
      height={size}
      viewBox="0 0 180 180"
      role="img"
      aria-label="Friendly green owl"
      className={className}
    >
      <ellipse
        cx="90"
        cy="157"
        rx="48"
        ry="10"
        fill="currentColor"
        opacity="0.12"
      />

      <path
        d="M46 61 35 42l24 8c8-8 19-12 31-12s23 4 31 12l24-8-11 19c8 11 12 23 12 38 0 33-24 56-56 56s-56-23-56-56c0-15 4-27 12-38Z"
        fill="#58cc02"
      />

      <path
        d="M47 91c0-25 19-43 43-43s43 18 43 43v35c0 18-19 29-43 29s-43-11-43-29V91Z"
        fill="#69d914"
      />

      <circle cx="67" cy={eyeY} r="23" fill="#ffffff" />
      <circle cx="113" cy={eyeY} r="23" fill="#ffffff" />

      <circle cx="68" cy={eyeY + 1} r="9" fill="#4b4b4b" />
      <circle cx="112" cy={eyeY + 1} r="9" fill="#4b4b4b" />

      <circle cx="71" cy={eyeY - 2} r="3" fill="#ffffff" />
      <circle cx="115" cy={eyeY - 2} r="3" fill="#ffffff" />

      <path d="m82 91 8-8 8 8-8 10-8-10Z" fill="#ff9600" />

      {mood === "happy" && (
        <path
          d="M73 111c5 9 11 13 17 13s12-4 17-13"
          fill="none"
          stroke="#4b4b4b"
          strokeWidth="4"
          strokeLinecap="round"
        />
      )}

      {mood === "thinking" && (
        <>
          <circle cx="82" cy="116" r="2.5" fill="#4b4b4b" />
          <circle cx="90" cy="119" r="2.5" fill="#4b4b4b" />
          <circle cx="99" cy="116" r="2.5" fill="#4b4b4b" />
        </>
      )}

      {mood === "sad" && (
        <path
          d="M76 122c5-6 10-8 14-8s9 2 14 8"
          fill="none"
          stroke="#4b4b4b"
          strokeWidth="4"
          strokeLinecap="round"
        />
      )}

      <path
        d="M49 116c-9 5-16 14-18 25 12 0 23-6 29-16"
        fill="#4b4b4b"
        opacity="0.18"
      />

      <path
        d="M131 116c9 5 16 14 18 25-12 0-23-6-29-16"
        fill="#4b4b4b"
        opacity="0.18"
      />

      <path
        d="M67 148c4 8 12 13 23 13s19-5 23-13"
        fill="none"
        stroke="#58a700"
        strokeWidth="5"
        strokeLinecap="round"
      />
    </svg>
  );
}