import type {
  ButtonHTMLAttributes,
  HTMLAttributes,
  ReactNode,
} from "react";
import { cx } from "../utils/cx";

export const MenuAnchor = ({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) => (
  <div className={cx("menu-anchor", className)} {...props} />
);

export const Menu = ({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) => <div className={cx("menu", className)}>{children}</div>;

export type MenuItemProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  tone?: "default" | "danger";
};

export const MenuItem = ({
  tone = "default",
  className,
  ...props
}: MenuItemProps) => (
  <button
    className={cx("menu__item", tone === "danger" && "menu__item--danger", className)}
    {...props}
  />
);
