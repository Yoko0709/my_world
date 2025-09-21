// src/types/social.ts
export type IconKey =
  | "github"
  | "researchgate"
  | "mail"
  | "outlook"
  | "linkedin"
  | "instagram"
  | "scholar";

export interface LinkItem { href: string; label: string; icon?: IconKey; ariaLabel?: string; }
export interface Props {
  links: LinkItem[];
  align?: "start" | "center" | "end";
  size?: number;
  gap?: number;
  color?: string;
  hoverColor?: string;
}