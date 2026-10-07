import type { ButtonHTMLAttributes, ReactNode } from "react";

export type Button3DTone = "green" | "blue" | "red" | "gold" | "neutral";

type Button3DProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  children: ReactNode;
  tone?: Button3DTone;
  fullWidth?: boolean;
};

const toneClass: Record<Button3DTone, string> = {
  green: "duo-button-green",
  blue: "duo-button-blue",
  red: "duo-button-red",
  gold: "duo-button-gold",
  neutral: "duo-button-neutral",
};

export function Button3D({
  children,
  tone = "green",
  fullWidth = false,
  className = "",
  type = "button",
  ...props
}: Button3DProps) {
  return (
    <button
      {...props}
      type={type}
      className={[
        "duo-button",
        toneClass[tone],
        fullWidth ? "w-full" : "",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
    >
      {children}
    </button>
  );
}