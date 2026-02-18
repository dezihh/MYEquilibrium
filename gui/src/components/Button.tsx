import type { ButtonHTMLAttributes } from "react";
import { cx } from "../utils/cx";

export type ButtonVariant =
  | "primary"
  | "outline"
  | "ghost"
  | "danger"
  | "text"
  | "icon";
export type ButtonTone = "default" | "danger";

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  tone?: ButtonTone;
};

export const Button = ({
  variant = "primary",
  tone = "default",
  className,
  ...props
}: ButtonProps) => (
  <button
    className={cx(
      "button",
      `button--${variant}`,
      tone === "danger" && "button--tone-danger",
      className
    )}
    {...props}
  />
);

export const IconButton = (props: ButtonHTMLAttributes<HTMLButtonElement>) => (
  <Button variant="icon" {...props} />
);
