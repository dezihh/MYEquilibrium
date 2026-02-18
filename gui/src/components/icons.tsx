import type { ReactNode } from "react";

export type SettingIcon = "image" | "bluetooth" | "code" | "macro" | "invert";

export const settingIcons: Record<SettingIcon, ReactNode> = {
  image: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <rect x="4" y="5" width="16" height="14" rx="2" />
      <circle cx="9" cy="10" r="1.5" />
      <path d="M6 17l4-4 3 3 3-2 2 3" />
    </svg>
  ),
  bluetooth: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 4l4 4-4 4 4 4-4 4V4z" />
      <path d="M8 8l8 8" />
      <path d="M8 16l8-8" />
    </svg>
  ),
  code: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9 8l-4 4 4 4" />
      <path d="M15 8l4 4-4 4" />
    </svg>
  ),
  macro: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M8 7h8M8 12h8M8 17h8" />
      <rect x="4" y="5" width="16" height="14" rx="3" />
    </svg>
  ),
  invert: (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 4v10" />
      <path d="M8 14c0 2.2 1.8 4 4 4s4-1.8 4-4" />
    </svg>
  ),
};
